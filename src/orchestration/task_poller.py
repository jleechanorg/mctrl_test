"""Task poller — polls Mission Control for inbox tasks and dispatches to agents.

Polls a Mission Control board for inbox tasks and dispatches each via
``ai_orch run``, which launches the appropriate agent process.

ai_orch handles CLI selection, model choice, and the agent process
lifecycle; the task poller passes task summaries and tracks dispatch status.

When ``async_dispatch`` is enabled, ``ai_orch run --async`` returns before
the agent finishes — dispatched tasks are marked IN_PROGRESS only (not DONE).
When synchronous (default), the subprocess blocks until the agent completes
and tasks transition through IN_PROGRESS → DONE.

All ai_orch parameters (``--agent-cli``, ``--model``, ``--async``,
``--resume``, ``--worktree``) are configurable via dataclass fields
or environment variables.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import logging
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

from orchestration.mc_client import MissionControlClient, TaskStatus

logger = logging.getLogger(__name__)

_TOKEN_USAGE_PATTERNS: dict[str, re.Pattern[str]] = {
    "input_tokens": re.compile(r"(?i)\b(?:input|prompt)\s*tokens?[^0-9]*(\d+)", re.MULTILINE),
    "output_tokens": re.compile(r"(?i)\b(?:output|completion)\s*tokens?[^0-9]*(\d+)", re.MULTILINE),
    "total_tokens": re.compile(r"(?i)\btotal\s*tokens?[^0-9]*(\d+)", re.MULTILINE),
}


def _extract_token_usage(stdout_payload: str | bytes | None) -> dict[str, int]:
    """Extract token usage counters from subprocess stdout."""
    if isinstance(stdout_payload, bytes):
        output = stdout_payload.decode("utf-8", errors="replace")
    elif stdout_payload is None:
        output = ""
    else:
        output = str(stdout_payload)

    output = output.strip()
    if not output:
        return {}

    try:
        parsed = json.loads(output)
        if isinstance(parsed, dict):
            result: dict[str, int] = {}
            for key in ("input_tokens", "output_tokens", "total_tokens"):
                value = parsed.get(key)
                if isinstance(value, int):
                    result[key] = value
            return result
    except json.JSONDecodeError:
        pass

    usage: dict[str, int] = {}
    for usage_field, pattern in _TOKEN_USAGE_PATTERNS.items():
        match = pattern.search(output)
        if match:
            try:
                usage[usage_field] = int(match.group(1))
            except ValueError:
                pass
    return usage



@dataclass
class TaskPoller:
    """Polls Mission Control for inbox tasks and dispatches to agents.

    Attributes:
        board_id: Mission Control board UUID to poll.
        client: MissionControlClient instance for API calls. If None, creates from env.
        poll_interval_seconds: Interval between polls in run_forever mode.
        dispatch_concurrency: Max number of tasks dispatched in parallel.
        dispatch_fn: Optional callable for task dispatch. If None, uses ai_orch.
        agent_cli: Agent CLI to pass via ``--agent-cli``. None = let ai_orch decide.
        model: Model to pass via ``--model``. None = let ai_orch decide.
        async_dispatch: If True, pass ``--async`` and skip DONE transition.
        resume: If True, pass ``--resume`` to ai_orch.
        worktree: If True, pass ``--worktree`` to ai_orch.
    """

    board_id: str
    client: Optional[MissionControlClient] = None
    poll_interval_seconds: int = 60
    dispatch_concurrency: int = 4
    dispatch_fn: Optional[Callable[[str | None, dict], bool | tuple[bool, dict] | dict]] = field(default=None, repr=False)
    agent_cli: str | None = None
    model: str | None = None
    async_dispatch: bool = False
    resume: bool = False
    worktree: bool = False
    _dispatched_count: int = field(default=0, repr=False)

    def __post_init__(self) -> None:
        """Create client from env if not provided; apply env var overrides."""
        if self.client is None:
            self.client = MissionControlClient()

        env_concurrency = os.environ.get("TASK_POLLER_DISPATCH_CONCURRENCY")
        if env_concurrency:
            try:
                self.dispatch_concurrency = int(env_concurrency)
            except ValueError:
                logger.warning(
                    "Invalid TASK_POLLER_DISPATCH_CONCURRENCY=%s; using %s",
                    env_concurrency,
                    self.dispatch_concurrency,
                )

        try:
            self.dispatch_concurrency = int(self.dispatch_concurrency)
        except (TypeError, ValueError):
            logger.warning("Invalid dispatch_concurrency=%s; using 1", self.dispatch_concurrency)
            self.dispatch_concurrency = 1
        self.dispatch_concurrency = max(1, self.dispatch_concurrency)

        # ai_orch param env var overrides
        env_agent_cli = os.environ.get("TASK_POLLER_AGENT_CLI")
        if env_agent_cli:
            self.agent_cli = env_agent_cli

        env_model = os.environ.get("TASK_POLLER_MODEL")
        if env_model:
            self.model = env_model

        for attr, env_key in [
            ("async_dispatch", "TASK_POLLER_ASYNC"),
            ("resume", "TASK_POLLER_RESUME"),
            ("worktree", "TASK_POLLER_WORKTREE"),
        ]:
            env_val = os.environ.get(env_key, "")
            if env_val.strip().lower() in ("1", "true", "yes"):
                setattr(self, attr, True)

    def poll_and_dispatch(self) -> int:
        """Poll for inbox tasks and dispatch each to an agent CLI.

        Returns:
            Number of tasks dispatched in this call.
        """
        if self.client is None or not self.client.is_configured:
            return 0

        tasks = self.client.list_inbox_tasks(self.board_id)
        if not tasks:
            return 0

        dispatchable_tasks: list[dict] = []
        for task in tasks:
            task_id = task.get("id")
            title = task.get("title", "Untitled")
            if not task_id:
                logger.warning(f"Skipping task without id: {task}")
                continue
            if task.get("approval_required") and not task.get("approved_at"):
                logger.info(f"Skipping task pending approval: {task_id} - {title}")
                continue
            dispatchable_tasks.append(task)

        if not dispatchable_tasks:
            return 0

        dispatched = 0
        max_workers = min(self.dispatch_concurrency, len(dispatchable_tasks))
        if max_workers == 1:
            for task in dispatchable_tasks:
                task_id = task.get("id", "<unknown>")
                try:
                    if self._dispatch_task(task):
                        dispatched += 1
                except Exception as e:
                    logger.error(f"Failed to dispatch task {task_id}: {e}")
        else:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_task_id = {
                    executor.submit(self._dispatch_task, task): str(task.get("id", "<unknown>"))
                    for task in dispatchable_tasks
                }
                for future in as_completed(future_to_task_id):
                    task_id = future_to_task_id[future]
                    try:
                        if future.result():
                            dispatched += 1
                    except Exception as e:
                        logger.error(f"Failed to dispatch task {task_id}: {e}")

        self._dispatched_count += dispatched
        return dispatched

    def decompose_task(self, task: dict) -> list[str]:
        """Decompose a task into subtasks and create dependency chains."""
        subtasks = task.get("subtasks")
        if not isinstance(subtasks, list) or not subtasks:
            return []

        if self.client is None or not self.client.is_configured:
            return []

        created_ids: list[str] = []
        previous_task_id: str | None = None

        for subtask in subtasks:
            if not isinstance(subtask, dict):
                continue

            title = str(subtask.get("title", "")).strip() or f"Subtask for {task.get('id')}"
            description = subtask.get("description", "")

            payload = {
                "board_id": task.get("board_id", self.board_id),
                "title": title,
                "description": description,
                "status": "inbox",
            }
            created = self.client.create_task(payload)
            if not isinstance(created, dict):
                continue

            subtask_id = created.get("id")
            if not isinstance(subtask_id, str) or not subtask_id:
                continue

            depends_on = subtask.get("depends_on", [])
            if depends_on is None:
                depends_on = []
            if not isinstance(depends_on, list):
                depends_on = [depends_on]

            explicit_dependencies = [
                str(dep)
                for dep in depends_on
                if isinstance(dep, str) and dep.strip()
            ]

            if previous_task_id is not None and previous_task_id not in explicit_dependencies:
                explicit_dependencies.append(previous_task_id)

            if explicit_dependencies:
                self.client.set_task_dependencies(
                    subtask_id,
                    explicit_dependencies,
                    board_id=self.board_id,
                )

            created_ids.append(subtask_id)
            previous_task_id = subtask_id

        return created_ids

    def _dispatch_task(self, task: dict) -> bool:
        """Dispatch a single task via ai_orch run.

        When ``async_dispatch`` is True, the task is only marked IN_PROGRESS
        (the agent hasn't finished yet). When False (default), the subprocess
        blocks and the task transitions IN_PROGRESS → DONE.

        Args:
            task: Task dict with 'id', 'title', 'description'.

        Returns:
            True if dispatch succeeded, False otherwise.
        """
        task_id = task.get("id")
        title = task.get("title", "Untitled")
        description = task.get("description", "")

        decompose_ids = self.decompose_task(task)
        if decompose_ids:
            logger.info(f"Created {len(decompose_ids)} subtasks for {task_id}")
            try:
                updated_task = self.client.update_task(task_id, TaskStatus.BLOCKED, board_id=self.board_id)
            except Exception as e:
                logger.error(f"Failed to block parent task {task_id}: {e}")
                return False

            if not updated_task:
                logger.error(f"Mission Control rejected blocked update for task {task_id}")
                return False

            return True

        task_summary = f"{title}: {description}" if description else title
        cli_label = self.agent_cli or "ai_orch-default"
        logger.info(f"Dispatching task {task_id} to {cli_label}: {title}")

        dispatched = False
        token_usage: dict[str, int] = {}

        if self.dispatch_fn is not None:
            try:
                dispatch_response = self.dispatch_fn(self.agent_cli, task)
                if isinstance(dispatch_response, tuple) and len(dispatch_response) == 2:
                    dispatched = bool(dispatch_response[0])
                    maybe_usage = dispatch_response[1]
                    if isinstance(maybe_usage, dict):
                        token_usage = maybe_usage
                elif isinstance(dispatch_response, dict):
                    dispatched = bool(dispatch_response.get("success"))
                    maybe_usage = dispatch_response.get("token_usage")
                    if isinstance(maybe_usage, dict):
                        token_usage = maybe_usage
                else:
                    dispatched = bool(dispatch_response)
            except Exception as e:
                logger.error(f"dispatch_fn failed for {task_id}: {e}")
        else:
            dispatched, token_usage = self._dispatch_via_ai_orch(task_summary, task_id)

        if not dispatched:
            return False

        custom_fields = {"cost": token_usage} if token_usage else None
        try:
            in_progress_task = self.client.update_task(
                task_id,
                TaskStatus.IN_PROGRESS,
                custom_fields=custom_fields,
                board_id=self.board_id,
            )
        except Exception as e:
            logger.error(f"Failed to mark task {task_id} as in_progress: {e}")
            return False

        if not in_progress_task:
            logger.error(f"Mission Control rejected in_progress update for task {task_id}")
            return False

        if self.async_dispatch:
            logger.info(f"Async dispatch — task {task_id} stays IN_PROGRESS")
            return True

        try:
            done_task = self.client.update_task(
                task_id,
                TaskStatus.DONE,
                board_id=self.board_id,
            )
        except Exception as e:
            logger.error(f"Failed to mark task {task_id} as done: {e}")
            return False

        if not done_task:
            logger.error(f"Mission Control rejected done update for task {task_id}")
            return False

        return True

    def _dispatch_via_ai_orch(
        self,
        task_summary: str,
        task_id: str,
    ) -> tuple[bool, dict[str, int]]:
        """Dispatch task via ``ai_orch run`` with dynamic param passthrough.

        Builds the ai_orch command from configured fields (``agent_cli``,
        ``model``, ``async_dispatch``, ``resume``, ``worktree``).  Only
        flags with non-default values are included.

        Args:
            task_summary: Task description string.
            task_id: Task ID for logging.

        Returns:
            (True if dispatch succeeded, token usage data).
        """
        cmd: list[str] = ["ai_orch", "run"]
        if self.agent_cli:
            cmd.extend(["--agent-cli", self.agent_cli])
        if self.model:
            cmd.extend(["--model", self.model])
        if self.async_dispatch:
            cmd.append("--async")
        if self.resume:
            cmd.append("--resume")
        if self.worktree:
            cmd.append("--worktree")
        cmd.extend(["--", task_summary])
        logger.info(f"ai_orch run for task {task_id}")

        token_usage: dict[str, int] = {}
        dispatched = False
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=300,
            )
            dispatched = result.returncode == 0
            token_usage = _extract_token_usage(result.stdout)
            if not dispatched:
                logger.error(f"Task dispatch exited {result.returncode} for {task_id}")
        except subprocess.TimeoutExpired:
            logger.error(f"Task dispatch timed out for {task_id}")
        except FileNotFoundError:
            logger.error("ai_orch not found in PATH")
        except Exception as e:
            logger.error(f"Failed to dispatch task {task_id}: {e}")

        return dispatched, token_usage

    def run_once(self) -> int:
        """Run a single poll and dispatch cycle.

        Returns:
            Number of tasks dispatched.
        """
        return self.poll_and_dispatch()

    def run_forever(self) -> None:
        """Run poll and dispatch loop indefinitely.

        Catches and logs exceptions without crashing.
        """
        while True:
            try:
                self.poll_and_dispatch()
            except Exception as e:
                logger.error(f"Poll cycle failed: {e}")
            time.sleep(self.poll_interval_seconds)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Poll Mission Control inbox tasks and dispatch agents")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single poll-and-dispatch cycle and exit",
    )
    parser.add_argument("--agent-cli", default=None, help="Agent CLI to pass to ai_orch (default: let ai_orch decide)")
    parser.add_argument("--model", default=None, help="Model to pass to ai_orch")
    parser.add_argument("--async", dest="async_dispatch", action="store_true", help="Pass --async to ai_orch (skip DONE transition)")
    parser.add_argument("--resume", action="store_true", help="Pass --resume to ai_orch")
    parser.add_argument("--worktree", action="store_true", help="Pass --worktree to ai_orch")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    args = parser.parse_args()
    board_id = os.environ.get("MISSION_CONTROL_BOARD_ID")
    if not board_id:
        print("ERROR: MISSION_CONTROL_BOARD_ID not set")
        exit(1)

    client = MissionControlClient()
    if not client.is_configured:
        print("ERROR: Mission Control not configured (check env vars)")
        exit(1)

    poller = TaskPoller(
        board_id=board_id,
        client=client,
        agent_cli=args.agent_cli,
        model=args.model,
        async_dispatch=args.async_dispatch,
        resume=args.resume,
        worktree=args.worktree,
    )
    print(f"Starting task poller for board {board_id}...")

    if args.once:
        print("Running one poll cycle")
        poller.run_once()
    else:
        poller.run_forever()
