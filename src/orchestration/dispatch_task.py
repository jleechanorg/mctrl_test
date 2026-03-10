"""dispatch_task — called by OpenClaw at agent spawn time.

Runs ai_orch, parses the session/worktree output, records git start_sha,
and writes BeadSessionMapping to the registry so the supervisor can track it.

Usage:
    python -m orchestration.dispatch_task \\
        --bead-id ORCH-xxx \\
        --task "implement feature X" \\
        --slack-trigger-ts 1772857900.668299 \\
        [--slack-trigger-channel C0A... ] \\
        [--agent-cli claude] \\
        [--registry-path .tracking/bead_session_registry.jsonl]
"""
from __future__ import annotations

import argparse
import hashlib
import logging
import os
import re
import shlex
import shutil
import site
import subprocess
import sys
import tempfile
import time

from orchestration.openclaw_notifier import notify_slack_started
from orchestration.session_registry import BeadSessionMapping, upsert_mapping

logger = logging.getLogger(__name__)


def find_existing_worktree(branch: str, repo_root: str) -> str | None:
    """Return path of an existing worktree for branch, or None.

    Skips the primary worktree (repo_root itself) — dispatch must not run
    agents in the main checkout. Returns None on any git failure so callers
    can fall back gracefully.
    """
    try:
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return None
    except Exception:
        return None

    primary = os.path.realpath(repo_root)
    current_path: str | None = None
    current_branch: str | None = None

    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            current_path = line[len("worktree "):].strip()
            current_branch = None
        elif line.startswith("branch refs/heads/"):
            current_branch = line[len("branch refs/heads/"):].strip()
        elif line == "":
            # End of a worktree block — check if it matches
            if (
                current_path
                and current_branch == branch
                and os.path.realpath(current_path) != primary
            ):
                return current_path
            current_path = None
            current_branch = None

    if (
        current_path
        and current_branch == branch
        and os.path.realpath(current_path) != primary
    ):
        return current_path

    return None


def _remote_branch_exists(branch: str, repo_root: str = ".") -> bool:
    """Return True if branch exists on origin."""
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--exit-code", "--heads", "origin", branch],
            cwd=repo_root,
            capture_output=True,
            timeout=15,
        )
        return result.returncode == 0
    except Exception:
        return False


def _worktree_add_path(branch: str, repo_root: str, worktree_base: str) -> str:
    """Checkout branch into a fresh directory under worktree_base. Returns path.

    If the branch is already checked out in the primary worktree, falls back to
    creating a detached HEAD worktree at origin/<branch>, then switches to the
    local tracking branch so the agent can commit and push normally.
    """
    safe = re.sub(r"[^a-zA-Z0-9._-]", "-", branch)
    dest = tempfile.mkdtemp(prefix=f"wt-{safe}-", dir=worktree_base)
    try:
        # Ensure origin/<branch> exists locally before the fallback path uses it.
        subprocess.run(
            ["git", "fetch", "--no-tags", "origin", branch],
            cwd=repo_root,
            check=True,
            timeout=30,
        )
        result = subprocess.run(
            ["git", "worktree", "add", dest, branch],
            cwd=repo_root,
            capture_output=True,
            timeout=30,
        )
        if result.returncode == 0:
            return dest

        stderr = result.stderr.decode("utf-8", errors="replace") if isinstance(result.stderr, bytes) else result.stderr
        if "already checked out" not in stderr:
            raise subprocess.CalledProcessError(result.returncode, result.args, result.stderr)

        # Branch is checked out in another worktree — create from the fetched
        # remote ref, then attach the local tracking branch inside the detached
        # linked worktree so the agent can commit and push normally.
        subprocess.run(
            ["git", "worktree", "add", "--detach", dest, f"origin/{branch}"],
            cwd=repo_root,
            check=True,
            timeout=30,
        )
        subprocess.run(
            ["git", "checkout", "-B", branch, "--track", f"origin/{branch}"],
            cwd=dest,
            check=True,
            timeout=15,
        )
        return dest
    except Exception:
        shutil.rmtree(dest, ignore_errors=True)
        raise


def resolve_worktree_for_branch(
    branch: str,
    repo_root: str,
    worktree_base: str,
) -> tuple[str, bool]:
    """Return (worktree_path, is_new) for branch.

    - Existing worktree → (path, False)
    - Branch on remote but not in any worktree → checkout fresh, (path, True)
    - Branch missing everywhere → raises ValueError
    """
    existing = find_existing_worktree(branch, repo_root)
    if existing:
        return existing, False

    if not _remote_branch_exists(branch, repo_root):
        raise ValueError(f"branch {branch!r} not found in any worktree or on remote origin")

    path = _worktree_add_path(branch, repo_root, worktree_base)
    return path, True


def _parse_ai_orch_output(output: str) -> tuple[str, str, str]:
    """Extract (session_name, worktree_path, branch) from ai_orch run output."""
    session = ""
    worktree = ""
    branch = ""

    for line in output.splitlines():
        # 🧩 Worktree: /tmp/ai-orch-worktrees/ai-orch-12345 (branch: ai-orch-12345)
        m = re.search(r"Worktree:\s+(\S+)\s+\(branch:\s+(\S+)\)", line)
        if m:
            worktree = m.group(1)
            branch = m.group(2)
        # 🚀 Async session: ai-claude-dfa2c0
        m2 = re.search(r"Async session:\s+(\S+)", line)
        if m2:
            session = m2.group(1)

    return session, worktree, branch


def _get_start_sha(worktree_path: str) -> str:
    """Get HEAD sha in the worktree — recorded as baseline for commit detection.

    Retries briefly because ai_orch may still be initializing the worktree git
    state when this is called immediately after spawn.
    """
    for _ in range(5):
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=worktree_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        time.sleep(1)
    return ""


_DEFAULT_WORKTREE_BASE = os.path.expanduser("~/.mctrl/worktrees")


def _task_with_push_instruction(task: str, branch: str = "") -> str:
    """Append a durable push requirement if the task does not already include one."""
    normalized = task.lower()
    if "git commit" in normalized:
        return task
    commit_text = (
        f"`git commit -m \"Your message\"`"
        if branch
        else "`git commit -m \"Your message\"`"
    )
    return (
        f"{task.rstrip()}\n\n"
        f"IMPORTANT: Work in the worktree ROOT directory (not a subdirectory). "
        f"After completing your changes, run:\n"
        f"1. `git add .` to stage all changes\n"
        f"2. {commit_text} to commit them\n"
        f"3. `git push origin {branch or '<your-branch>'}` to push to remote.\n"
        f"Your work is only visible after it is pushed to origin."
    )


def _unique_session_name(bead_id: str, session_name: str) -> str:
    """Build a bead-traceable tmux session name for this dispatch run."""
    bead_token = re.sub(r"[^a-zA-Z0-9]+", "-", bead_id).strip("-").lower() or "bead"
    return f"{bead_token}-{int(time.time())}-{session_name}"


def _make_async_session_name(agent_cli: str, repo_root: str) -> str:
    cwd_hash = hashlib.md5(os.path.realpath(repo_root).encode()).hexdigest()[:6]
    return f"ai-{agent_cli}-{cwd_hash}"


def _create_new_worktree(repo_root: str, worktree_base: str) -> tuple[str, str]:
    """Create a fresh worktree + branch for direct CLI dispatch."""
    os.makedirs(worktree_base, exist_ok=True)
    branch = f"ai-orch-{int(time.time()) % 100000}"
    worktree_path = os.path.join(worktree_base, branch)
    result = subprocess.run(
        ["git", "worktree", "add", "-b", branch, worktree_path],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git worktree add failed: {result.stderr.strip()}")
    return worktree_path, branch


def _build_cursor_shell_cmd(task: str, worktree_path: str) -> str:
    """Run Cursor in headless trusted mode so dispatch never blocks on trust UI."""
    model = os.environ.get("MCTRL_CURSOR_MODEL", "auto")
    return " ".join(
        [
            "cursor-agent",
            "--print",
            "--trust",
            "--approve-mcps",
            "--output-format",
            "text",
            "--model",
            shlex.quote(model),
            "--workspace",
            shlex.quote(worktree_path),
            "--yolo",
            shlex.quote(task),
        ]
    )


def _build_ai_orch_env() -> dict[str, str]:
    """Build a clean env so ai_orch does not import mctrl's local orchestration package."""
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)

    user_site = site.getusersitepackages()
    if user_site:
        env["PYTHONPATH"] = user_site

    return env


def _dispatch_cursor_direct(
    *,
    bead_id: str,
    task: str,
    branch: str,
    repo_root: str,
) -> tuple[str, str, str]:
    """Dispatch Cursor via tmux directly, bypassing ai_orch's interactive fallback."""
    worktree_base = os.environ.get("MCTRL_WORKTREE_BASE", _DEFAULT_WORKTREE_BASE)
    if branch:
        worktree_path, _ = resolve_worktree_for_branch(branch, repo_root, worktree_base)
        effective_branch = branch
    else:
        worktree_path, effective_branch = _create_new_worktree(repo_root, worktree_base)

    session_name = _make_async_session_name("cursor", repo_root)
    shell_cmd = _build_cursor_shell_cmd(
        _task_with_push_instruction(task, effective_branch),
        worktree_path,
    )
    result = subprocess.run(
        ["tmux", "new-session", "-d", "-s", session_name, "-c", worktree_path, shell_cmd],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        raise RuntimeError(f"cursor tmux dispatch failed: {result.stderr.strip()}")
    return session_name, worktree_path, effective_branch


def _rename_tmux_session(session_name: str, bead_id: str) -> str:
    """Rename the tmux session to a bead-traceable name when it is still alive."""
    target_name = _unique_session_name(bead_id, session_name)
    if target_name == session_name:
        return session_name

    result = subprocess.run(
        ["tmux", "rename-session", "-t", session_name, target_name],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode == 0:
        return target_name

    stderr = (result.stderr or "").strip().lower()
    if "can't find session" in stderr or "no such session" in stderr:
        return session_name
    logger.warning(
        "Could not rename tmux session %r to %r: %s",
        session_name,
        target_name,
        result.stderr.strip(),
    )
    return session_name


def dispatch(
    *,
    bead_id: str,
    task: str,
    slack_trigger_ts: str = "",
    slack_trigger_channel: str = "",
    agent_cli: str = "claude",
    registry_path: str,
    branch: str = "",
    repo_root: str = ".",
) -> BeadSessionMapping:
    """Spawn ai_orch session and register the mapping. Returns the created mapping.

    When branch is provided, resolve_worktree_for_branch is called first:
    - Existing linked worktree → ai_orch runs there (no --worktree flag)
    - Remote-only branch → checkout fresh worktree, ai_orch runs there
    - Branch missing everywhere → raises ValueError before spawning

    Without branch, ai_orch creates a new worktree via --worktree (new task).
    """
    if slack_trigger_ts and not slack_trigger_channel:
        raise ValueError("slack_trigger_channel is required when slack_trigger_ts is set")

    if agent_cli == "cursor":
        session_name, worktree_path, parsed_branch = _dispatch_cursor_direct(
            bead_id=bead_id,
            task=task,
            branch=branch,
            repo_root=repo_root,
        )
    else:
        if branch:
            worktree_base = os.environ.get("MCTRL_WORKTREE_BASE", _DEFAULT_WORKTREE_BASE)
            os.makedirs(worktree_base, exist_ok=True)
            cwd, _ = resolve_worktree_for_branch(branch, repo_root, worktree_base)
            agent_task = _task_with_push_instruction(task, branch)
            cmd = ["ai_orch", "run", "--async", "--agent-cli", agent_cli, agent_task]
        else:
            cwd = repo_root
            agent_task = _task_with_push_instruction(task)
            cmd = ["ai_orch", "run", "--async", "--worktree", "--agent-cli", agent_cli, agent_task]

        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60,
            env=_build_ai_orch_env(),
        )
        output = result.stdout + result.stderr

        if result.returncode != 0:
            raise RuntimeError(f"ai_orch failed (exit {result.returncode}):\n{output}")

        session_name, worktree_path, parsed_branch = _parse_ai_orch_output(output)
        if not session_name or not worktree_path:
            raise RuntimeError(f"Could not parse ai_orch output:\n{output}")

    session_name = _rename_tmux_session(session_name, bead_id)

    effective_branch = branch or parsed_branch
    start_sha = _get_start_sha(worktree_path)

    mapping = BeadSessionMapping.create(
        bead_id=bead_id,
        session_name=session_name,
        worktree_path=worktree_path,
        branch=effective_branch,
        agent_cli=agent_cli,
        status="in_progress",
        start_sha=start_sha,
        slack_trigger_ts=slack_trigger_ts,
        slack_trigger_channel=slack_trigger_channel,
    )
    upsert_mapping(mapping, registry_path=registry_path)
    notify_slack_started({
        "event": "task_started",
        "bead_id": bead_id,
        "session": session_name,
        "worktree_path": worktree_path,
        "branch": effective_branch,
        "agent_cli": agent_cli,
        "slack_trigger_ts": slack_trigger_ts,
        "slack_trigger_channel": slack_trigger_channel,
    })
    return mapping


def main() -> None:
    parser = argparse.ArgumentParser(description="Dispatch a task via ai_orch and register it.")
    parser.add_argument("--bead-id", required=True, help="Bead ID (e.g. ORCH-xxx)")
    parser.add_argument("--task", required=True, help="Task description passed to ai_orch")
    parser.add_argument("--slack-trigger-ts", default="", help="Slack ts of trigger message (for threading)")
    parser.add_argument("--slack-trigger-channel", default="", help="Slack channel ID of trigger message (for threading)")
    parser.add_argument("--agent-cli", default="claude", help="Agent CLI: claude, codex, gemini, minimax, cursor")
    parser.add_argument(
        "--registry-path",
        default=".tracking/bead_session_registry.jsonl",
        help="Path to bead session registry JSONL",
    )
    args = parser.parse_args()

    try:
        mapping = dispatch(
            bead_id=args.bead_id,
            task=args.task,
            slack_trigger_ts=args.slack_trigger_ts,
            slack_trigger_channel=args.slack_trigger_channel,
            agent_cli=args.agent_cli,
            registry_path=args.registry_path,
        )
        print(f"dispatched bead={mapping.bead_id} session={mapping.session_name} worktree={mapping.worktree_path}")
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
