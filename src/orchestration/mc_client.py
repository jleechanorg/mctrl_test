from __future__ import annotations

import logging
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class TaskStatus(StrEnum):
    PENDING = "pending"
    DISPATCHING = "dispatching"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"
    EXECUTION_FAILED = "execution_failed"


class MissionControlClient:
    """Mission Control client that reads configuration from environment."""

    def __init__(self) -> None:
        import os
        self.base_url = os.environ.get("MISSION_CONTROL_BASE_URL", "").rstrip("/")
        self._token = os.environ.get("MISSION_CONTROL_TOKEN", "")

    @property
    def is_configured(self) -> bool:
        return bool(self.base_url and self._token)

    def upsert_agent(
        self,
        board_id: str,
        agent_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register or update an agent heartbeat in Mission Control."""
        import json
        import urllib.request
        import urllib.error

        payload: dict[str, Any] = {"agent_id": agent_id, "board_id": board_id}
        if metadata:
            payload["metadata"] = metadata
        url = f"{self.base_url}/agents/{agent_id}"
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._token}",
            },
            method="PUT",
        )
        try:
            with urllib.request.urlopen(req, timeout=10):
                pass
        except Exception as exc:  # noqa: BLE001
            logger.warning("upsert_agent error for %s: %s", agent_id, exc)


class MCClient:
    """Minimal Mission Control client for task state management."""

    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = base_url
        self.api_key = api_key

    def update_task(
        self,
        task_id: str,
        status: TaskStatus,
        board_id: str | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Update task status. Returns updated task dict or None if update failed (e.g. already claimed)."""
        import urllib.request
        import urllib.error
        import json

        payload: dict[str, Any] = {"status": str(status)}
        if board_id is not None:
            payload["board_id"] = board_id
        if custom_fields is not None:
            payload["custom_fields"] = custom_fields

        url = f"{self.base_url}/tasks/{task_id}"
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="PATCH",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            if exc.code == 409:
                # Already claimed by another worker
                return None
            logger.warning("update_task HTTP error %s for task %s", exc.code, task_id)
            return None
        except Exception as exc:  # noqa: BLE001
            logger.warning("update_task error for task %s: %s", task_id, exc)
            return None
