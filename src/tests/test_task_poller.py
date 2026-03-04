"""Tests for orchestration.task_poller — Task polling and dispatch."""

from __future__ import annotations

import threading
from unittest.mock import patch, MagicMock, call
import json

import pytest

from orchestration.task_poller import TaskPoller, detect_cli
from orchestration.mc_client import TaskStatus


@pytest.fixture(autouse=True)
def _clear_minimax_api_key(monkeypatch):
    """Keep tests hermetic unless a test explicitly sets MINIMAX_API_KEY."""
    monkeypatch.delenv("MINIMAX_API_KEY", raising=False)


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
    def test_detect_cli_handles_none_title_and_description(self):
        """None values should be treated as empty strings, not crash."""
        task = {"title": None, "description": None}
        assert detect_cli(task) == "claude"

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
        mock_client.update_task.return_value = {"id": "task-1", "status": "done"}
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Test task", "description": "Do work"}
        ]

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
        )

        with patch.object(poller, "_dispatch_via_subprocess", return_value=(True, {})):
            result = poller.poll_and_dispatch()

        assert result == 1
        mock_client.update_task.assert_has_calls(
            [
                call("task-1", TaskStatus.IN_PROGRESS, custom_fields=None, board_id="board-123"),
                call("task-1", TaskStatus.DONE, board_id="board-123"),
            ],
        )
        assert mock_client.update_task.call_count == 2

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

        with patch.object(poller, "_dispatch_via_subprocess", return_value=(True, {})):
            result = poller.poll_and_dispatch()

        assert result == 3
        assert mock_client.update_task.call_count == 6

    def test_poll_and_dispatch_dispatches_tasks_concurrently(self):
        """With dispatch_concurrency > 1, task dispatches overlap in time."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Task 1", "description": "Work 1"},
            {"id": "task-2", "title": "Task 2", "description": "Work 2"},
        ]

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
            dispatch_concurrency=2,
        )

        started = 0
        lock = threading.Lock()
        both_started = threading.Event()
        overlap_checks: list[bool] = []

        def blocking_dispatch(_task: dict) -> bool:
            nonlocal started
            with lock:
                started += 1
                if started == 2:
                    both_started.set()
            did_overlap = both_started.wait(timeout=0.5)
            with lock:
                overlap_checks.append(did_overlap)
            return True

        with patch.object(poller, "_dispatch_task", side_effect=blocking_dispatch):
            result = poller.poll_and_dispatch()

        assert result == 2
        assert overlap_checks == [True, True]

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

        with patch.object(poller, "_dispatch_via_subprocess", return_value=(True, {})):
            result = poller.poll_and_dispatch()

        assert result == 0
        mock_client.update_task.assert_called_once_with("task-1", TaskStatus.IN_PROGRESS, custom_fields=None, board_id="board-123")

    def test_poll_and_dispatch_does_not_count_if_done_update_fails(self):
        """Done transition failure leaves dispatch uncounted."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Test task", "description": "Do work"},
        ]
        mock_client.update_task.side_effect = [
            {"id": "task-1", "status": "in_progress"},
            {},
        ]

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
        )

        with patch.object(poller, "_dispatch_via_subprocess", return_value=(True, {})):
            result = poller.poll_and_dispatch()

        assert result == 0
        mock_client.update_task.assert_has_calls(
            [
                call("task-1", TaskStatus.IN_PROGRESS, custom_fields=None, board_id="board-123"),
                call("task-1", TaskStatus.DONE, board_id="board-123"),
            ],
        )
        assert mock_client.update_task.call_count == 2

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

        with patch.object(poller, "_dispatch_via_subprocess", return_value=(True, {})):
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
        mock_client.update_task.return_value = {"id": "task-2", "status": "done"}
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

        with patch.object(poller, "_dispatch_via_subprocess", return_value=(True, {})) as mock_dispatch:
            result = poller.poll_and_dispatch()

        assert result == 1
        mock_client.update_task.assert_has_calls(
            [
                call("task-2", TaskStatus.IN_PROGRESS, custom_fields=None, board_id="board-123"),
                call("task-2", TaskStatus.DONE, board_id="board-123"),
            ],
        )
        assert mock_client.update_task.call_count == 2
        assert mock_dispatch.call_count == 1

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
        mock_client.update_task.assert_has_calls(
            [
                call(
                    "task-1",
                    TaskStatus.IN_PROGRESS,
                    custom_fields={"cost": {"input_tokens": 5}},
                    board_id="board-123",
                ),
                call("task-1", TaskStatus.DONE, board_id="board-123"),
            ],
        )
        assert mock_client.update_task.call_count == 2

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
        mock_client.update_task.assert_has_calls(
            [
                call(
                    "task-1",
                    TaskStatus.IN_PROGRESS,
                    custom_fields={"cost": {"total_tokens": 9}},
                    board_id="board-123",
                ),
                call("task-1", TaskStatus.DONE, board_id="board-123"),
            ],
        )
        assert mock_client.update_task.call_count == 2

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
        mock_client.update_task.assert_called_once_with("task-1", TaskStatus.BLOCKED, board_id="board-123")
        assert mock_client.create_task.call_count == 2
        mock_client.set_task_dependencies.assert_called_once_with(
            "task-sub-2",
            ["task-sub-1"],
            board_id="board-123",
        )

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
        mock_client.set_task_dependencies.assert_any_call(
            "sub-2",
            ["manual", "sub-1"],
            board_id="board-123",
        )
        mock_client.set_task_dependencies.assert_any_call(
            "sub-3",
            ["sub-2"],
            board_id="board-123",
        )

    def test_dispatch_via_subprocess_succeeds_on_zero_returncode(self):
        """_dispatch_via_subprocess returns (True, ...) when agent exits 0."""
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

    def test_dispatch_via_subprocess_uses_sync_commands_not_ai_orch(self):
        """_dispatch_via_subprocess must NOT use ai_orch (tmux-detached, exits 0 immediately).
        Must use CLI-specific sync commands that block until agent completes."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        poller = TaskPoller(board_id="board-123", client=mock_client)

        with patch("orchestration.task_poller.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = b""
            mock_run.return_value.stderr = b""
            poller._dispatch_via_subprocess("claude", "do the thing", "task-1")
            cmd = mock_run.call_args[0][0]

            assert "ai_orch" not in cmd, "ai_orch creates detached tmux sessions (exits 0 immediately)"
            assert "claude" in cmd
            assert "--dangerously-skip-permissions" in cmd

    def test_dispatch_via_subprocess_codex_uses_exec_subcommand(self):
        """codex CLI must use 'codex exec --yolo' (non-interactive), not ai_orch."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        poller = TaskPoller(board_id="board-123", client=mock_client)

        with patch("orchestration.task_poller.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = b""
            mock_run.return_value.stderr = b""
            poller._dispatch_via_subprocess("codex", "do the thing", "task-1")
            cmd = mock_run.call_args[0][0]

            assert "codex" in cmd
            assert "exec" in cmd
            assert "--yolo" in cmd
            assert "ai_orch" not in cmd

    def test_dispatch_via_subprocess_gemini_uses_yolo_stdin_mode(self):
        """gemini CLI must use '--yolo' with stdin (not deprecated -p flag), not ai_orch."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        poller = TaskPoller(board_id="board-123", client=mock_client)

        with patch("orchestration.task_poller.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = b""
            mock_run.return_value.stderr = b""
            poller._dispatch_via_subprocess("gemini", "do the thing", "task-1")
            cmd = mock_run.call_args[0][0]
            call_kwargs = mock_run.call_args[1] if mock_run.call_args[1] else {}
            stdin_input = mock_run.call_args[0][1] if len(mock_run.call_args[0]) > 1 else call_kwargs.get("input")

            assert "gemini" in cmd
            assert "--yolo" in cmd
            assert "-p" not in cmd, "gemini -p flag is deprecated; prompt must go via stdin"
            assert "ai_orch" not in cmd
            assert stdin_input is not None, "gemini prompt must be passed via stdin"

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

    def test_dispatch_uses_detect_cli(self, monkeypatch):
        """Task dispatch uses detect_cli to pick CLI (requires no MINIMAX_API_KEY)."""
        monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Complex refactor", "description": ""}
        ]

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
        )

        with patch.object(poller, "_dispatch_via_subprocess", return_value=(True, {})) as mock_dispatch:
            with patch("orchestration.task_poller.detect_cli", return_value="codex") as mock_detect:
                poller.poll_and_dispatch()

                mock_detect.assert_called_once()
                # Verify dispatch was called with the cli returned by detect_cli
                assert mock_dispatch.call_args[0][0] == "codex"


class TestMinimaxDispatchWiring:
    """When MINIMAX_API_KEY is set, TaskPoller must use build_claudem_dispatch,
    not pass 'claudem' to ai_orch (which rejects it with exit code 2)."""

    @patch.dict("os.environ", {"MINIMAX_API_KEY": "test-key"})
    def test_poller_auto_wires_claudem_dispatch_when_minimax_key_set(self):
        """TaskPoller.__post_init__ sets dispatch_fn=build_claudem_dispatch()
        when MINIMAX_API_KEY is present and no explicit dispatch_fn given."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = []

        poller = TaskPoller(board_id="board-123", client=mock_client)
        assert poller.dispatch_fn is not None, (
            "dispatch_fn should be auto-set when MINIMAX_API_KEY is present; "
            "otherwise detect_cli returns 'claudem' which ai_orch rejects with exit 2"
        )

    @patch.dict("os.environ", {"MINIMAX_API_KEY": "test-key"})
    def test_dispatch_uses_claudem_fn_not_subprocess_when_minimax_key_set(self):
        """With MINIMAX_API_KEY set, dispatch goes through claudem dispatch_fn,
        NOT subprocess.run — ensuring 'claudem' is never passed to the inline subprocess path."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "hello world task", "description": "write hello world"}
        ]
        mock_client.update_task.return_value = {"id": "task-1", "status": "in_progress"}

        dispatch_called_with: list = []

        def fake_claudem_dispatch(cli: str, task: dict) -> bool:
            dispatch_called_with.append((cli, task))
            return True

        poller = TaskPoller(board_id="board-123", client=mock_client)
        # Replace auto-wired dispatch_fn with our spy
        poller.dispatch_fn = fake_claudem_dispatch

        with patch("orchestration.task_poller.subprocess.run") as mock_subprocess:
            poller.poll_and_dispatch()

        # subprocess.run should NOT be called — claudem dispatch_fn handles it
        mock_subprocess.assert_not_called()
        assert len(dispatch_called_with) == 1
        assert dispatch_called_with[0][0] == "claudem"

    @patch.dict("os.environ", {}, clear=False)
    def test_poller_dispatch_fn_is_none_without_minimax_key(self, monkeypatch):
        """Without MINIMAX_API_KEY, dispatch_fn stays None (uses inline subprocess)."""
        monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = []

        poller = TaskPoller(board_id="board-123", client=mock_client)
        assert poller.dispatch_fn is None


class TestMissionControlBackendService:
    """Tests for in-process Mission Control backend + poller runtime."""

    def test_is_enabled_defaults_to_false_for_unset_or_blank(self):
        """Unset/blank env should not implicitly enable poller."""
        from orchestration import mc_backend_service

        assert mc_backend_service._is_enabled(None) is False
        assert mc_backend_service._is_enabled("") is False
        assert mc_backend_service._is_enabled("   ") is False

    def test_is_enabled_accepts_truthy_values(self):
        """Common truthy values enable poller."""
        from orchestration import mc_backend_service

        assert mc_backend_service._is_enabled("1") is True
        assert mc_backend_service._is_enabled("true") is True
        assert mc_backend_service._is_enabled("yes") is True
        assert mc_backend_service._is_enabled("on") is True

    @patch.dict(
        "os.environ",
        {
            "MISSION_CONTROL_IN_PROCESS_POLLER": "1",
            "MISSION_CONTROL_BOARD_ID": "board-123",
            "MISSION_CONTROL_TOKEN": "tok",
            "MISSION_CONTROL_BASE_URL": "http://localhost:9010",
        },
        clear=True,
    )
    def test_run_service_starts_poller_before_uvicorn(self):
        """Service should start poller lane first, then boot API server."""
        from orchestration import mc_backend_service

        call_order: list[tuple] = []

        with patch.object(
            mc_backend_service,
            "start_in_process_task_poller",
            side_effect=lambda board_id, poll_interval_seconds=None: call_order.append(
                ("poller", board_id, poll_interval_seconds)
            ),
        ):
            with patch.object(
                mc_backend_service,
                "_run_uvicorn",
                side_effect=lambda app, host, port: call_order.append(
                    ("uvicorn", app, host, port)
                ),
            ):
                mc_backend_service.run_service(app="app.main:app", host="127.0.0.1", port=9010)

        assert call_order[0] == ("poller", "board-123", None)
        assert call_order[1] == ("uvicorn", "app.main:app", "127.0.0.1", 9010)

    @patch.dict(
        "os.environ",
        {
            "MISSION_CONTROL_IN_PROCESS_POLLER": "1",
            "MISSION_CONTROL_TOKEN": "tok",
            "MISSION_CONTROL_BASE_URL": "http://localhost:9010",
        },
        clear=True,
    )
    def test_run_service_requires_board_id_when_poller_enabled(self):
        """Fail fast when poller is enabled but board id is missing."""
        from orchestration import mc_backend_service

        with patch.object(mc_backend_service, "_run_uvicorn") as mock_uvicorn:
            with pytest.raises(RuntimeError, match="MISSION_CONTROL_BOARD_ID"):
                mc_backend_service.run_service(app="app.main:app", host="127.0.0.1", port=9010)

        mock_uvicorn.assert_not_called()

    @patch.dict(
        "os.environ",
        {
            "MISSION_CONTROL_IN_PROCESS_POLLER": "0",
        },
        clear=True,
    )
    def test_run_service_can_disable_poller_via_env(self):
        """Disable switch allows backend-only mode for break-glass cases."""
        from orchestration import mc_backend_service

        with patch.object(mc_backend_service, "start_in_process_task_poller") as mock_start:
            with patch.object(mc_backend_service, "_run_uvicorn") as mock_uvicorn:
                mc_backend_service.run_service(app="app.main:app", host="127.0.0.1", port=9010)

        mock_start.assert_not_called()
        mock_uvicorn.assert_called_once_with("app.main:app", "127.0.0.1", 9010)

    @patch.dict(
        "os.environ",
        {
            "MISSION_CONTROL_TOKEN": "tok",
            "MISSION_CONTROL_BASE_URL": "http://localhost:9010",
        },
        clear=True,
    )
    def test_run_service_defaults_to_backend_only_when_poller_env_unset(self):
        """Without opt-in env, service should run backend without poller."""
        from orchestration import mc_backend_service

        with patch.object(mc_backend_service, "start_in_process_task_poller") as mock_start:
            with patch.object(mc_backend_service, "_run_uvicorn") as mock_uvicorn:
                mc_backend_service.run_service(app="app.main:app", host="127.0.0.1", port=9010)

        mock_start.assert_not_called()
        mock_uvicorn.assert_called_once_with("app.main:app", "127.0.0.1", 9010)

    def test_start_in_process_task_poller_builds_and_starts_thread(self):
        """Thread wrapper should create TaskPoller and start a daemon thread."""
        from orchestration import mc_backend_service

        fake_client = MagicMock()
        fake_client.is_configured = True
        fake_thread = MagicMock()

        with patch.object(mc_backend_service, "MissionControlClient", return_value=fake_client):
            with patch.object(mc_backend_service, "TaskPoller") as mock_poller_cls:
                with patch.object(mc_backend_service.threading, "Thread", return_value=fake_thread):
                    result = mc_backend_service.start_in_process_task_poller(
                        board_id="board-123",
                        poll_interval_seconds=45,
                    )

        mock_poller_cls.assert_called_once_with(
            board_id="board-123",
            client=fake_client,
            poll_interval_seconds=45,
        )
        fake_thread.start.assert_called_once()
        assert result is fake_thread

    def test_start_in_process_task_poller_requires_configured_client(self):
        """Fail fast if MC client is not configured in environment."""
        from orchestration import mc_backend_service

        fake_client = MagicMock()
        fake_client.is_configured = False

        with patch.object(mc_backend_service, "MissionControlClient", return_value=fake_client):
            with pytest.raises(RuntimeError, match="Mission Control not configured"):
                mc_backend_service.start_in_process_task_poller(board_id="board-123")
