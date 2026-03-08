"""Tests for orchestration.mc_backend_service."""

from __future__ import annotations

import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from orchestration.mc_backend_service import (
    _is_enabled,
    start_in_process_heartbeat_poller,
    run_service,
    DEFAULT_HEARTBEAT_INTERVAL,
    HEARTBEAT_INTERVAL_ENV,
    POLLER_ENABLE_ENV,
    BOARD_ID_ENV,
)


class TestIsEnabled:
    def test_empty_is_disabled(self):
        assert _is_enabled("") is False
        assert _is_enabled(None) is False

    def test_zero_is_disabled(self):
        assert _is_enabled("0") is False
        assert _is_enabled("false") is False
        assert _is_enabled("no") is False
        assert _is_enabled("off") is False

    def test_any_other_value_is_enabled(self):
        assert _is_enabled("1") is True
        assert _is_enabled("true") is True
        assert _is_enabled("yes") is True


class TestStartInProcessHeartbeatPoller:
    @patch("orchestration.mc_backend_service.MissionControlClient")
    def test_raises_when_not_configured(self, MockClient):
        MockClient.return_value.is_configured = False
        with pytest.raises(RuntimeError, match="Mission Control not configured"):
            start_in_process_heartbeat_poller(board_id="board-123")

    @patch("orchestration.mc_backend_service.sync_agents_to_mission_control")
    @patch("orchestration.mc_backend_service.MissionControlClient")
    def test_starts_daemon_thread(self, MockClient, mock_sync):
        MockClient.return_value.is_configured = True
        # Long interval so the thread parks immediately after the initial sync.
        thread, stop_event = start_in_process_heartbeat_poller(board_id="board-123", interval_seconds=3600)
        assert isinstance(thread, threading.Thread)
        assert thread.daemon is True
        assert thread.is_alive()
        # Thread is daemon so it stops on process exit; no manual teardown needed.

    @patch("orchestration.mc_backend_service.sync_agents_to_mission_control")
    @patch("orchestration.mc_backend_service.MissionControlClient")
    def test_calls_sync_with_board_id_and_client(self, MockClient, mock_sync):
        mock_client = MagicMock()
        mock_client.is_configured = True
        MockClient.return_value = mock_client

        # Long interval: the initial (pre-loop) sync fires synchronously on thread start,
        # so we only need to wait for the thread to execute rather than relying on timing.
        thread, stop_event = start_in_process_heartbeat_poller(board_id="board-abc", interval_seconds=3600)
        thread.join(timeout=1.0)  # Wait briefly; thread parks in stop_event.wait after initial sync.

        # sync_agents_to_mission_control should be called at least once (initial sync)
        assert mock_sync.call_count >= 1
        _, kwargs = mock_sync.call_args_list[0]
        assert kwargs["board_id"] == "board-abc"
        assert kwargs["client"] is mock_client


class TestRunServiceHeartbeatIntegration:
    @patch("orchestration.mc_backend_service._run_uvicorn")
    @patch("orchestration.mc_backend_service.start_in_process_heartbeat_poller")
    def test_starts_heartbeat_alongside_poller(
        self, mock_heartbeat_poller, mock_uvicorn
    ):
        env = {
            POLLER_ENABLE_ENV: "1",
            BOARD_ID_ENV: "board-xyz",
        }
        run_service(app="app.main:app", host="127.0.0.1", port=9010, env=env)

        mock_heartbeat_poller.assert_called_once_with(
            board_id="board-xyz", interval_seconds=DEFAULT_HEARTBEAT_INTERVAL
        )

    @patch("orchestration.mc_backend_service._run_uvicorn")
    @patch("orchestration.mc_backend_service.start_in_process_heartbeat_poller")
    def test_heartbeat_interval_from_env(
        self, mock_heartbeat_poller, mock_uvicorn
    ):
        env = {
            POLLER_ENABLE_ENV: "1",
            BOARD_ID_ENV: "board-xyz",
            HEARTBEAT_INTERVAL_ENV: "30",
        }
        run_service(app="app.main:app", host="127.0.0.1", port=9010, env=env)

        mock_heartbeat_poller.assert_called_once_with(
            board_id="board-xyz", interval_seconds=30
        )

    @patch("orchestration.mc_backend_service._run_uvicorn")
    @patch("orchestration.mc_backend_service.start_in_process_heartbeat_poller")
    def test_no_heartbeat_when_board_id_missing(
        self, mock_heartbeat_poller, mock_uvicorn
    ):
        env = {POLLER_ENABLE_ENV: "1"}
        run_service(app="app.main:app", host="127.0.0.1", port=9010, env=env)

        mock_heartbeat_poller.assert_not_called()

    @patch("orchestration.mc_backend_service._run_uvicorn")
    @patch("orchestration.mc_backend_service.start_in_process_heartbeat_poller")
    def test_invalid_heartbeat_interval_raises(
        self, mock_heartbeat_poller, mock_uvicorn
    ):
        env = {
            POLLER_ENABLE_ENV: "1",
            BOARD_ID_ENV: "board-xyz",
            HEARTBEAT_INTERVAL_ENV: "bad",
        }
        with pytest.raises(RuntimeError, match="must be an integer"):
            run_service(app="app.main:app", host="127.0.0.1", port=9010, env=env)

    @patch("orchestration.mc_backend_service._run_uvicorn")
    @patch("orchestration.mc_backend_service.start_in_process_heartbeat_poller")
    def test_zero_heartbeat_interval_raises(
        self, mock_heartbeat_poller, mock_uvicorn
    ):
        env = {
            POLLER_ENABLE_ENV: "1",
            BOARD_ID_ENV: "board-xyz",
            HEARTBEAT_INTERVAL_ENV: "0",
        }
        with pytest.raises(RuntimeError, match="must be > 0"):
            run_service(app="app.main:app", host="127.0.0.1", port=9010, env=env)
