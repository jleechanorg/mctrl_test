"""Tests for E2E harness and claudem dispatch adapter.

Tests cover:
- FakeMissionControlServer behavior
- dispatch_fn injection in TaskPoller
- build_claudem_dispatch() factory
- detect_cli() minimax path
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
from orchestration.task_poller import (
    TaskPoller,
    detect_cli,
    build_claudem_dispatch,
)
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

    @patch.dict("os.environ", {}, clear=True)
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

        # CLI may be selected by prompt-library defaults (claudem) or fallback (claude)
        assert captured_args.get("cli") in {"claude", "claudem"}
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


class TestBuildClaudemDispatch:
    """Tests for build_claudem_dispatch factory."""

    @patch("orchestration.task_poller.subprocess.run")
    def test_returns_callable(self, mock_run):
        """build_claudem_dispatch returns a callable."""
        mock_run.return_value.returncode = 0
        dispatch_fn = build_claudem_dispatch()

        assert callable(dispatch_fn)

    @patch("orchestration.task_poller.subprocess.run")
    def test_calls_claudem_with_task_info(self, mock_run):
        """Dispatch function calls claude binary with task summary (not claudem bash fn)."""
        mock_run.return_value.returncode = 0
        dispatch_fn = build_claudem_dispatch()

        task = {"id": "task-123", "title": "My Task", "description": "Task desc"}
        dispatch_fn("claudem", task)

        # Verify subprocess.run was called
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        call_kwargs = mock_run.call_args[1]
        # cmd should pass prompt over stdin (no -p with --print)
        assert call_args == ["claude", "--dangerously-skip-permissions", "--print"]
        assert call_kwargs.get("input") == b"My Task: Task desc"

    @patch("orchestration.task_poller.subprocess.run")
    def test_returns_true_on_success(self, mock_run):
        """Dispatch function returns True on successful dispatch."""
        mock_run.return_value.returncode = 0
        dispatch_fn = build_claudem_dispatch()

        result = dispatch_fn("claudem", {"id": "task-1", "title": "Test"})

        assert result is True

    @patch("orchestration.task_poller.subprocess.run")
    def test_returns_false_on_failure(self, mock_run):
        """Dispatch function returns False when claudem exits non-zero."""
        mock_run.return_value.returncode = 1
        dispatch_fn = build_claudem_dispatch()

        result = dispatch_fn("claudem", {"id": "task-1", "title": "Test"})

        assert result is False

    @patch("orchestration.task_poller.subprocess.run")
    def test_uses_timeout_of_300(self, mock_run):
        """Dispatch function uses 300s timeout."""
        mock_run.return_value.returncode = 0
        dispatch_fn = build_claudem_dispatch()

        dispatch_fn("claudem", {"id": "task-1", "title": "Test"})

        call_kwargs = mock_run.call_args[1]
        assert call_kwargs.get("timeout") == 300


class TestDetectCliMinimax:
    """Tests for detect_cli minimax path."""

    @patch.dict("os.environ", {"MINIMAX_API_KEY": "test-key-123"})
    def test_returns_claudem_when_minimax_set(self):
        """When MINIMAX_API_KEY is set, returns claudem."""
        task = {"title": "Any task", "description": "Any description"}
        result = detect_cli(task)

        assert result == "claudem"

    @patch.dict("os.environ", {}, clear=True)
    def test_falls_back_to_keyword_detection(self):
        """When MINIMAX_API_KEY not set, falls back to keyword detection."""
        task = {"title": "Refactor complex code", "description": ""}
        result = detect_cli(task)

        assert result == "codex"

    @patch.dict("os.environ", {}, clear=True)
    def test_falls_back_to_claude_when_no_keywords(self):
        """When no keywords match, defaults to claude."""
        task = {"title": "Random task", "description": "Nothing special"}
        result = detect_cli(task)

        assert result == "claude"
