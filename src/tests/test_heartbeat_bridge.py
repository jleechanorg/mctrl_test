"""Tests for orchestration.heartbeat_bridge — tmux-to-Mission Control sync."""

import json
from unittest.mock import patch, MagicMock, call

import pytest

from orchestration.heartbeat_bridge import (
    list_tmux_sessions,
    sync_agents_to_mission_control,
    HeartbeatBridge,
    HeartbeatPoller,
    _post_event,
)


# ---------------------------------------------------------------------------
# list_tmux_sessions()
# ---------------------------------------------------------------------------


class TestListTmuxSessions:
    @patch("orchestration.heartbeat_bridge.subprocess.run")
    def test_parses_sessions(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="claude-fix-bug\ncodex-feat-123\ngemini-review\n",
        )
        sessions = list_tmux_sessions()
        assert sessions == ["claude-fix-bug", "codex-feat-123", "gemini-review"]

    @patch("orchestration.heartbeat_bridge.subprocess.run")
    def test_no_sessions(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="no server running")
        sessions = list_tmux_sessions()
        assert sessions == []

    @patch("orchestration.heartbeat_bridge.subprocess.run",
           side_effect=FileNotFoundError("tmux not found"))
    def test_tmux_not_installed(self, mock_run):
        sessions = list_tmux_sessions()
        assert sessions == []


# ---------------------------------------------------------------------------
# HeartbeatBridge
# ---------------------------------------------------------------------------


class TestHeartbeatBridge:
    def test_creation(self):
        bridge = HeartbeatBridge(webhook_url="http://localhost:8080")
        assert bridge is not None

    def test_tracks_known_agents(self):
        bridge = HeartbeatBridge(webhook_url="http://localhost:8080")
        bridge.update_known(["agent-1", "agent-2"])
        assert bridge.known_agents == {"agent-1", "agent-2"}

    def test_detects_disappeared_agents(self):
        bridge = HeartbeatBridge(webhook_url="http://localhost:8080")
        bridge.update_known(["agent-1", "agent-2"])
        disappeared = bridge.detect_disappeared(["agent-1"])
        assert disappeared == {"agent-2"}

    def test_no_disappearances(self):
        bridge = HeartbeatBridge(webhook_url="http://localhost:8080")
        bridge.update_known(["agent-1"])
        disappeared = bridge.detect_disappeared(["agent-1"])
        assert disappeared == set()

    def test_new_agent_detected(self):
        bridge = HeartbeatBridge(webhook_url="http://localhost:8080")
        bridge.update_known(["agent-1"])
        new = bridge.detect_new(["agent-1", "agent-2"])
        assert new == {"agent-2"}


# ---------------------------------------------------------------------------
# _post_event()
# ---------------------------------------------------------------------------


class TestPostEvent:
    @patch("orchestration.heartbeat_bridge.urlopen")
    def test_posts_event(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_resp)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)
        _post_event("http://localhost:8080", "agent_failed", "agent-1")
        mock_urlopen.assert_called_once()

    @patch("orchestration.heartbeat_bridge.urlopen", side_effect=Exception("fail"))
    def test_failure_is_silent(self, mock_urlopen):
        _post_event("http://localhost:8080", "agent_failed", "agent-1")


# ---------------------------------------------------------------------------
# sync_agents_to_mission_control()
# ---------------------------------------------------------------------------


class TestSyncAgents:
    @patch("orchestration.heartbeat_bridge.list_tmux_sessions", return_value=["agent-1"])
    @patch("orchestration.heartbeat_bridge.urlopen")
    def test_heartbeat_posted_with_explicit_url(self, mock_urlopen, mock_list):
        mock_resp = MagicMock()
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_resp)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)
        sync_agents_to_mission_control(webhook_url="http://localhost:8080/webhook")
        mock_urlopen.assert_called()

    @patch("orchestration.heartbeat_bridge.list_tmux_sessions", return_value=["agent-1"])
    @patch("orchestration.heartbeat_bridge.urlopen")
    @patch.dict("os.environ", {"MISSION_CONTROL_WEBHOOK_URL": "http://localhost:8080/webhook"})
    def test_heartbeat_posted_from_env(self, mock_urlopen, mock_list):
        mock_resp = MagicMock()
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_resp)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)
        sync_agents_to_mission_control()
        mock_urlopen.assert_called()

    @patch("orchestration.heartbeat_bridge.list_tmux_sessions", return_value=[])
    @patch("orchestration.heartbeat_bridge.urlopen")
    def test_no_sessions_no_post(self, mock_urlopen, mock_list):
        sync_agents_to_mission_control(webhook_url="http://localhost:8080/webhook")
        mock_urlopen.assert_not_called()

    @patch("orchestration.heartbeat_bridge.list_tmux_sessions", return_value=["agent-1"])
    @patch("orchestration.heartbeat_bridge.urlopen", side_effect=Exception("network error"))
    def test_failure_is_silent(self, mock_urlopen, mock_list):
        """Heartbeat failures must be silent — never block."""
        sync_agents_to_mission_control(webhook_url="http://localhost:8080/webhook")


# ---------------------------------------------------------------------------
# HeartbeatPoller
# ---------------------------------------------------------------------------


class TestHeartbeatPoller:
    def test_creation(self):
        poller = HeartbeatPoller(webhook_url="http://localhost:8080", interval_seconds=60)
        assert poller.interval_seconds == 60
        assert poller.is_running is False

    def test_start_stop(self):
        poller = HeartbeatPoller(webhook_url="http://localhost:8080", interval_seconds=60)
        poller.start()
        assert poller.is_running is True
        poller.stop()
        assert poller.is_running is False

    def test_double_start_idempotent(self):
        poller = HeartbeatPoller(webhook_url="http://localhost:8080", interval_seconds=60)
        poller.start()
        poller.start()  # Should not error
        assert poller.is_running is True
        poller.stop()

    def test_stop_when_not_running(self):
        poller = HeartbeatPoller(webhook_url="http://localhost:8080", interval_seconds=60)
        poller.stop()  # Should not error
        assert poller.is_running is False

    def test_bridge_tracks_agents(self):
        poller = HeartbeatPoller(webhook_url="http://localhost:8080", interval_seconds=60)
        assert isinstance(poller.bridge, HeartbeatBridge)

    def test_uses_explicit_webhook_url(self):
        poller = HeartbeatPoller(webhook_url="http://example.com/hook", interval_seconds=30)
        assert poller.webhook_url == "http://example.com/hook"
