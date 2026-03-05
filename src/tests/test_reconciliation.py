from __future__ import annotations

import subprocess
from unittest.mock import Mock, patch

import pytest

from orchestration.reconciliation import (
    get_stuck_tasks,
    reconcile_once,
    run_tmux_sessions,
)


class TestGetStuckTasks:
    def test_returns_tasks_with_no_matching_session(self) -> None:
        client = Mock()
        client.list_tasks.return_value = [
            {"id": "T-1", "title": "task one"},
            {"id": "T-2", "title": "task two"},
        ]
        # Only T-1 appears in a session name
        active_sessions = {"session-T-1-abc", "unrelated-session"}

        stuck = get_stuck_tasks(client, board_id="board-1", active_sessions=active_sessions)

        assert len(stuck) == 1
        assert stuck[0]["id"] == "T-2"

    def test_returns_empty_when_all_tasks_have_sessions(self) -> None:
        client = Mock()
        client.list_tasks.return_value = [
            {"id": "T-1", "title": "task one"},
            {"id": "T-2", "title": "task two"},
        ]
        active_sessions = {"session-T-1-abc", "session-T-2-xyz"}

        stuck = get_stuck_tasks(client, board_id="board-1", active_sessions=active_sessions)

        assert stuck == []

    def test_calls_list_tasks_with_in_progress_status(self) -> None:
        client = Mock()
        client.list_tasks.return_value = []

        get_stuck_tasks(client, board_id="board-42", active_sessions=set())

        client.list_tasks.assert_called_once_with("board-42", status="in_progress")

    def test_returns_empty_when_no_tasks(self) -> None:
        client = Mock()
        client.list_tasks.return_value = []

        stuck = get_stuck_tasks(client, board_id="board-1", active_sessions={"some-session"})

        assert stuck == []


class TestRunTmuxSessions:
    def test_returns_empty_set_when_tmux_not_running(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def fake_run(*_args, **_kwargs):
            raise FileNotFoundError("tmux not found")

        monkeypatch.setattr(subprocess, "run", fake_run)

        sessions = run_tmux_sessions()

        assert sessions == set()

    def test_returns_empty_set_when_tmux_times_out(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def fake_run(*_args, **_kwargs):
            raise subprocess.TimeoutExpired(cmd=["tmux"], timeout=10)

        monkeypatch.setattr(subprocess, "run", fake_run)

        sessions = run_tmux_sessions()

        assert sessions == set()

    def test_returns_empty_set_when_tmux_returns_nonzero(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def fake_run(*_args, **_kwargs):
            return subprocess.CompletedProcess(
                args=["tmux"], returncode=1, stdout="", stderr="no server running"
            )

        monkeypatch.setattr(subprocess, "run", fake_run)

        sessions = run_tmux_sessions()

        assert sessions == set()

    def test_parses_session_names_from_output(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def fake_run(*_args, **_kwargs):
            return subprocess.CompletedProcess(
                args=["tmux"], returncode=0, stdout="session-T-1\nsession-T-2\n", stderr=""
            )

        monkeypatch.setattr(subprocess, "run", fake_run)

        sessions = run_tmux_sessions()

        assert sessions == {"session-T-1", "session-T-2"}


class TestReconcileOnce:
    def test_returns_stuck_task_ids(self, monkeypatch: pytest.MonkeyPatch) -> None:
        client = Mock()
        client.list_tasks.return_value = [
            {"id": "T-1", "title": "task one"},
            {"id": "T-2", "title": "task two"},
        ]
        # T-1 has a session, T-2 does not
        monkeypatch.setattr(
            "orchestration.reconciliation.run_tmux_sessions",
            lambda: {"session-T-1-abc"},
        )

        result = reconcile_once(client, board_id="board-1")

        assert result == ["T-2"]

    def test_does_not_call_update_task(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify human review is required — reconcile_once must never auto-transition tasks."""
        client = Mock()
        client.list_tasks.return_value = [
            {"id": "T-99", "title": "stuck task"},
        ]
        monkeypatch.setattr(
            "orchestration.reconciliation.run_tmux_sessions",
            lambda: set(),
        )

        reconcile_once(client, board_id="board-1")

        client.update_task.assert_not_called()

    def test_returns_empty_when_no_stuck_tasks(self, monkeypatch: pytest.MonkeyPatch) -> None:
        client = Mock()
        client.list_tasks.return_value = [
            {"id": "T-1", "title": "task one"},
        ]
        monkeypatch.setattr(
            "orchestration.reconciliation.run_tmux_sessions",
            lambda: {"session-T-1-running"},
        )

        result = reconcile_once(client, board_id="board-1")

        assert result == []
