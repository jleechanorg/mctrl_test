"""Tests for orchestration.heartbeat_bridge — tmux-to-Mission Control sync."""

import json
import threading
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

    def test_all_disappeared_agents_get_failed_event(self):
        """Per-agent isolation: all disappeared agents receive agent_failed, not just the first."""
        notified: list[tuple[str, str]] = []
        done = threading.Event()

        def record_post(url: str, event: str, agent: str) -> None:
            notified.append((event, agent))
            if len(notified) >= 2:
                done.set()

        poller = HeartbeatPoller(webhook_url="http://test/hook", interval_seconds=100)
        poller.bridge.update_known(["agent-a", "agent-b"])

        with (
            patch("orchestration.heartbeat_bridge._post_event", side_effect=record_post),
            patch("orchestration.heartbeat_bridge.list_tmux_sessions", return_value=[]),
            patch("orchestration.heartbeat_bridge.sync_agents_to_mission_control"),
        ):
            poller.start()
            done.wait(timeout=2)
            poller.stop()

        failed_agents = {ag for ev, ag in notified if ev == "agent_failed"}
        assert failed_agents == {"agent-a", "agent-b"}


# ---------------------------------------------------------------------------
# register_or_heartbeat_agent()
# ---------------------------------------------------------------------------


class TestRegisterOrHeartbeatAgent:
    """Tests for register_or_heartbeat_agent function."""

    def test_returns_none_when_unconfigured(self):
        """Returns None when client is not configured."""
        from orchestration.heartbeat_bridge import register_or_heartbeat_agent
        from orchestration.mc_client import MissionControlClient

        client = MissionControlClient(base_url=None, token=None)

        result = register_or_heartbeat_agent("session-1", "board-123", client)

        assert result is None

    @patch("orchestration.heartbeat_bridge._agent_id_cache", {})
    def test_registers_and_returns_agent_id(self):
        """Returns agent ID after successful registration."""
        from orchestration.heartbeat_bridge import register_or_heartbeat_agent
        from orchestration.mc_client import MissionControlClient

        with patch.dict("os.environ", {
            "MISSION_CONTROL_BASE_URL": "http://localhost:8000",
            "MISSION_CONTROL_TOKEN": "test-token",
        }):
            client = MissionControlClient()
            client._post = MagicMock(return_value={"id": "mc-agent-123"})

            result = register_or_heartbeat_agent("session-1", "board-123", client)

            assert result == "mc-agent-123"
            client._post.assert_called_once_with(
                "/api/v1/agents/heartbeat",
                {"name": "session-1", "board_id": "board-123"},
            )

    @patch("orchestration.heartbeat_bridge._agent_id_cache", {})
    def test_caches_agent_id(self):
        """Agent ID is cached after first registration."""
        from orchestration.heartbeat_bridge import register_or_heartbeat_agent, _agent_id_cache
        from orchestration.mc_client import MissionControlClient

        with patch.dict("os.environ", {
            "MISSION_CONTROL_BASE_URL": "http://localhost:8000",
            "MISSION_CONTROL_TOKEN": "test-token",
        }):
            client = MissionControlClient()
            client._post = MagicMock(return_value={"id": "mc-agent-123"})

            # First call
            result1 = register_or_heartbeat_agent("session-1", "board-123", client)
            assert result1 == "mc-agent-123"

            # Second call also sends heartbeat (cache is fallback only, not early exit)
            result2 = register_or_heartbeat_agent("session-1", "board-123", client)
            assert result2 == "mc-agent-123"

            # _post called once per invocation — heartbeat sent every time
            assert client._post.call_count == 2

    @patch("orchestration.heartbeat_bridge._agent_id_cache", {"board-123:session-1": "cached-agent-id"})
    def test_cached_id_does_not_short_circuit_heartbeat(self):
        """Cache hit does not prevent sending a heartbeat request."""
        from orchestration.heartbeat_bridge import register_or_heartbeat_agent
        from orchestration.mc_client import MissionControlClient

        with patch.dict("os.environ", {
            "MISSION_CONTROL_BASE_URL": "http://localhost:8000",
            "MISSION_CONTROL_TOKEN": "test-token",
        }):
            client = MissionControlClient()
            client._post = MagicMock(return_value={"id": "mc-agent-123"})

            result = register_or_heartbeat_agent("session-1", "board-123", client)

            assert result == "mc-agent-123"
            client._post.assert_called_once_with(
                "/api/v1/agents/heartbeat",
                {"name": "session-1", "board_id": "board-123"},
            )

    @patch("orchestration.heartbeat_bridge._agent_id_cache", {})
    def test_returns_none_on_error(self):
        """Returns None when registration fails."""
        from orchestration.heartbeat_bridge import register_or_heartbeat_agent
        from orchestration.mc_client import MissionControlClient, MissionControlError

        with patch.dict("os.environ", {
            "MISSION_CONTROL_BASE_URL": "http://localhost:8000",
            "MISSION_CONTROL_TOKEN": "test-token",
        }):
            client = MissionControlClient()
            client._post = MagicMock(side_effect=MissionControlError("Connection failed"))

            result = register_or_heartbeat_agent("session-1", "board-123", client)

            assert result is None
