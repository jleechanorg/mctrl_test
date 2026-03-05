from __future__ import annotations

import logging
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orchestration.mc_client import MissionControlClient

logger = logging.getLogger(__name__)


def run_tmux_sessions() -> set[str]:
    """Return set of active tmux session names. Empty set if tmux not running."""
    try:
        result = subprocess.run(
            ["tmux", "ls", "-F", "#{session_name}"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return set()
        return {line.strip() for line in result.stdout.splitlines() if line.strip()}
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return set()


def get_stuck_tasks(
    client: MissionControlClient,
    board_id: str,
    active_sessions: set[str],
) -> list[dict]:
    """Return in_progress tasks with no matching active tmux session."""
    tasks = client.list_tasks(board_id, status="in_progress") or []
    stuck = []
    for task in tasks:
        task_id = task.get("id", "")
        # Match by task_id prefix in session name
        has_session = any(
            f"-{task_id}-" in s or s.startswith(f"{task_id}-") or s.endswith(f"-{task_id}") or s == task_id
            for s in active_sessions
        )
        if not has_session:
            stuck.append(task)
            logger.warning("Stuck task detected (no active session): %s - %s", task_id, task.get("title", ""))
    return stuck


def reconcile_once(client: MissionControlClient, board_id: str) -> list[str]:
    """Detect stuck tasks and return their IDs. Does NOT auto-transition — human review required."""
    active = run_tmux_sessions()
    stuck = get_stuck_tasks(client, board_id, active)
    return [t.get("id") for t in stuck if t.get("id")]
