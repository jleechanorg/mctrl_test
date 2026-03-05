"""Tests for orchestration.task_poller — Task polling and dispatch."""

from __future__ import annotations

import threading
from unittest.mock import patch, MagicMock, call

from orchestration.task_poller import (
    TaskPoller,
    _extract_token_usage,
)
from orchestration.mc_client import TaskStatus


class TestExtractTokenUsage:
    def test_json_payload(self):
        data = b'{"input_tokens": 10, "output_tokens": 20, "total_tokens": 30}'
        assert _extract_token_usage(data) == {
            "input_tokens": 10,
            "output_tokens": 20,
            "total_tokens": 30,
        }

    def test_empty(self):
        assert _extract_token_usage(None) == {}
        assert _extract_token_usage(b"") == {}

    def test_regex_fallback(self):
        text = "Input tokens: 5\nOutput tokens: 10\nTotal tokens: 15"
        result = _extract_token_usage(text)
        assert result["input_tokens"] == 5
        assert result["output_tokens"] == 10
        assert result["total_tokens"] == 15



class TestTaskPoller:
    """Tests for TaskPoller class."""

    def test_default_agent_cli_is_none(self):
        """agent_cli defaults to None — ai_orch decides the CLI."""
        mock_client = MagicMock()
        poller = TaskPoller(board_id="board-123", client=mock_client)
        assert poller.agent_cli is None

    def test_poll_and_dispatch_empty_tasks(self):
        mock_client = MagicMock()
        mock_client.list_inbox_tasks.return_value = []
        mock_client.is_configured = True

        poller = TaskPoller(board_id="board-123", client=mock_client)
        result = poller.poll_and_dispatch()

        assert result == 0
        mock_client.list_inbox_tasks.assert_called_once_with("board-123")

    def test_poll_and_dispatch_single_task(self):
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.update_task.return_value = {"id": "task-1", "status": "done"}
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Test task", "description": "Do work"}
        ]

        poller = TaskPoller(board_id="board-123", client=mock_client)

        with patch.object(poller, "_dispatch_via_ai_orch", return_value=(True, {})):
            result = poller.poll_and_dispatch()

        assert result == 1
        mock_client.update_task.assert_has_calls([
            call("task-1", TaskStatus.IN_PROGRESS, custom_fields=None, board_id="board-123"),
            call("task-1", TaskStatus.DONE, board_id="board-123"),
        ])
        assert mock_client.update_task.call_count == 2

    def test_poll_and_dispatch_multiple_tasks(self):
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.update_task.return_value = {"id": "ok", "status": "done"}
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Task 1", "description": "Work 1"},
            {"id": "task-2", "title": "Task 2", "description": "Work 2"},
            {"id": "task-3", "title": "Task 3", "description": "Work 3"},
        ]

        poller = TaskPoller(board_id="board-123", client=mock_client)

        with patch.object(poller, "_dispatch_via_ai_orch", return_value=(True, {})):
            result = poller.poll_and_dispatch()

        assert result == 3
        # 2 update_task calls per task (in_progress + done)
        assert mock_client.update_task.call_count == 6

    def test_poll_and_dispatch_concurrent(self):
        """With dispatch_concurrency > 1, task dispatches overlap in time."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.update_task.return_value = {"id": "ok", "status": "in_progress"}
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Task 1", "description": "Work 1"},
            {"id": "task-2", "title": "Task 2", "description": "Work 2"},
        ]

        poller = TaskPoller(board_id="board-123", client=mock_client, dispatch_concurrency=2)

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

    def test_poll_and_dispatch_skips_task_without_id(self):
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.update_task.return_value = {"id": "task-2", "status": "in_progress"}
        mock_client.list_inbox_tasks.return_value = [
            {"title": "Task without id"},
            {"id": "task-2", "title": "Task 2", "description": "Work"},
        ]

        poller = TaskPoller(board_id="board-123", client=mock_client)

        with patch.object(poller, "_dispatch_via_ai_orch", return_value=(True, {})):
            result = poller.poll_and_dispatch()

        assert result >= 1

    def test_poll_and_dispatch_skips_unapproved_task(self):
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.update_task.return_value = {"id": "task-2", "status": "in_progress"}
        mock_client.list_inbox_tasks.return_value = [
            {
                "id": "task-1",
                "title": "Pending approval",
                "approval_required": True,
                "approved_at": None,
            },
            {
                "id": "task-2",
                "title": "Approved task",
                "description": "Work",
                "approval_required": True,
                "approved_at": "2026-03-02T00:00:00Z",
            },
        ]

        poller = TaskPoller(board_id="board-123", client=mock_client)

        with patch.object(poller, "_dispatch_via_ai_orch", return_value=(True, {})) as mock_dispatch:
            result = poller.poll_and_dispatch()

        assert result == 1
        assert mock_dispatch.call_count == 1

    def test_poll_returns_zero_when_not_configured(self):
        mock_client = MagicMock()
        mock_client.is_configured = False

        poller = TaskPoller(board_id="board-123", client=mock_client)
        result = poller.poll_and_dispatch()

        assert result == 0
        mock_client.list_inbox_tasks.assert_not_called()

    def test_in_progress_update_failure_returns_false(self):
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Test", "description": "work"},
        ]
        mock_client.update_task.return_value = {}  # falsy = rejected

        poller = TaskPoller(board_id="board-123", client=mock_client)

        with patch.object(poller, "_dispatch_via_ai_orch", return_value=(True, {})):
            result = poller.poll_and_dispatch()

        assert result == 0

    def test_in_progress_update_rejection_returns_false(self):
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Test", "description": "work"},
        ]
        mock_client.update_task.return_value = {}

        poller = TaskPoller(board_id="board-123", client=mock_client)

        with patch.object(poller, "_dispatch_via_ai_orch", return_value=(True, {})):
            result = poller.poll_and_dispatch()

        assert result == 0

    def test_dispatch_fn_tuple_with_token_cost(self):
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Test", "description": "work"},
        ]
        mock_client.update_task.return_value = {"id": "task-1", "status": "in_progress"}

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
            dispatch_fn=lambda cli, task: (True, {"input_tokens": 5}),
        )

        result = poller.poll_and_dispatch()

        assert result == 1
        mock_client.update_task.assert_any_call(
            "task-1",
            TaskStatus.IN_PROGRESS,
            custom_fields={"cost": {"input_tokens": 5}},
            board_id="board-123",
        )

    def test_dispatch_fn_dict_payload(self):
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Test", "description": "work"},
        ]
        mock_client.update_task.return_value = {"id": "task-1", "status": "in_progress"}

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
            dispatch_fn=lambda cli, task: {"success": True, "token_usage": {"total_tokens": 9}},
        )

        result = poller.poll_and_dispatch()

        assert result == 1
        mock_client.update_task.assert_any_call(
            "task-1",
            TaskStatus.IN_PROGRESS,
            custom_fields={"cost": {"total_tokens": 9}},
            board_id="board-123",
        )

    def test_optional_client_created_from_env(self):
        with patch("orchestration.task_poller.MissionControlClient") as MockClient:
            mock_instance = MagicMock()
            MockClient.return_value = mock_instance
            poller = TaskPoller(board_id="board-123")
            MockClient.assert_called_once()
            assert poller.client is mock_instance


class TestDecomposeTask:
    def test_creates_subtasks_with_dependencies(self):
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
            "title": "Parent",
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
            "sub-2", ["manual", "sub-1"], board_id="board-123",
        )
        mock_client.set_task_dependencies.assert_any_call(
            "sub-3", ["sub-2"], board_id="board-123",
        )

    def test_blocks_parent_when_subtasks_created(self):
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.update_task.return_value = {"id": "task-1", "status": "blocked"}
        mock_client.create_task.side_effect = [{"id": "sub-1"}, {"id": "sub-2"}]

        poller = TaskPoller(board_id="board-123", client=mock_client)

        task = {
            "id": "task-1",
            "title": "Parent",
            "subtasks": [
                {"title": "A", "description": "a"},
                {"title": "B", "description": "b"},
            ],
        }

        result = poller._dispatch_task(task)

        assert result is True
        mock_client.update_task.assert_called_once_with(
            "task-1", TaskStatus.BLOCKED, board_id="board-123",
        )

    def test_no_subtasks_returns_empty(self):
        mock_client = MagicMock()
        mock_client.is_configured = True
        poller = TaskPoller(board_id="board-123", client=mock_client)

        assert poller.decompose_task({"id": "t1", "title": "no subs"}) == []
        assert poller.decompose_task({"id": "t1", "subtasks": []}) == []


class TestDispatchViaAiOrch:
    def test_success_returns_true_and_tokens(self):
        mock_client = MagicMock()
        mock_client.is_configured = True
        poller = TaskPoller(board_id="board-123", client=mock_client)

        with patch("orchestration.task_poller.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = b'{"input_tokens": 10, "output_tokens": 20, "total_tokens": 30}'
            dispatched, tokens = poller._dispatch_via_ai_orch("do work", "task-1")

        assert dispatched is True
        assert tokens == {"input_tokens": 10, "output_tokens": 20, "total_tokens": 30}

    def test_calls_ai_orch_run_default(self):
        """Default command has no --agent-cli when agent_cli is None."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        poller = TaskPoller(board_id="board-123", client=mock_client)

        with patch("orchestration.task_poller.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = b""
            poller._dispatch_via_ai_orch("do the thing", "task-1")
            cmd = mock_run.call_args[0][0]

        assert cmd == ["ai_orch", "run", "--", "do the thing"]

    def test_ai_orch_with_all_params(self):
        """All ai_orch params are passed through to the command."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
            agent_cli="codex",
            model="opus",
            async_dispatch=True,
            resume=True,
            worktree=True,
        )

        with patch("orchestration.task_poller.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = b""
            poller._dispatch_via_ai_orch("do work", "task-1")
            cmd = mock_run.call_args[0][0]

        assert cmd == [
            "ai_orch", "run",
            "--agent-cli", "codex",
            "--model", "opus",
            "--async",
            "--resume",
            "--worktree",
            "--", "do work",
        ]

    def test_inherits_env_lets_ai_orch_handle_stripping(self):
        """ai_orch handles CLAUDECODE stripping — task poller does not pass explicit env."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        poller = TaskPoller(board_id="board-123", client=mock_client)

        with patch("orchestration.task_poller.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = b""
            poller._dispatch_via_ai_orch("work", "task-1")

        # No explicit env= kwarg — inherits parent env, ai_orch handles the rest
        assert "env" not in mock_run.call_args[1]

    def test_nonzero_exit_returns_false(self):
        mock_client = MagicMock()
        mock_client.is_configured = True
        poller = TaskPoller(board_id="board-123", client=mock_client)

        with patch("orchestration.task_poller.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = b""
            dispatched, _ = poller._dispatch_via_ai_orch("work", "task-1")

        assert dispatched is False

    def test_timeout_returns_false(self):
        mock_client = MagicMock()
        mock_client.is_configured = True
        poller = TaskPoller(board_id="board-123", client=mock_client)

        import subprocess as sp
        with patch("orchestration.task_poller.subprocess.run", side_effect=sp.TimeoutExpired("cmd", 300)):
            dispatched, _ = poller._dispatch_via_ai_orch("work", "task-1")

        assert dispatched is False

    def test_file_not_found_returns_false(self):
        mock_client = MagicMock()
        mock_client.is_configured = True
        poller = TaskPoller(board_id="board-123", client=mock_client)

        with patch("orchestration.task_poller.subprocess.run", side_effect=FileNotFoundError):
            dispatched, _ = poller._dispatch_via_ai_orch("work", "task-1")

        assert dispatched is False


class TestAsyncDispatchSemantics:
    """Tests for ORCH-238: async_dispatch skips DONE, sync marks DONE."""

    def test_async_dispatch_skips_done(self):
        """When async_dispatch=True, task stays IN_PROGRESS (no DONE)."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Test", "description": "work"},
        ]
        mock_client.update_task.return_value = {"id": "task-1", "status": "in_progress"}

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
            async_dispatch=True,
        )

        with patch.object(poller, "_dispatch_via_ai_orch", return_value=(True, {})):
            result = poller.poll_and_dispatch()

        assert result == 1
        # Only IN_PROGRESS — no DONE call
        mock_client.update_task.assert_called_once_with(
            "task-1", TaskStatus.IN_PROGRESS, custom_fields=None, board_id="board-123",
        )

    def test_sync_dispatch_marks_done(self):
        """When async_dispatch=False (default), task transitions to DONE."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Test", "description": "work"},
        ]
        mock_client.update_task.return_value = {"id": "task-1", "status": "done"}

        poller = TaskPoller(board_id="board-123", client=mock_client)

        with patch.object(poller, "_dispatch_via_ai_orch", return_value=(True, {})):
            result = poller.poll_and_dispatch()

        assert result == 1
        mock_client.update_task.assert_has_calls([
            call("task-1", TaskStatus.IN_PROGRESS, custom_fields=None, board_id="board-123"),
            call("task-1", TaskStatus.DONE, board_id="board-123"),
        ])
        assert mock_client.update_task.call_count == 2

    def test_async_dispatch_with_dispatch_fn(self):
        """dispatch_fn + async_dispatch=True also skips DONE."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = [
            {"id": "task-1", "title": "Test", "description": "work"},
        ]
        mock_client.update_task.return_value = {"id": "task-1", "status": "in_progress"}

        poller = TaskPoller(
            board_id="board-123",
            client=mock_client,
            async_dispatch=True,
            dispatch_fn=lambda cli, task: True,
        )

        result = poller.poll_and_dispatch()

        assert result == 1
        mock_client.update_task.assert_called_once_with(
            "task-1", TaskStatus.IN_PROGRESS, custom_fields=None, board_id="board-123",
        )


class TestRunMethods:
    def test_run_once(self):
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.list_inbox_tasks.return_value = []

        poller = TaskPoller(board_id="board-123", client=mock_client)
        result = poller.run_once()

        assert result == 0
        mock_client.list_inbox_tasks.assert_called_once()

    def test_run_forever_exists_and_callable(self):
        mock_client = MagicMock()
        poller = TaskPoller(board_id="board-123", client=mock_client, poll_interval_seconds=1)

        assert hasattr(poller, "run_forever")
        assert callable(poller.run_forever)
        assert poller.poll_interval_seconds == 1
