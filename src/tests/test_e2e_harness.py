"""Tests for E2E harness and dispatch_fn injection.

Tests cover:
- FakeMissionControlServer behavior
- dispatch_fn injection in TaskPoller
"""

from __future__ import annotations

import json
import threading
from http.server import HTTPServer
from unittest.mock import patch, MagicMock
import pytest
import sys
from pathlib import Path

# Add src to path for imports
_src_path = str(Path(__file__).parent.parent.parent)
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)

from integration.run_e2e import (
    FakeMissionControlServer,
    FAKE_TASKS,
)
from orchestration.task_poller import TaskPoller
from orchestration.mc_client import TaskStatus


class TestFakeMissionControlServer:
    """Tests for FakeMissionControlServer."""

    def setup_method(self):
        """Clear fake tasks before each test."""
        FAKE_TASKS.clear()

    def teardown_method(self):
        """Clear fake tasks after each test."""
        FAKE_TASKS.clear()

    def test_server_starts_on_available_port(self):
        """Fake server starts on a random available port."""
        server = FakeMissionControlServer()
        port = server.start()

        assert port is not None
        assert port > 0
        server.stop()

    def test_seed_task_creates_inbox_task(self):
        """Seeding a task creates it with inbox status."""
        server = FakeMissionControlServer()
        server.start()

        try:
            server.seed_task("task-1", "Test Task", "Test Description")
            status = server.get_task_status("task-1")

            assert status == "inbox"
            assert FAKE_TASKS["task-1"]["title"] == "Test Task"
            assert FAKE_TASKS["task-1"]["description"] == "Test Description"
        finally:
            server.stop()

    def test_get_task_status_returns_none_for_nonexistent(self):
        """Getting status for nonexistent task returns None."""
        server = FakeMissionControlServer()
        server.start()

        try:
            status = server.get_task_status("nonexistent")
            assert status is None
        finally:
            server.stop()

    def test_seed_task_updates_existing_task(self):
        """Seeding with same ID updates existing task."""
        server = FakeMissionControlServer()
        server.start()

        try:
            server.seed_task("task-1", "Original", "Original desc")
            server.seed_task("task-1", "Updated", "Updated desc")

            assert FAKE_TASKS["task-1"]["title"] == "Updated"
            assert FAKE_TASKS["task-1"]["description"] == "Updated desc"
        finally:
            server.stop()


class TestDispatchFn:
    """Tests for dispatch_fn parameter in TaskPoller."""

    def test_dispatch_fn_receives_correct_args(self):
        """dispatch_fn is called with (cli, task) arguments."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Test Task", "description": "Description"}
        ]

        captured_args = {}

        def capture_dispatch(cli: str, task: dict) -> bool:
            captured_args["cli"] = cli
            captured_args["task"] = task
            return True

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
            dispatch_fn=capture_dispatch,
        )

        poller.poll_and_dispatch()

        assert captured_args.get("cli") is None  # default agent_cli is None
        assert captured_args.get("task").get("id") == "task-1"

    def test_dispatch_fn_overrides_subprocess(self):
        """When dispatch_fn is set, subprocess is not called."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Test Task", "description": "Description"}
        ]

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
            dispatch_fn=lambda cli, task: True,
        )

        with patch("orchestration.task_poller.subprocess.run") as mock_run:
            poller.poll_and_dispatch()
            # subprocess.run should NOT be called when dispatch_fn is set
            mock_run.assert_not_called()

    def test_dispatch_fn_failure_does_not_update_status(self):
        """When dispatch_fn returns False, status is not updated to in_progress."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Test Task", "description": "Description"}
        ]

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
            dispatch_fn=lambda cli, task: False,  # Return False = failure
        )

        poller.poll_and_dispatch()

        # update_task should NOT be called when dispatch fails
        mock_client.update_task.assert_not_called()


