"""TDD tests for worktree reuse logic in dispatch_task.

find_existing_worktree(branch, repo_root) — scans git worktree list,
returns path if branch already checked out, None otherwise.

resolve_worktree_for_branch(branch, repo_root, bead_worktree_base) —
returns (path, is_new):
  - existing worktree → (path, False)
  - branch on remote but not in any worktree → checkout fresh, (path, True)
  - branch missing everywhere → raises ValueError
"""
from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path
from unittest.mock import ANY, MagicMock, patch

import pytest

from orchestration.dispatch_task import find_existing_worktree, resolve_worktree_for_branch


# ---------------------------------------------------------------------------
# find_existing_worktree
# ---------------------------------------------------------------------------

PORCELAIN_TWO_WORKTREES = textwrap.dedent("""\
    worktree /Users/jleechan/project_jleechanclaw/mctrl
    HEAD abc123
    branch refs/heads/main

    worktree /tmp/wt-feat-xyz
    HEAD def456
    branch refs/heads/feat/xyz

    worktree /tmp/wt-fix-abc
    HEAD 789abc
    branch refs/heads/fix/abc

""")


def _mock_wt_list(stdout: str, returncode: int = 0):
    m = MagicMock()
    m.stdout = stdout
    m.returncode = returncode
    return m


def test_find_existing_worktree_found():
    with patch("subprocess.run", return_value=_mock_wt_list(PORCELAIN_TWO_WORKTREES)):
        result = find_existing_worktree("feat/xyz", repo_root="/repo")
    assert result == "/tmp/wt-feat-xyz"


def test_find_existing_worktree_not_found():
    with patch("subprocess.run", return_value=_mock_wt_list(PORCELAIN_TWO_WORKTREES)):
        result = find_existing_worktree("feat/does-not-exist", repo_root="/repo")
    assert result is None


def test_find_existing_worktree_skips_main_worktree():
    """The primary worktree (first block) must not be returned even if branch matches."""
    porcelain = textwrap.dedent("""\
        worktree /Users/jleechan/project_jleechanclaw/mctrl
        HEAD abc123
        branch refs/heads/feat/xyz

    """)
    with patch("subprocess.run", return_value=_mock_wt_list(porcelain)):
        result = find_existing_worktree("feat/xyz", repo_root="/Users/jleechan/project_jleechanclaw/mctrl")
    # Primary worktree is the repo root — should not dispatch into it
    assert result is None


def test_find_existing_worktree_bare_or_detached():
    """Detached HEAD blocks (no 'branch' line) must not crash."""
    porcelain = textwrap.dedent("""\
        worktree /tmp/wt-detached
        HEAD deadbeef
        detached

    """)
    with patch("subprocess.run", return_value=_mock_wt_list(porcelain)):
        result = find_existing_worktree("feat/xyz", repo_root="/repo")
    assert result is None


def test_find_existing_worktree_git_failure_returns_none():
    """If git worktree list fails, return None gracefully (don't crash dispatch)."""
    with patch("subprocess.run", return_value=_mock_wt_list("", returncode=1)):
        result = find_existing_worktree("feat/xyz", repo_root="/repo")
    assert result is None


def test_find_existing_worktree_flushes_last_block_without_trailing_blank():
    """The final porcelain block should still be checked without a blank terminator."""
    porcelain = textwrap.dedent("""\
        worktree /tmp/wt-feat-xyz
        HEAD def456
        branch refs/heads/feat/xyz
    """)
    with patch("subprocess.run", return_value=_mock_wt_list(porcelain)):
        result = find_existing_worktree("feat/xyz", repo_root="/repo")
    assert result == "/tmp/wt-feat-xyz"


# ---------------------------------------------------------------------------
# resolve_worktree_for_branch
# ---------------------------------------------------------------------------

def test_resolve_returns_existing_worktree(tmp_path: Path):
    """If branch already in a worktree, return it without creating a new one."""
    with patch("orchestration.dispatch_task.find_existing_worktree", return_value="/tmp/wt-feat-xyz"):
        path, is_new = resolve_worktree_for_branch(
            branch="feat/xyz",
            repo_root=str(tmp_path),
            worktree_base="/tmp/mctrl-worktrees",
        )
    assert path == "/tmp/wt-feat-xyz"
    assert is_new is False


def test_resolve_creates_new_worktree_when_none_exists(tmp_path: Path):
    """If branch not in any worktree but exists on remote, checkout fresh."""
    new_wt = str(tmp_path / "wt-new")

    def fake_run(cmd, **kw):
        m = MagicMock()
        m.returncode = 0
        m.stdout = ""
        m.stderr = ""
        return m

    with patch("orchestration.dispatch_task.find_existing_worktree", return_value=None), \
         patch("orchestration.dispatch_task._remote_branch_exists", return_value=True), \
         patch("subprocess.run", side_effect=fake_run), \
         patch("orchestration.dispatch_task._worktree_add_path", return_value=new_wt):
        path, is_new = resolve_worktree_for_branch(
            branch="feat/new-branch",
            repo_root=str(tmp_path),
            worktree_base=str(tmp_path),
        )
    assert path == new_wt
    assert is_new is True


def test_resolve_raises_when_branch_missing_everywhere(tmp_path: Path):
    """If branch not in worktrees and not on remote, raise ValueError."""
    with patch("orchestration.dispatch_task.find_existing_worktree", return_value=None), \
         patch("orchestration.dispatch_task._remote_branch_exists", return_value=False):
        with pytest.raises(ValueError, match="branch.*not found"):
            resolve_worktree_for_branch(
                branch="feat/ghost",
                repo_root=str(tmp_path),
                worktree_base=str(tmp_path),
            )


# ---------------------------------------------------------------------------
# dispatch() with branch= parameter (full round-trip wiring)
# ---------------------------------------------------------------------------

def test_dispatch_fires_slack_started_after_spawn(tmp_path: Path):
    """dispatch() calls notify_slack_started with correct payload after spawning agent."""
    existing_wt = str(tmp_path / "wt")
    fake_output = (
        "🚀 Async session: ai-minimax-start1\n"
        f"🧩 Worktree: {existing_wt} (branch: feat/test)\n"
    )

    def fake_run(cmd, **kw):
        m = MagicMock()
        m.returncode = 0
        m.stdout = fake_output
        m.stderr = ""
        return m

    started_calls: list[dict] = []

    with patch("subprocess.run", side_effect=fake_run), \
         patch("orchestration.dispatch_task.upsert_mapping"), \
         patch("orchestration.dispatch_task.notify_slack_started",
               side_effect=lambda p: started_calls.append(p) or True) as mock_started:
        from orchestration.dispatch_task import dispatch
        dispatch(
            bead_id="ORCH-start-test",
            task="do the thing",
            slack_trigger_ts="1234567890.000",
            agent_cli="minimax",
            registry_path=str(tmp_path / "registry.jsonl"),
        )

    mock_started.assert_called_once()
    payload = started_calls[0]
    assert payload["bead_id"] == "ORCH-start-test"
    assert payload["session"] == "ai-minimax-start1"
    assert payload["event"] == "task_started"
    assert payload["slack_trigger_ts"] == "1234567890.000"
    assert payload["agent_cli"] == "minimax"


def test_dispatch_with_branch_reuses_existing_worktree(tmp_path: Path):
    """dispatch(branch=...) uses existing worktree, runs ai_orch without --worktree."""
    existing_wt = str(tmp_path / "existing-wt")

    fake_output = (
        "🚀 Async session: ai-minimax-abc123\n"
        f"🧩 Worktree: {existing_wt} (branch: feat/mvp-loopback-supervisor)\n"
    )

    def fake_run(cmd, **kw):
        m = MagicMock()
        m.returncode = 0
        m.stdout = fake_output
        m.stderr = ""
        return m

    with patch("orchestration.dispatch_task.resolve_worktree_for_branch",
               return_value=(existing_wt, False)) as mock_resolve, \
         patch("subprocess.run", side_effect=fake_run), \
         patch("orchestration.dispatch_task.upsert_mapping"):
        from orchestration.dispatch_task import dispatch
        mapping = dispatch(
            bead_id="ORCH-test",
            task="fix PR comments",
            branch="feat/mvp-loopback-supervisor",
            repo_root=str(tmp_path),
            registry_path=str(tmp_path / "registry.jsonl"),
        )

    mock_resolve.assert_called_once_with(
        "feat/mvp-loopback-supervisor", str(tmp_path), ANY
    )
    assert mapping.session_name == "ai-minimax-abc123"
    assert mapping.branch == "feat/mvp-loopback-supervisor"


def test_dispatch_without_branch_still_uses_worktree_flag(tmp_path: Path):
    """dispatch() with no branch= still passes --worktree to ai_orch (new task)."""
    fake_output = (
        "🚀 Async session: ai-minimax-newxyz\n"
        f"🧩 Worktree: /tmp/wt-new (branch: feat/new-thing)\n"
    )
    cmd_log = []

    def fake_run(cmd, **kw):
        cmd_log.append(list(cmd))
        m = MagicMock()
        m.returncode = 0
        m.stdout = fake_output
        m.stderr = ""
        return m

    with patch("subprocess.run", side_effect=fake_run), \
         patch("orchestration.dispatch_task.upsert_mapping"):
        from orchestration.dispatch_task import dispatch
        dispatch(
            bead_id="ORCH-test2",
            task="new task",
            registry_path=str(tmp_path / "registry.jsonl"),
        )

    orch_cmd = next((c for c in cmd_log if "ai_orch" in c), None)
    assert orch_cmd is not None
    assert "--worktree" in orch_cmd


def test_worktree_add_path_falls_back_when_branch_in_primary(tmp_path: Path):
    """If git worktree add fails with 'already checked out', detach from origin and switch."""
    call_log = []

    def fake_run(cmd, **kw):
        call_log.append(list(cmd))
        m = MagicMock()
        if "worktree" in cmd and "add" in cmd and "--detach" not in cmd:
            m.returncode = 128
            m.stderr = b"fatal: 'feat/xyz' is already checked out at '/repo'"
        else:
            m.returncode = 0
            m.stderr = b""
            m.stdout = b""
        return m

    with patch("subprocess.run", side_effect=fake_run):
        from orchestration.dispatch_task import _worktree_add_path
        _worktree_add_path("feat/xyz", "/repo", str(tmp_path))

    cmds = [" ".join(c) for c in call_log]
    assert cmds[0] == "git fetch --no-tags origin feat/xyz"
    assert any("--detach" in c for c in cmds), "must fall back to detached checkout"
    assert any("checkout" in c and "-B" in c for c in cmds), "must switch to tracking branch"


def test_worktree_add_path_cleans_up_tempdir_on_failure(tmp_path: Path):
    """Any failure after mkdtemp should remove the partially created worktree dir."""

    def fake_run(cmd, **kw):
        m = MagicMock()
        if cmd[:4] == ["git", "fetch", "--no-tags", "origin"]:
            m.returncode = 0
            return m
        m.returncode = 128
        m.stderr = b"fatal: invalid reference: feat/missing"
        return m

    with patch("subprocess.run", side_effect=fake_run):
        from orchestration.dispatch_task import _worktree_add_path
        with pytest.raises(subprocess.CalledProcessError):
            _worktree_add_path("feat/missing", "/repo", str(tmp_path))

    assert list(tmp_path.iterdir()) == []
