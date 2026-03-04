"""Task poller — polls Mission Control for inbox tasks and dispatches to agents.

Polls a Mission Control board for inbox tasks, detects which CLI to use,
and spawns agents via ai_orch to handle each task.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import logging
import os
import re
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from orchestration.mc_client import MissionControlClient, TaskStatus

logger = logging.getLogger(__name__)

# Default CLI keywords for task type detection
DEFAULT_CLI_KEYWORDS: dict[str, list[str]] = {
    "codex": ["codex", "complex", "refactor", "large"],
    "gemini": ["gemini", "design", "UI", "frontend", "creative"],
    "cursor": ["cursor", "edit", "fix", "small"],
    "claude": [],  # Default fallback
}

PROMPT_LIBRARY_PATH = Path.home() / ".jleechanclaw" / "prompt_library.json"


def _normalize_text(value: object) -> str:
    """Normalize free text into lower-case, whitespace-compact form."""
    return " ".join(str(value or "").lower().split())


def _load_prompt_library(library_path: Path) -> dict:
    """Load prompt library JSON from disk."""
    if not library_path.exists():
        return {}
    try:
        with library_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_prompt_library(library_path: Path, data: dict) -> None:
    """Persist prompt library JSON to disk."""
    library_path.parent.mkdir(parents=True, exist_ok=True)
    with library_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _resolve_library_cli(search_text: str, library: dict) -> str | None:
    """Resolve a CLI override from prompt library entries."""
    patterns = library.get("patterns")
    if not isinstance(patterns, dict):
        return None

    for pattern, value in sorted(
        patterns.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        if not isinstance(pattern, str):
            continue
        if not pattern:
            continue
        if pattern.lower() not in search_text:
            continue

        if isinstance(value, str):
            return value
        if isinstance(value, dict) and isinstance(value.get("cli"), str):
            return value.get("cli")
    return None


def _build_prompt_key(task: dict) -> str:
    """Create a short prompt key for library learning."""
    explicit = task.get("prompt_library_key")
    if explicit:
        return _normalize_text(explicit)

    title = _normalize_text(task.get("title", ""))
    description = _normalize_text(task.get("description", ""))
    text = f"{title} {description}".strip()
    if not text:
        return ""

    words = [w for w in text.split() if len(w) > 2]
    return " ".join(words[:5])


def _update_prompt_library(task: dict, cli: str, library_path: Path) -> None:
    """Persist successful task-to-CLI choice for future prompt detection."""
    key = _build_prompt_key(task)
    if not key:
        return

    library = _load_prompt_library(library_path)
    patterns = library.get("patterns")
    if not isinstance(patterns, dict):
        patterns = {}

    entry = patterns.get(key)
    if isinstance(entry, dict):
        if entry.get("cli") == cli:
            count = entry.get("hits", 0)
            entry["hits"] = (count + 1) if isinstance(count, int) else 1
        else:
            entry["cli"] = cli
            entry["hits"] = 1
    elif isinstance(entry, str):
        patterns[key] = {"cli": entry if entry == cli else cli, "hits": 1}
        if entry == cli:
            patterns[key]["hits"] = 2
    else:
        patterns[key] = {"cli": cli, "hits": 1}

    library["patterns"] = patterns
    _save_prompt_library(library_path, library)


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

    # Common Claude JSON shape:
    # {"input_tokens": 10, "output_tokens": 20, "total_tokens": 30}
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
    for field, pattern in _TOKEN_USAGE_PATTERNS.items():
        match = pattern.search(output)
        if match:
            try:
                usage[field] = int(match.group(1))
            except ValueError:
                pass
    return usage


def detect_cli(
    task: dict,
    agent_cli_map: dict[str, list[str]] | None = None,
    prompt_library_path: Path | None = None,
) -> str:
    """Detect which CLI to use based on task content.

    Examines task title and description for keywords that indicate
    which agent CLI is best suited for the task. Also checks for
    MINIMAX_API_KEY env var to enable minimax/claudem (returns 'claudem'
    meaning: use build_claudem_dispatch).

    Args:
        task: Task dict with 'title' and/or 'description' keys.
        agent_cli_map: Optional custom mapping of keywords to CLI names.
        prompt_library_path: Optional path override for prompt library.

    Returns:
        CLI name string (e.g., 'claude', 'codex', 'gemini', 'cursor', 'claudem').
    """
    # Check for minimax/claudem first if API key is set
    if os.environ.get("MINIMAX_API_KEY"):
        return "claudem"

    cli_map = agent_cli_map or DEFAULT_CLI_KEYWORDS

    # Build searchable text from task
    title = str(task.get("title") or "").lower()
    description = str(task.get("description") or "").lower()
    search_text = f"{title} {description}"

    library = _load_prompt_library(prompt_library_path or PROMPT_LIBRARY_PATH)
    library_choice = _resolve_library_cli(search_text, library)
    if library_choice:
        return library_choice

    # Check for matching keywords in order (specific to general)
    for cli, keywords in cli_map.items():
        if cli == "claude":
            continue  # Claude is default, check last
        for keyword in keywords:
            if keyword.lower() in search_text:
                return cli

    return "claude"  # Default fallback


def build_claudem_dispatch() -> Callable[[str, dict], bool]:
    """Build a dispatch function that uses claudem (minimax) for task execution.

    Returns a callable that:
    - Runs `claude --dangerously-skip-permissions --print` via subprocess
    - Sends `<task_title>: <task_description>` to stdin
    - Uses 300s timeout
    - Captures stdout/stderr to /tmp/ralph/jobs/<task_id>_<timestamp>.log

    Returns:
        Callable that takes (cli: str, task: dict) and returns True on success.
    """
    log_dir = Path("/tmp/ralph/jobs")

    def claudem_dispatch(cli: str, task: dict) -> bool:
        """Dispatch task using claudem (minimax).

        Args:
            cli: CLI name (should be 'claudem' but accepts others for flexibility).
            task: Task dict with 'id', 'title', 'description'.

        Returns:
            True if dispatch succeeded, False otherwise.
        """
        log_dir.mkdir(parents=True, exist_ok=True)
        task_id = task.get("id", "unknown")
        title = task.get("title", "Untitled")
        description = task.get("description", "")
        task_summary = f"{title}: {description}" if description else title

        # Build claudem command using claude binary with minimax env
        # (claudem is a bash function, not a binary, so we call claude directly)
        cmd = ["claude", "--dangerously-skip-permissions", "--print"]

        # Create log file path
        timestamp = int(time.time())
        log_file = log_dir / f"{task_id}_{timestamp}.log"

        logger.info(f"Dispatching to claudem: {title} (log: {log_file})")

        # Build env, removing all Claude Code session vars to allow nested sessions
        env = dict(os.environ)
        for key in list(env):
            if key == "CLAUDECODE" or key.startswith("CLAUDE_CODE_"):
                env.pop(key)
        env.update({
            "ANTHROPIC_BASE_URL": "https://api.minimax.io/anthropic",
            "ANTHROPIC_AUTH_TOKEN": os.environ.get("MINIMAX_API_KEY", ""),
            "ANTHROPIC_MODEL": "MiniMax-M2.5",
            "ANTHROPIC_SMALL_FAST_MODEL": "MiniMax-M2.5",
            "API_TIMEOUT_MS": "3000000",
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
        })

        try:
            result = subprocess.run(
                cmd,
                input=task_summary.encode(),
                capture_output=True,
                timeout=300,  # 5 min timeout
                env=env,
            )

            # Write output to log file
            with open(log_file, "w") as f:
                f.write(f"# Task ID: {task_id}\n")
                f.write(f"# Title: {title}\n")
                f.write(f"# Timestamp: {timestamp}\n")
                f.write(f"# Exit code: {result.returncode}\n")
                f.write(f"# STDOUT:\n{result.stdout.decode('utf-8', errors='replace')}\n")
                f.write(f"# STDERR:\n{result.stderr.decode('utf-8', errors='replace')}\n")

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            logger.error(f"claudem dispatch timed out for {task_id}")
            with open(log_file, "w") as f:
                f.write(f"# Task ID: {task_id}\n# Status: TIMEOUT\n")
            return False
        except FileNotFoundError:
            logger.error("claudem not found in PATH")
            return False
        except Exception as e:
            logger.error(f"claudem dispatch failed for {task_id}: {e}")
            return False

    return claudem_dispatch


@dataclass
class TaskPoller:
    """Polls Mission Control for inbox tasks and dispatches to agents.

    Attributes:
        board_id: Mission Control board UUID to poll.
        client: MissionControlClient instance for API calls. If None, creates from env.
        agent_cli_map: Optional custom mapping of keywords to CLI names.
        poll_interval_seconds: Interval between polls in run_forever mode.
        dispatch_concurrency: Max number of tasks dispatched in parallel.
        dispatch_fn: Optional callable for task dispatch. If None, uses subprocess.
    """

    board_id: str
    client: Optional[MissionControlClient] = None
    agent_cli_map: dict[str, list[str]] = field(default_factory=lambda: dict(DEFAULT_CLI_KEYWORDS))
    prompt_library_path: Path = field(default_factory=lambda: PROMPT_LIBRARY_PATH)
    poll_interval_seconds: int = 60
    dispatch_concurrency: int = 4
    dispatch_fn: Optional[Callable[[str, dict], bool]] = field(default=None, repr=False)
    _dispatched_count: int = field(default=0, repr=False)

    def __post_init__(self) -> None:
        """Create client from env if not provided. Auto-wire claudem dispatch when MINIMAX_API_KEY set."""
        if self.client is None:
            self.client = MissionControlClient()
        # Auto-wire claudem dispatch when MINIMAX_API_KEY is present and no explicit dispatch_fn given.
        # Without this, detect_cli returns "claudem" which ai_orch rejects (only accepts claude/codex/etc).
        if self.dispatch_fn is None and os.environ.get("MINIMAX_API_KEY"):
            self.dispatch_fn = build_claudem_dispatch()

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

    def poll_and_dispatch(self) -> int:
        """Poll for inbox tasks and dispatch each to an agent CLI.

        Returns:
            Number of tasks dispatched in this call.
        """
        # Check if client is configured
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
        """Dispatch a single task to an agent CLI.

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
            except Exception as e:  # pragma: no cover - client-level exceptions
                logger.error(f"Failed to block parent task {task_id}: {e}")
                return False

            if not updated_task:
                logger.error(f"Mission Control rejected blocked update for task {task_id}")
                return False

            return True

        cli = detect_cli(
            task,
            self.agent_cli_map,
            prompt_library_path=self.prompt_library_path,
        )
        task_summary = f"{title}: {description}" if description else title

        logger.info(f"Dispatching task {task_id} to {cli}: {title}")

        dispatched = False
        token_usage: dict[str, int] = {}

        # Use custom dispatch_fn if provided
        if self.dispatch_fn is not None:
            try:
                dispatch_response = self.dispatch_fn(cli, task)
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
            # Default: use subprocess directly (claude/codex/gemini/cursor)
            dispatched, token_usage = self._dispatch_via_subprocess(cli, task_summary, task_id)

        # Only mark in_progress when dispatch succeeded and API update succeeds
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
        except Exception as e:  # pragma: no cover - client-level exceptions
            logger.error(f"Failed to mark task {task_id} as in_progress: {e}")
            return False

        if not in_progress_task:
            logger.error(f"Mission Control rejected in_progress update for task {task_id}")
            return False

        try:
            done_task = self.client.update_task(
                task_id,
                TaskStatus.DONE,
                board_id=self.board_id,
            )
        except Exception as e:  # pragma: no cover - client-level exceptions
            logger.error(f"Failed to mark task {task_id} as done: {e}")
            return False

        if not done_task:
            logger.error(f"Mission Control rejected done update for task {task_id}")
            return False

        _update_prompt_library(task, cli, self.prompt_library_path)
        return True

    def _dispatch_via_subprocess(
        self,
        cli: str,
        task_summary: str,
        task_id: str,
    ) -> tuple[bool, dict[str, int]]:
        """Dispatch task via synchronous subprocess.

        Command patterns:
        - claude:  claude --output-format stream-json --verbose
                   --dangerously-skip-permissions  (prompt via stdin)
        - codex:   codex exec --yolo --skip-git-repo-check  (prompt via stdin)
        - gemini:  gemini -m {model} --yolo  (prompt via stdin; -p is deprecated)
        - cursor:  cursor-agent -f -p @{tmpfile} --model {model} --output-format text

        ai_orch run is intentionally NOT used — it creates a detached tmux
        session and exits 0 immediately before the agent finishes.

        Args:
            cli: CLI name to use (claude, codex, gemini, cursor).
            task_summary: Task description string.
            task_id: Task ID for logging.

        Returns:
            (True if dispatch succeeded, token usage data).
        """
        # Strip Claude Code session vars to allow nested claude invocations.
        env = dict(os.environ)
        for key in list(env):
            if key == "CLAUDECODE" or key.startswith("CLAUDE_CODE_"):
                env.pop(key)

        cmd: list[str]
        stdin_input: bytes | None = None
        prompt_file_path: str | None = None

        if cli == "codex":
            cmd = ["codex", "exec", "--yolo", "--skip-git-repo-check"]
            stdin_input = task_summary.encode()
        elif cli == "gemini":
            model = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")
            cmd = ["gemini", "-m", model, "--yolo"]
            stdin_input = task_summary.encode()
        elif cli == "cursor":
            model = os.environ.get("CURSOR_MODEL", "composer-1")
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
                f.write(task_summary)
                prompt_file_path = f.name
            cmd = ["cursor-agent", "-f", "-p", f"@{prompt_file_path}",
                   "--model", model, "--output-format", "text"]
        else:
            # claude (default)
            cmd = ["claude", "--output-format", "stream-json", "--verbose",
                   "--dangerously-skip-permissions"]
            stdin_input = task_summary.encode()

        token_usage: dict[str, int] = {}
        dispatched = False
        try:
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                timeout=300,
                env=env,
            )
            dispatched = result.returncode == 0
            token_usage = _extract_token_usage(result.stdout)
            if not dispatched:
                logger.error(f"Task dispatch exited {result.returncode} for {task_id}")
        except subprocess.TimeoutExpired:
            logger.error(f"Task dispatch timed out for {task_id}")
        except FileNotFoundError:
            logger.error(f"{cli} not found in PATH")
        except Exception as e:
            logger.error(f"Failed to dispatch task {task_id}: {e}")
        finally:
            if prompt_file_path:
                try:
                    os.unlink(prompt_file_path)
                except OSError:
                    pass

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

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Load config from environment
    args = parser.parse_args()
    board_id = os.environ.get("MISSION_CONTROL_BOARD_ID")
    if not board_id:
        print("ERROR: MISSION_CONTROL_BOARD_ID not set")
        exit(1)

    client = MissionControlClient()
    if not client.is_configured:
        print("ERROR: Mission Control not configured (check env vars)")
        exit(1)

    dispatch_fn = build_claudem_dispatch() if os.environ.get("MINIMAX_API_KEY") else None
    poller = TaskPoller(board_id=board_id, client=client, dispatch_fn=dispatch_fn)
    print(f"Starting task poller for board {board_id}...")

    if args.once:
        print("Running one poll cycle")
        poller.run_once()
    else:
        poller.run_forever()
