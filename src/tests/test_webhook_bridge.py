"""Tests for orchestration.webhook_bridge — fire-and-forget Mission Control notifier."""

import json
from unittest.mock import patch, MagicMock

import pytest

from orchestration.webhook_bridge import notify_mission_control, WebhookEvent


class TestWebhookEvent:
    """Tests for the WebhookEvent enum/constants."""

    def test_agent_started(self):
        assert WebhookEvent.AGENT_STARTED == "agent_started"

    def test_agent_failed(self):
        assert WebhookEvent.AGENT_FAILED == "agent_failed"

    def test_task_complete(self):
        assert WebhookEvent.TASK_COMPLETE == "task_complete"

    def test_agent_killed(self):
        assert WebhookEvent.AGENT_KILLED == "agent_killed"


class TestNotifyMissionControl:
    """Tests for notify_mission_control()."""

    @patch.dict("os.environ", {"MISSION_CONTROL_WEBHOOK_URL": "http://localhost:8080/webhook"})
    @patch("orchestration.webhook_bridge.urlopen")
    def test_successful_post(self, mock_urlopen):
        mock_response = MagicMock()
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)
        notify_mission_control(
            WebhookEvent.AGENT_STARTED,
            {"agent_name": "claude-1", "task": "Fix bug #42"},
        )
        mock_urlopen.assert_called_once()
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        body = json.loads(req.data)
        assert body["event"] == "agent_started"
        assert body["agent_name"] == "claude-1"

    @patch.dict("os.environ", {}, clear=True)
    @patch("orchestration.webhook_bridge.urlopen")
    def test_no_url_configured_is_noop(self, mock_urlopen):
        """When MISSION_CONTROL_WEBHOOK_URL is not set, do nothing."""
        notify_mission_control(
            WebhookEvent.AGENT_STARTED,
            {"agent_name": "claude-1"},
        )
        mock_urlopen.assert_not_called()

    @patch.dict("os.environ", {"MISSION_CONTROL_WEBHOOK_URL": "http://localhost:8080/webhook"})
    @patch("orchestration.webhook_bridge.urlopen", side_effect=Exception("connection refused"))
    def test_failure_is_silent(self, mock_urlopen):
        """Failure must never raise — fire-and-forget."""
        # Should not raise
        notify_mission_control(
            WebhookEvent.AGENT_FAILED,
            {"agent_name": "codex-2", "exit_code": 1},
        )
        mock_urlopen.assert_called_once()

    @patch.dict("os.environ", {"MISSION_CONTROL_WEBHOOK_URL": "http://localhost:8080/webhook"})
    @patch("orchestration.webhook_bridge.urlopen")
    def test_content_type_json(self, mock_urlopen):
        notify_mission_control(
            WebhookEvent.TASK_COMPLETE,
            {"pr_url": "https://github.com/o/r/pull/1"},
        )
        req = mock_urlopen.call_args[0][0]
        assert req.get_header("Content-type") == "application/json"

    @patch.dict("os.environ", {"MISSION_CONTROL_WEBHOOK_URL": "http://localhost:8080/webhook"})
    @patch("orchestration.webhook_bridge.urlopen")
    def test_timeout_is_set(self, mock_urlopen):
        notify_mission_control(WebhookEvent.AGENT_KILLED, {"reason": "manual"})
        call_args = mock_urlopen.call_args
        # Timeout is passed as kwarg to urlopen
        assert call_args[1].get("timeout") == 5

    @patch.dict("os.environ", {"MISSION_CONTROL_WEBHOOK_URL": "http://localhost:8080/webhook"})
    @patch("orchestration.webhook_bridge.urlopen", side_effect=TimeoutError("timed out"))
    def test_timeout_is_silent(self, mock_urlopen):
        """Timeout must not raise."""
        notify_mission_control(WebhookEvent.AGENT_STARTED, {"agent_name": "test"})
        mock_urlopen.assert_called_once()

    @patch.dict("os.environ", {}, clear=True)
    @patch("orchestration.webhook_bridge.urlopen")
    def test_explicit_url_overrides_env(self, mock_urlopen):
        """Explicit webhook_url param should work even without env var."""
        mock_response = MagicMock()
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_response)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)
        notify_mission_control(
            WebhookEvent.AGENT_STARTED,
            {"agent_name": "claude-1"},
            webhook_url="http://explicit.example.com/webhook",
        )
        mock_urlopen.assert_called_once()
        req = mock_urlopen.call_args[0][0]
        assert "explicit.example.com" in req.full_url
