"""Tests for orchestration.heartbeat_bridge — tmux-to-Mission Control sync."""

import json
from unittest.mock import patch, MagicMock

import pytest

from orchestration.heartbeat_bridge import (
    list_tmux_sessions,
    sync_agents_to_mission_control,
    HeartbeatBridge,
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
# sync_agents_to_mission_control()
# ---------------------------------------------------------------------------


class TestSyncAgents:
    @patch("orchestration.heartbeat_bridge.list_tmux_sessions", return_value=["agent-1"])
    @patch("orchestration.heartbeat_bridge.urlopen")
    @patch.dict("os.environ", {"MISSION_CONTROL_WEBHOOK_URL": "http://localhost:8080/webhook"})
    def test_heartbeat_posted(self, mock_urlopen, mock_list):
        mock_urlopen.return_value = MagicMock()
        sync_agents_to_mission_control()
        mock_urlopen.assert_called()

    @patch("orchestration.heartbeat_bridge.list_tmux_sessions", return_value=[])
    @patch("orchestration.heartbeat_bridge.urlopen")
    @patch.dict("os.environ", {"MISSION_CONTROL_WEBHOOK_URL": "http://localhost:8080/webhook"})
    def test_no_sessions_no_post(self, mock_urlopen, mock_list):
        sync_agents_to_mission_control()
        # No heartbeat to post when no sessions
        mock_urlopen.assert_not_called()

    @patch("orchestration.heartbeat_bridge.list_tmux_sessions", return_value=["agent-1"])
    @patch("orchestration.heartbeat_bridge.urlopen", side_effect=Exception("network error"))
    @patch.dict("os.environ", {"MISSION_CONTROL_WEBHOOK_URL": "http://localhost:8080/webhook"})
    def test_failure_is_silent(self, mock_urlopen, mock_list):
        """Heartbeat failures must be silent — never block."""
        sync_agents_to_mission_control()  # Should not raise
