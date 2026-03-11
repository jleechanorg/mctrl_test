from __future__ import annotations

from pathlib import Path
import subprocess
from unittest.mock import MagicMock, Mock

import pytest

from orchestration.reconciliation import (
    _remote_branch_exists,
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

        emitted = reconcile_registry_once(
            registry_path=str(registry),
            outbox_path=str(outbox),
            dead_letter_path=str(tmp_path / "dead_letter.jsonl"),
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
            dead_letter_path=str(tmp_path / "dead_letter.jsonl"),
        )

        assert emitted == []
        found = get_mapping("ORCH-456", registry_path=str(registry))
        assert found is not None
        assert found.status == "in_progress"

    def test_missing_session_with_local_only_commits_transitions_to_needs_human(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        registry = tmp_path / "registry.jsonl"
        outbox = tmp_path / "outbox.jsonl"

        upsert_mapping(
            BeadSessionMapping.create(
                bead_id="ORCH-local-only",
                session_name="session-local-only",
                worktree_path="/tmp/wt-local-only",
                branch="feat/local-only",
                agent_cli="codex",
                status="in_progress",
                start_sha="abc123",
            ),
            registry_path=str(registry),
        )
        monkeypatch.setattr(
            "orchestration.reconciliation.run_tmux_sessions",
            lambda: set(),
        )
        monkeypatch.setattr(
            "orchestration.reconciliation._worktree_has_commits",
            lambda *_args, **_kwargs: True,
        )
        monkeypatch.setattr(
            "orchestration.reconciliation._remote_branch_exists",
            lambda *_args, **_kwargs: False,
        )
        monkeypatch.setattr("orchestration.reconciliation.notify_openclaw", lambda p, *, outbox_path: True)

        emitted = reconcile_registry_once(
            registry_path=str(registry),
            outbox_path=str(outbox),
            dead_letter_path=str(tmp_path / "dead_letter.jsonl"),
        )

        assert len(emitted) == 1
        assert emitted[0]["event"] == "task_needs_human"
        assert emitted[0]["action_required"] == "push_or_salvage"
        assert "did not push" in emitted[0]["summary"]

        found = get_mapping("ORCH-local-only", registry_path=str(registry))
        assert found is not None
        assert found.status == "needs_human"

    def test_missing_session_with_remote_branch_transitions_to_finished(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        registry = tmp_path / "registry.jsonl"
        outbox = tmp_path / "outbox.jsonl"

        upsert_mapping(
            BeadSessionMapping.create(
                bead_id="ORCH-remote-ok",
                session_name="session-remote-ok",
                worktree_path="/tmp/wt-remote-ok",
                branch="feat/remote-ok",
                agent_cli="claude",
                status="in_progress",
                start_sha="abc123",
            ),
            registry_path=str(registry),
        )
        monkeypatch.setattr(
            "orchestration.reconciliation.run_tmux_sessions",
            lambda: set(),
        )
        monkeypatch.setattr(
            "orchestration.reconciliation._worktree_has_commits",
            lambda *_args, **_kwargs: True,
        )
        monkeypatch.setattr(
            "orchestration.reconciliation._remote_branch_exists",
            lambda *_args, **_kwargs: True,
        )
        monkeypatch.setattr("orchestration.reconciliation.notify_openclaw", lambda p, *, outbox_path: True)

        emitted = reconcile_registry_once(
            registry_path=str(registry),
            outbox_path=str(outbox),
            dead_letter_path=str(tmp_path / "dead_letter.jsonl"),
        )

        assert len(emitted) == 1
        assert emitted[0]["event"] == "task_finished"
        assert emitted[0]["action_required"] == "review_and_merge"

        found = get_mapping("ORCH-remote-ok", registry_path=str(registry))
        assert found is not None
        assert found.status == "finished"


class TestRemoteBranchExists:
    def test_returns_false_when_origin_branch_does_not_contain_local_head(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        calls: list[list[str]] = []

        def fake_run(args, **kwargs):
            calls.append(args)
            if args[:4] == ["git", "fetch", "--no-tags", "origin"]:
                return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")
            if args == ["git", "rev-parse", "--verify", "origin/feat/demo"]:
                return subprocess.CompletedProcess(
                    args=args, returncode=0, stdout="deadbeef\n", stderr=""
                )
            if args == ["git", "merge-base", "--is-ancestor", "HEAD", "origin/feat/demo"]:
                return subprocess.CompletedProcess(args=args, returncode=1, stdout="", stderr="")
            raise AssertionError(f"unexpected subprocess call: {args}")

        monkeypatch.setattr(subprocess, "run", fake_run)

        assert _remote_branch_exists("feat/demo", "/tmp/wt-demo") is False
        assert calls == [
            ["git", "fetch", "--no-tags", "origin", "feat/demo"],
            ["git", "rev-parse", "--verify", "origin/feat/demo"],
            ["git", "merge-base", "--is-ancestor", "HEAD", "origin/feat/demo"],
        ]

    def test_returns_true_when_origin_branch_contains_local_head(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def fake_run(args, **kwargs):
            if args[:4] == ["git", "fetch", "--no-tags", "origin"]:
                return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")
            if args == ["git", "rev-parse", "--verify", "origin/feat/demo"]:
                return subprocess.CompletedProcess(
                    args=args, returncode=0, stdout="deadbeef\n", stderr=""
                )
            if args == ["git", "merge-base", "--is-ancestor", "HEAD", "origin/feat/demo"]:
                return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")
            raise AssertionError(f"unexpected subprocess call: {args}")

        monkeypatch.setattr(subprocess, "run", fake_run)

        assert _remote_branch_exists("feat/demo", "/tmp/wt-demo") is True

    def test_returns_none_when_remote_verification_fails_transiently(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def fake_run(args, **kwargs):
            if args[:4] == ["git", "fetch", "--no-tags", "origin"]:
                return subprocess.CompletedProcess(
                    args=args, returncode=128, stdout="", stderr="network timeout"
                )
            raise AssertionError(f"unexpected subprocess call: {args}")

        monkeypatch.setattr(subprocess, "run", fake_run)

        assert _remote_branch_exists("feat/demo", "/tmp/wt-demo") is None


def test_reconcile_leaves_in_progress_when_remote_check_is_transient_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = tmp_path / "registry.jsonl"
    outbox = tmp_path / "outbox.jsonl"
    mapping = BeadSessionMapping.create(
        bead_id="ORCH-remote-unknown",
        session_name="ai-test-missing",
        worktree_path="/tmp/wt-demo",
        branch="feat/demo",
        agent_cli="claude",
        status="in_progress",
        start_sha="abc123",
        slack_trigger_ts="",
    )
    upsert_mapping(mapping, registry_path=str(registry))

    monkeypatch.setattr(
        "orchestration.reconciliation.run_tmux_sessions",
        lambda: set(),
    )
    monkeypatch.setattr(
        "orchestration.reconciliation._worktree_has_commits",
        lambda *_args, **_kwargs: True,
    )
    monkeypatch.setattr(
        "orchestration.reconciliation._remote_branch_exists",
        lambda *_args, **_kwargs: None,
    )
    notify_openclaw = MagicMock(return_value=True)
    monkeypatch.setattr("orchestration.reconciliation.notify_openclaw", notify_openclaw)

    emitted = reconcile_registry_once(
        registry_path=str(registry),
        outbox_path=str(outbox),
        dead_letter_path=str(tmp_path / "dead_letter.jsonl"),
    )

    assert emitted == []
    found = get_mapping("ORCH-remote-unknown", registry_path=str(registry))
    assert found is not None
    assert found.status == "in_progress"
    notify_openclaw.assert_not_called()
