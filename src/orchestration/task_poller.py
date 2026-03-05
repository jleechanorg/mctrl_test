from __future__ import annotations

import logging
import subprocess
from typing import Any, Callable

from orchestration.mc_client import MCClient, TaskStatus

logger = logging.getLogger(__name__)


class TaskPoller:
    """Polls for pending tasks and dispatches them via ai_orch or a custom dispatch function."""

    def __init__(
        self,
        client: MCClient,
        board_id: str | None = None,
        dispatch_fn: Callable[[str], tuple[bool, dict[str, Any]]] | None = None,
    ) -> None:
        self.client = client
        self.board_id = board_id
        self._dispatch_fn = dispatch_fn

    def _dispatch_via_ai_orch(self, task_id: str) -> tuple[bool, dict[str, Any]]:
        """Run ai_orch subprocess for the given task. Returns (success, metadata)."""
        result = subprocess.run(
            ["ai_orch", "run", task_id],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            logger.error(
                "Task %s failed with exit %d: %s",
                task_id,
                result.returncode,
                result.stderr,
            )
            return (False, {"exit_code": result.returncode, "status": TaskStatus.EXECUTION_FAILED})
        return (True, {})

    def _dispatch_task(self, task_id: str) -> bool:
        """Claim and dispatch a single task. Returns True on success."""
        # Atomically claim the task by setting DISPATCHING first
        lock_result = self.client.update_task(
            task_id, TaskStatus.DISPATCHING, board_id=self.board_id
        )
        if lock_result is None:
            logger.warning("task %s already claimed, skipping", task_id)
            return False

        dispatch_fn = self._dispatch_fn if self._dispatch_fn is not None else self._dispatch_via_ai_orch
        try:
            success, meta = dispatch_fn(task_id)
        except Exception as exc:
            logger.error("task %s dispatch raised exception: %s", task_id, exc)
            self.client.update_task(
                task_id,
                TaskStatus.FAILED,
                board_id=self.board_id,
            )
            return False

        if not success:
            error_status = TaskStatus(meta["status"]) if "status" in meta else TaskStatus.FAILED
            self.client.update_task(
                task_id,
                error_status,
                board_id=self.board_id,
            )
            return False

        self.client.update_task(
            task_id,
            TaskStatus.DONE,
            board_id=self.board_id,
            custom_fields=meta,
        )
        return True
