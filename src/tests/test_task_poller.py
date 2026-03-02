"""Tests for orchestration.task_poller — Task polling and dispatch."""

from __future__ import annotations

from unittest.mock import patch, MagicMock
import json

import pytest

from orchestration.task_poller import TaskPoller, detect_cli
from orchestration.mc_client import TaskStatus


class TestDetectCli:
    """Tests for detect_cli function."""

    @patch.dict("os.environ", {}, clear=True)
    def test_defaults_to_claude(self):
        """When no keywords match, defaults to claude."""
        task = {"title": "Generic task", "description": "Just do something"}
        assert detect_cli(task) == "claude"

    @patch.dict("os.environ", {}, clear=True)
    def test_detects_codex(self):
        """Codex keyword triggers codex CLI."""
        task = {"title": "Refactor complex code", "description": "Use codex"}
        assert detect_cli(task) == "codex"

    @patch.dict("os.environ", {}, clear=True)
    def test_detects_gemini(self):
        """Gemini keyword triggers gemini CLI."""
        task = {"title": "Design UI", "description": "Use gemini for creative work"}
        assert detect_cli(task) == "gemini"

    @patch.dict("os.environ", {}, clear=True)
    def test_detects_cursor(self):
        """Cursor keyword triggers cursor CLI."""
        task = {"title": "Fix small bug", "description": "Use cursor for edits"}
        assert detect_cli(task) == "cursor"

    @patch.dict("os.environ", {}, clear=True)
    def test_title_only(self):
        """Keywords in title alone should detect CLI."""
        task = {"title": "Complex refactor needed", "description": ""}
        assert detect_cli(task) == "codex"

    @patch.dict("os.environ", {}, clear=True)
    def test_description_only(self):
        """Keywords in description alone should detect CLI."""
        task = {"title": "Task", "description": "This needs creative design work"}
        assert detect_cli(task) == "gemini"

    @patch.dict("os.environ", {}, clear=True)
    def test_custom_agent_cli_map(self):
        """Custom agent_cli_map is passed to detect_cli and used for dispatch."""
        custom_map = {"special": ["custom-keyword"], "claude": []}
        task = {"title": "custom-keyword task", "description": ""}
        result = detect_cli(task, agent_cli_map=custom_map)
        assert result == "special"

    @patch.dict("os.environ", {}, clear=True)
    def test_custom_agent_cli_map_fallback(self):
        """detect_cli falls back to claude when no keyword matches."""
        custom_map = {"special": ["xyz"], "claude": []}
        task = {"title": "unrelated task", "description": ""}
        result = detect_cli(task, agent_cli_map=custom_map)
        assert result == "claude"

    @patch.dict("os.environ", {"MINIMAX_API_KEY": "test-key"})
    def test_detect_cli_returns_claudem_when_minimax_set(self):
        """When MINIMAX_API_KEY is set, returns claudem regardless of keywords."""
        task = {"title": "Generic task", "description": "Just do something"}
        assert detect_cli(task) == "claudem"

    @patch.dict("os.environ", {}, clear=True)
    def test_detect_cli_uses_prompt_library(self, tmp_path):
        """Prompt library entries override keyword-based detection."""
        library_file = tmp_path / "prompt_library.json"
        library_file.write_text(json.dumps({
            "patterns": {
                "generic task": "codex",
            },
        }))

        task = {"title": "Generic task", "description": "Just do something"}
        assert detect_cli(task, prompt_library_path=library_file) == "codex"


class TestTaskPoller:
    """Tests for TaskPoller class."""

    def test_poll_and_dispatch_empty_tasks(self):
        """When no tasks, poll_and_dispatch returns 0."""
        mock_client = MagicMock()
        mock_client.list_inbox_tasks.return_value = []
        mock_client.is_configured = True

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
        )

        result = poller.poll_and_dispatch()

        assert result == 0
        mock_client.list_inbox_tasks.assert_called_once_with("board-123")

    def test_poll_and_dispatch_single_task(self):
        """Single task is dispatched and status updated."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Test task", "description": "Do work"}
        ]

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
        )

        with patch("orchestration.task_poller.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            result = poller.poll_and_dispatch()

        assert result == 1
        mock_client.update_task.assert_called_once_with("task-1", TaskStatus.IN_PROGRESS, custom_fields=None)

    def test_poll_and_dispatch_multiple_tasks(self):
        """Multiple tasks are each dispatched and status updated."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Task 1", "description": "Work 1"},
            {"id": "task-2", "title": "Task 2", "description": "Work 2"},
            {"id": "task-3", "title": "Task 3", "description": "Work 3"},
        ]

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
        )

        with patch("orchestration.task_poller.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            result = poller.poll_and_dispatch()

        assert result == 3
        assert mock_client.update_task.call_count == 3

    def test_poll_and_dispatch_does_not_count_if_task_status_update_fails(self):
        """Failed status updates are not counted as successful dispatch."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Test task", "description": "Do work"},
        ]
        mock_client.update_task.return_value = {}

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
        )

        with patch("orchestration.task_poller.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            result = poller.poll_and_dispatch()

        assert result == 0
        mock_client.update_task.assert_called_once_with("task-1", TaskStatus.IN_PROGRESS, custom_fields=None)

    def test_poll_and_dispatch_skips_task_without_id(self):
        """Task without id is skipped with warning."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = [
            {"title": "Task without id"},  # Missing id - will skip
            {"id": "task-2", "title": "Task 2", "description": "Work"},
        ]

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
        )

        with patch("orchestration.task_poller.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            with patch("orchestration.task_poller.logger") as mock_logger:
                result = poller.poll_and_dispatch()

        # Verify warning was logged for task without id
        mock_logger.warning.assert_called()
        # Verify at least one task was processed
        assert result >= 1

    def test_poll_and_dispatch_skips_task_requiring_approval(self):
        """Tasks requiring approval are skipped until approved."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = [
            {
                "id": "task-1",
                "title": "Pending approval task",
                "description": "Wait for approval",
                "approval_required": True,
                "approved_at": None,
            },
            {
                "id": "task-2",
                "title": "Task 2",
                "description": "Work",
                "approval_required": True,
                "approved_at": "2026-03-02T00:00:00Z",
            },
        ]

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
        )

        with patch("orchestration.task_poller.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            result = poller.poll_and_dispatch()

        assert result == 1
        assert mock_client.update_task.call_count == 1
        mock_client.update_task.assert_called_once_with("task-2", TaskStatus.IN_PROGRESS, custom_fields=None)
        assert mock_run.call_count == 1

    def test_poll_and_dispatch_not_configured(self):
        """When client not configured, returns 0 without calling API."""
        mock_client = MagicMock()
        mock_client.is_configured = False

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
        )

        result = poller.poll_and_dispatch()

        assert result == 0
        # When not configured, list_inbox_tasks is NOT called
        mock_client.list_inbox_tasks.assert_not_called()

    def test_poll_and_dispatch_uses_dispatch_fn_tuple_and_token_cost(self, tmp_path):
        """Tuple return from dispatch_fn includes cost metadata used in status update."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Test task", "description": "Do work"},
        ]
        mock_client.update_task.return_value = {"id": "task-1", "status": "in_progress"}

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
            dispatch_fn=lambda cli, task: (True, {"input_tokens": 5}),
            prompt_library_path=tmp_path / "prompt_library.json",
        )

        result = poller.poll_and_dispatch()

        assert result == 1
        mock_client.update_task.assert_called_once_with(
            "task-1",
            TaskStatus.IN_PROGRESS,
            custom_fields={"cost": {"input_tokens": 5}},
        )

    def test_poll_and_dispatch_uses_dispatch_fn_dict_payload(self, tmp_path):
        """Dict return from dispatch_fn is supported and includes token usage."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Test task", "description": "Do work"},
        ]
        mock_client.update_task.return_value = {"id": "task-1", "status": "in_progress"}

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
            dispatch_fn=lambda cli, task: {"success": True, "token_usage": {"total_tokens": 9}},
            prompt_library_path=tmp_path / "prompt_library.json",
        )

        result = poller.poll_and_dispatch()

        assert result == 1
        mock_client.update_task.assert_called_once_with(
            "task-1",
            TaskStatus.IN_PROGRESS,
            custom_fields={"cost": {"total_tokens": 9}},
        )

    def test_dispatch_task_blocks_parent_when_subtasks_created(self):
        """When subtasks are created, parent task is marked blocked and not dispatched."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.update_task.return_value = {"id": "task-1", "status": "blocked"}
        mock_client.create_task.side_effect = [
            {"id": "task-sub-1"},
            {"id": "task-sub-2"},
        ]
        mock_client.set_task_dependencies.return_value = {}

        poller = TaskPoller(board_id="board-123", client=mock_client)

        task = {
            "id": "task-1",
            "title": "Parent task",
            "subtasks": [
                {"title": "Subtask 1", "description": "do a"},
                {"title": "Subtask 2", "description": "do b"},
            ],
        }

        result = poller._dispatch_task(task)

        assert result is True
        mock_client.update_task.assert_called_once_with("task-1", TaskStatus.BLOCKED)
        assert mock_client.create_task.call_count == 2
        mock_client.set_task_dependencies.assert_called_once_with("task-sub-2", ["task-sub-1"])

    def test_decompose_task_builds_dependencies_between_subtasks(self):
        """Subtasks inherit explicit and previous subtasks as dependencies."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.create_task.side_effect = [
            {"id": "sub-1"},
            {"id": "sub-2"},
            {"id": "sub-3"},
        ]
        poller = TaskPoller(board_id="board-123", client=mock_client)

        task = {
            "id": "task-1",
            "title": "Parent task",
            "subtasks": [
                {"title": "One", "description": "do one"},
                {"title": "Two", "description": "do two", "depends_on": ["manual"]},
                {"title": "Three", "description": "do three", "depends_on": []},
            ],
        }

        created_ids = poller.decompose_task(task)

        assert created_ids == ["sub-1", "sub-2", "sub-3"]
        assert mock_client.create_task.call_count == 3
        mock_client.set_task_dependencies.assert_any_call("sub-2", ["manual", "sub-1"])
        mock_client.set_task_dependencies.assert_any_call("sub-3", ["sub-2"])

    def test_dispatch_via_subprocess_extracts_token_usage(self):
        """_dispatch_via_subprocess parses token usage from stdout JSON."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        poller = TaskPoller(board_id="board-123", client=mock_client)

        with patch("orchestration.task_poller.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = b'{"input_tokens": 10, "output_tokens": 20, "total_tokens": 30}'
            mock_run.return_value.stderr = b""
            dispatched, token_usage = poller._dispatch_via_subprocess(
                "claude",
                "Work item",
                "task-1",
            )

        assert dispatched is True
        assert token_usage == {"input_tokens": 10, "output_tokens": 20, "total_tokens": 30}

    def test_run_once_calls_poll_and_dispatch(self):
        """run_once calls poll_and_dispatch and returns result."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = []

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
        )

        result = poller.run_once()

        assert result == 0
        mock_client.list_inbox_tasks.assert_called_once()

    def test_run_forever_method_exists(self):
        """run_forever method exists with correct signature."""
        mock_client = MagicMock()

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
            poll_interval_seconds=1,
        )

        # Verify run_forever method exists and is callable
        assert hasattr(poller, "run_forever")
        assert callable(poller.run_forever)

        # Verify poll_interval_seconds is stored in the instance
        assert poller.poll_interval_seconds == 1

    def test_task_poller_optional_client(self):
        """TaskPoller creates client from env if not provided."""
        with patch("orchestration.task_poller.MissionControlClient") as MockClient:
            mock_client_instance = MagicMock()
            MockClient.return_value = mock_client_instance

            poller = TaskPoller(board_id="board-123")

            # Client should be created from env
            MockClient.assert_called_once()
            assert poller.client is mock_client_instance

    def test_dispatch_uses_detect_cli(self):
        """Task dispatch uses detect_cli to pick CLI."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Complex refactor", "description": ""}
        ]

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
        )

        with patch("orchestration.task_poller.subprocess.run") as mock_run:
            with patch("orchestration.task_poller.detect_cli", return_value="codex") as mock_detect:
                poller.poll_and_dispatch()

                mock_detect.assert_called_once()
                # Verify codex was used in the command
                call_args = mock_run.call_args[0][0]
                assert "--agent-cli" in call_args
                cli_index = call_args.index("--agent-cli")
                assert call_args[cli_index + 1] == "codex"
