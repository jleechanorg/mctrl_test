"""Mission Control client — HTTP API wrapper for Mission Control dashboard.

Provides a typed client for Mission Control REST APIs.
Graceful no-op when unconfigured.
"""

from __future__ import annotations

import json
import os
from enum import StrEnum
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class MissionControlError(Exception):
    """Raised when Mission Control API returns non-2xx or connection fails."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class TaskStatus(StrEnum):
    """Task status values in Mission Control."""
    INBOX = "inbox"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"


class MissionControlClient:
    """HTTP client for Mission Control REST API.

    Reads configuration from environment variables:
    - MISSION_CONTROL_BASE_URL: Base URL (e.g., http://localhost:8000)
    - MISSION_CONTROL_TOKEN: Bearer token for authentication
    """

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float = 10.0,
    ):
        """Initialize the Mission Control client.

        Args:
            base_url: Override MISSION_CONTROL_BASE_URL. None = use env or unconfigured.
            token: Override MISSION_CONTROL_TOKEN. None = use env or unconfigured.
            timeout: Request timeout in seconds. Default 10s.
        """
        self._base_url = base_url or os.environ.get("MISSION_CONTROL_BASE_URL")
        self._token = token or os.environ.get("MISSION_CONTROL_TOKEN")
        self._timeout = timeout
        self._configured = bool(self._base_url and self._token)

    @property
    def is_configured(self) -> bool:
        """Check if client is properly configured."""
        return self._configured

    def _get_headers(self) -> dict[str, str]:
        """Build request headers with auth."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._token}",
        }

    def _request(
        self,
        method: str,
        path: str,
        body: dict | None = None,
    ) -> dict | None:
        """Make HTTP request to Mission Control API.

        Args:
            method: HTTP method (GET, POST, PATCH, etc.)
            path: API path (e.g., /api/v1/boards/123/tasks)
            body: Optional JSON body dict

        Returns:
            Parsed JSON response dict, or None if unconfigured.

        Raises:
            MissionControlError: On non-2xx response or connection error.
        """
        if not self._configured:
            return None

        url = f"{self._base_url}{path}"
        headers = self._get_headers()

        try:
            data = json.dumps(body).encode("utf-8") if body else None
            req = Request(url, data=data, headers=headers, method=method)
            with urlopen(req, timeout=self._timeout) as resp:
                response_body = resp.read()
                if response_body:
                    return json.loads(response_body)
                return {}
        except HTTPError as e:
            try:
                error_body = e.read().decode("utf-8")
                error_data = json.loads(error_body) if error_body else {}
                error_msg = error_data.get("detail", str(e))
            except Exception:
                error_msg = str(e)
            raise MissionControlError(error_msg, status_code=e.code) from e
        except URLError as e:
            raise MissionControlError(f"Connection failed: {e.reason}") from e
        except json.JSONDecodeError as e:
            raise MissionControlError(f"Invalid JSON response: {e}") from e
        except Exception as e:
            raise MissionControlError(f"Request failed: {e}") from e

    def _get(self, path: str) -> dict | None:
        """Make GET request."""
        return self._request("GET", path)

    def _post(self, path: str, body: dict | None = None) -> dict | None:
        """Make POST request."""
        return self._request("POST", path, body)

    def _patch(self, path: str, body: dict | None = None) -> dict | None:
        """Make PATCH request."""
        return self._request("PATCH", path, body)

    @staticmethod
    def _normalize_task_payload(payload: dict) -> dict:
        """Normalize legacy payload shape to TaskCreate/TaskUpdate schema fields."""
        body = dict(payload)
        if "custom_fields" in body and "custom_field_values" not in body:
            body["custom_field_values"] = body.pop("custom_fields")

        allowed_keys = {
            "title",
            "description",
            "status",
            "priority",
            "due_at",
            "assigned_agent_id",
            "depends_on_task_ids",
            "tag_ids",
            "created_by_user_id",
            "custom_field_values",
            "comment",
        }
        return {k: v for k, v in body.items() if k in allowed_keys}

    # === Task API ===

    def list_inbox_tasks(self, board_id: str) -> list[dict]:
        """List tasks in inbox for a board.

        Args:
            board_id: The Mission Control board UUID.

        Returns:
            List of task dicts, or empty list if unconfigured/error.
        """
        if not self._configured:
            return []

        try:
            result = self._get(f"/api/v1/boards/{board_id}/tasks?status=inbox")
            if result is None:
                return []
            # Handle different response shapes: {"items": [...]}, {"results": [...]}, or [...]
            if isinstance(result, list):
                return result
            return result.get("items", result.get("results", []))
        except MissionControlError:
            return []

    def update_task(
        self,
        task_id: str,
        status: TaskStatus,
        assigned_agent_id: str | None = None,
        custom_fields: dict | None = None,
        board_id: str | None = None,
    ) -> dict:
        """Update a task in Mission Control.

        Args:
            task_id: The task UUID.
            status: New task status.
            assigned_agent_id: Optional agent ID to assign the task to.
            custom_fields: Optional task custom fields payload.
            board_id: Board UUID. When provided uses /api/v1/boards/{board_id}/tasks/{task_id}.

        Returns:
            Updated task dict, or empty dict if unconfigured.
        """
        if not self._configured:
            return {}

        body: dict = {"status": str(status)}
        if assigned_agent_id:
            body["assigned_agent_id"] = assigned_agent_id
        if custom_fields is not None:
            body["custom_field_values"] = custom_fields

        path = (
            f"/api/v1/boards/{board_id}/tasks/{task_id}"
            if board_id
            else f"/api/v1/tasks/{task_id}"
        )
        try:
            result = self._patch(path, body)
            return result or {}
        except MissionControlError as e:
            # Some boards reject unknown custom fields; retry status-only update.
            if e.status_code == 422 and "custom_field_values" in body:
                retry_body = dict(body)
                retry_body.pop("custom_field_values", None)
                try:
                    result = self._patch(path, retry_body)
                    return result or {}
                except MissionControlError:
                    return {}
            return {}

    def create_task(self, payload: dict) -> dict:
        """Create a new task in Mission Control.

        Args:
            payload: New task payload.

        Returns:
            Created task dict, or empty dict if unconfigured.
        """
        if not self._configured:
            return {}

        board_id = payload.get("board_id")
        normalized_payload = self._normalize_task_payload(payload)

        if isinstance(board_id, str) and board_id.strip():
            try:
                result = self._post(
                    f"/api/v1/boards/{board_id}/tasks",
                    normalized_payload,
                )
                return result or {}
            except MissionControlError as e:
                # Backwards compatibility for older MC API versions.
                if e.status_code not in (404, 405):
                    return {}

        try:
            result = self._post("/api/v1/tasks", payload)
            return result or {}
        except MissionControlError:
            return {}

    def set_task_dependencies(
        self,
        task_id: str,
        depends_on_ids: list[str],
        *,
        board_id: str | None = None,
    ) -> dict:
        """Set task dependencies in Mission Control.

        Args:
            task_id: Task UUID.
            depends_on_ids: List of upstream dependency task IDs.
            board_id: Optional board UUID for board-scoped API.

        Returns:
            Response payload, or empty dict if unconfigured.
        """
        if not self._configured:
            return {}

        if board_id:
            try:
                result = self._patch(
                    f"/api/v1/boards/{board_id}/tasks/{task_id}",
                    {"depends_on_task_ids": depends_on_ids},
                )
                return result or {}
            except MissionControlError as e:
                # Backwards compatibility for older MC API versions.
                if e.status_code not in (404, 405):
                    return {}

        try:
            result = self._post(
                f"/api/v1/tasks/{task_id}/dependencies",
                {"depends_on": depends_on_ids},
            )
            return result or {}
        except MissionControlError:
            return {}
