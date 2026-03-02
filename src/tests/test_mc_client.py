"""Tests for orchestration.mc_client — Mission Control HTTP client."""

from __future__ import annotations

import json
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError

import pytest

from orchestration.mc_client import (
    MissionControlClient,
    MissionControlError,
    TaskStatus,
)


class TestTaskStatus:
    """Tests for the TaskStatus StrEnum."""

    def test_inbox(self):
        assert TaskStatus.INBOX == "inbox"

    def test_in_progress(self):
        assert TaskStatus.IN_PROGRESS == "in_progress"

    def test_done(self):
        assert TaskStatus.DONE == "done"

    def test_blocked(self):
        assert TaskStatus.BLOCKED == "blocked"


class TestMissionControlClient:
    """Tests for MissionControlClient."""

    def test_unconfigured_returns_none_for_get(self):
        """When not configured, _get returns None without making HTTP calls."""
        with patch.dict("os.environ", {}, clear=True):
            client = MissionControlClient()
            assert client.is_configured is False
            result = client._get("/api/v1/test")
            assert result is None

    def test_unconfigured_returns_none_for_post(self):
        """When not configured, _post returns None without making HTTP calls."""
        with patch.dict("os.environ", {}, clear=True):
            client = MissionControlClient()
            result = client._post("/api/v1/test", {"foo": "bar"})
            assert result is None

    def test_unconfigured_returns_none_for_patch(self):
        """When not configured, _patch returns None without making HTTP calls."""
        with patch.dict("os.environ", {}, clear=True):
            client = MissionControlClient()
            result = client._patch("/api/v1/test/123", {"status": "done"})
            assert result is None

    @patch.dict(
        "os.environ",
        {
            "MISSION_CONTROL_BASE_URL": "http://localhost:8000",
            "MISSION_CONTROL_TOKEN": "test-token",
        },
    )
    @patch("orchestration.mc_client.urlopen")
    def test_get_calls_correct_url(self, mock_urlopen):
        """_get makes request to correct URL with auth headers."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"results": []}'
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)

        client = MissionControlClient()
        client._get("/api/v1/boards/board-123/tasks")

        mock_urlopen.assert_called_once()
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        assert "localhost:8000" in req.full_url
        assert req.full_url.endswith("/api/v1/boards/board-123/tasks")
        assert req.get_header("Authorization") == "Bearer test-token"
        assert req.get_header("Content-type") == "application/json"

    @patch.dict(
        "os.environ",
        {
            "MISSION_CONTROL_BASE_URL": "http://localhost:8000",
            "MISSION_CONTROL_TOKEN": "test-token",
        },
    )
    @patch("orchestration.mc_client.urlopen")
    def test_post_sends_json_body(self, mock_urlopen):
        """_post sends JSON body in request."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"id": "123"}'
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)

        client = MissionControlClient()
        client._post("/api/v1/test", {"name": "test-agent"})

        req = mock_urlopen.call_args[0][0]
        body = json.loads(req.data)
        assert body == {"name": "test-agent"}

    @patch.dict(
        "os.environ",
        {
            "MISSION_CONTROL_BASE_URL": "http://localhost:8000",
            "MISSION_CONTROL_TOKEN": "test-token",
        },
    )
    @patch("orchestration.mc_client.urlopen")
    def test_patch_sends_json_body(self, mock_urlopen):
        """_patch sends JSON body with PATCH method."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"status": "done"}'
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)

        client = MissionControlClient()
        client._patch("/api/v1/tasks/123", {"status": "done"})

        req = mock_urlopen.call_args[0][0]
        assert req.method == "PATCH"
        body = json.loads(req.data)
        assert body == {"status": "done"}

    @patch.dict(
        "os.environ",
        {
            "MISSION_CONTROL_BASE_URL": "http://localhost:8000",
            "MISSION_CONTROL_TOKEN": "test-token",
        },
    )
    @patch("orchestration.mc_client.urlopen")
    def test_list_inbox_tasks_parses_response(self, mock_urlopen):
        """list_inbox_tasks parses JSON response correctly."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "results": [
                {"id": "task-1", "title": "Fix bug"},
                {"id": "task-2", "title": "Add feature"},
            ]
        }).encode()
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)

        client = MissionControlClient()
        tasks = client.list_inbox_tasks("board-123")

        assert len(tasks) == 2
        assert tasks[0]["id"] == "task-1"
        assert tasks[1]["title"] == "Add feature"

    @patch.dict(
        "os.environ",
        {
            "MISSION_CONTROL_BASE_URL": "http://localhost:8000",
            "MISSION_CONTROL_TOKEN": "test-token",
        },
    )
    @patch("orchestration.mc_client.urlopen")
    def test_list_inbox_tasks_empty_on_error(self, mock_urlopen):
        """list_inbox_tasks returns empty list on error."""
        mock_urlopen.side_effect = HTTPError(
            "http://localhost:8000",
            500,
            "Server Error",
            {},
            None,
        )

        client = MissionControlClient()
        tasks = client.list_inbox_tasks("board-123")

        assert tasks == []

    @patch.dict(
        "os.environ",
        {
            "MISSION_CONTROL_BASE_URL": "http://localhost:8000",
            "MISSION_CONTROL_TOKEN": "test-token",
        },
    )
    @patch("orchestration.mc_client.urlopen")
    def test_create_task_posts_payload(self, mock_urlopen):
        """create_task sends POST /api/v1/tasks with body payload."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"id": "task-1"}'
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)

        client = MissionControlClient()
        payload = {"title": "New task", "board_id": "board-1"}
        result = client.create_task(payload)

        req = mock_urlopen.call_args[0][0]
        assert req.full_url == "http://localhost:8000/api/v1/tasks"
        body = json.loads(req.data)
        assert result["id"] == "task-1"
        assert body == payload

    @patch.dict("os.environ", {}, clear=True)
    def test_create_task_unconfigured(self):
        """create_task returns empty when client is unconfigured."""
        client = MissionControlClient(base_url=None, token=None)
        result = client.create_task({"title": "x"})

        assert result == {}

    @patch.dict(
        "os.environ",
        {
            "MISSION_CONTROL_BASE_URL": "http://localhost:8000",
            "MISSION_CONTROL_TOKEN": "test-token",
        },
    )
    @patch("orchestration.mc_client.urlopen")
    def test_set_task_dependencies_posts_payload(self, mock_urlopen):
        """set_task_dependencies sends dependency payload for child task."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"ok": true}'
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)

        client = MissionControlClient()
        result = client.set_task_dependencies("task-1", ["task-a", "task-b"])

        req = mock_urlopen.call_args[0][0]
        assert req.full_url == "http://localhost:8000/api/v1/tasks/task-1/dependencies"
        body = json.loads(req.data)
        assert result == {"ok": True}
        assert body == {"depends_on": ["task-a", "task-b"]}

    @patch.dict("os.environ", {}, clear=True)
    def test_set_task_dependencies_unconfigured(self):
        """set_task_dependencies returns empty when client is unconfigured."""
        client = MissionControlClient(base_url=None, token=None)
        result = client.set_task_dependencies("task-1", ["task-a"])

        assert result == {}

    @patch.dict(
        "os.environ",
        {
            "MISSION_CONTROL_BASE_URL": "http://localhost:8000",
            "MISSION_CONTROL_TOKEN": "test-token",
        },
    )
    @patch("orchestration.mc_client.urlopen")
    def test_update_task_sends_correct_payload(self, mock_urlopen):
        """update_task sends correct PATCH payload."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"id": "task-1", "status": "in_progress"}'
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)

        client = MissionControlClient()
        result = client.update_task("task-1", TaskStatus.IN_PROGRESS, "agent-123")

        req = mock_urlopen.call_args[0][0]
        body = json.loads(req.data)
        assert body["status"] == "in_progress"
        assert body["assigned_agent_id"] == "agent-123"

    @patch.dict("os.environ", {}, clear=True)
    @patch("orchestration.mc_client.urlopen")
    def test_update_task_returns_empty_when_unconfigured(self, mock_urlopen):
        """update_task returns empty dict when not configured."""
        client = MissionControlClient(base_url=None, token=None)
        result = client.update_task("task-1", TaskStatus.DONE)

        assert result == {}
        mock_urlopen.assert_not_called()

    @patch.dict(
        "os.environ",
        {
            "MISSION_CONTROL_BASE_URL": "http://localhost:8000",
            "MISSION_CONTROL_TOKEN": "test-token",
        },
    )
    @patch("orchestration.mc_client.urlopen")
    def test_mission_control_error_raised_on_4xx(self, mock_urlopen):
        """MissionControlError raised on 4xx response."""
        mock_urlopen.side_effect = HTTPError(
            "http://localhost:8000/api/v1/tasks/123",
            404,
            "Not Found",
            {},
            None,
        )

        client = MissionControlClient()
        with pytest.raises(MissionControlError) as exc_info:
            client._get("/api/v1/tasks/123")

        assert exc_info.value.status_code == 404

    @patch.dict(
        "os.environ",
        {
            "MISSION_CONTROL_BASE_URL": "http://localhost:8000",
            "MISSION_CONTROL_TOKEN": "test-token",
        },
    )
    @patch("orchestration.mc_client.urlopen")
    def test_mission_control_error_raised_on_5xx(self, mock_urlopen):
        """MissionControlError raised on 5xx response."""
        mock_urlopen.side_effect = HTTPError(
            "http://localhost:8000/api/v1/tasks",
            500,
            "Internal Server Error",
            {},
            None,
        )

        client = MissionControlClient()
        with pytest.raises(MissionControlError) as exc_info:
            client._get("/api/v1/tasks")

        assert exc_info.value.status_code == 500

    @patch.dict(
        "os.environ",
        {
            "MISSION_CONTROL_BASE_URL": "http://localhost:8000",
            "MISSION_CONTROL_TOKEN": "test-token",
        },
    )
    @patch("orchestration.mc_client.urlopen")
    def test_timeout_is_set(self, mock_urlopen):
        """HTTP requests use configured timeout."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"{}"
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)

        client = MissionControlClient(timeout=15.0)
        client._get("/api/v1/test")

        call_args = mock_urlopen.call_args
        assert call_args[1].get("timeout") == 15.0
