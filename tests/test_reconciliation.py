from __future__ import annotations

from pathlib import Path
import subprocess
from unittest.mock import Mock

import pytest

from orchestration.reconciliation import (
    reconcile_registry_once,
    run_tmux_sessions,
)
from orchestration.session_registry import BeadSessionMapping, get_mapping, upsert_mapping


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


class TestReconcileRegistryOnce:
    def test_missing_session_transitions_to_needs_human_and_emits(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        registry = tmp_path / "registry.jsonl"
        outbox = tmp_path / "outbox.jsonl"

        upsert_mapping(
            BeadSessionMapping.create(
                bead_id="ORCH-123",
                session_name="session-123",
                worktree_path="/tmp/wt-123",
                branch="feat/orch-123",
                agent_cli="codex",
                status="in_progress",
            ),
            registry_path=str(registry),
        )
        monkeypatch.setattr(
            "orchestration.reconciliation.run_tmux_sessions",
            lambda: set(),
        )
        # Stub network calls — unit tests must not post real Slack or OpenClaw messages.
        monkeypatch.setattr("orchestration.reconciliation.notify_openclaw", lambda p, *, outbox_path: True)
        monkeypatch.setattr("orchestration.reconciliation.notify_slack_done", lambda p: True)

        emitted = reconcile_registry_once(
            registry_path=str(registry),
            outbox_path=str(outbox),
        )

        assert len(emitted) == 1
        assert emitted[0]["event"] == "task_needs_human"
        assert emitted[0]["bead_id"] == "ORCH-123"

        found = get_mapping("ORCH-123", registry_path=str(registry))
        assert found is not None
        assert found.status == "needs_human"

    def test_active_session_keeps_status_and_emits_nothing(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        registry = tmp_path / "registry.jsonl"
        outbox = tmp_path / "outbox.jsonl"

        upsert_mapping(
            BeadSessionMapping.create(
                bead_id="ORCH-456",
                session_name="session-456",
                worktree_path="/tmp/wt-456",
                branch="feat/orch-456",
                agent_cli="claude",
                status="in_progress",
            ),
            registry_path=str(registry),
        )
        monkeypatch.setattr(
            "orchestration.reconciliation.run_tmux_sessions",
            lambda: {"session-456"},
        )

        emitted = reconcile_registry_once(
            registry_path=str(registry),
            outbox_path=str(outbox),
        )

        assert emitted == []
        found = get_mapping("ORCH-456", registry_path=str(registry))
        assert found is not None
        assert found.status == "in_progress"
