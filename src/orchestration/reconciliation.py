from __future__ import annotations

import logging
import subprocess
import threading
from typing import Any

from orchestration.openclaw_notifier import (
    drain_outbox,
    notify_openclaw,
    notify_slack_done,
    openclaw_notification_max_runtime_seconds,
)
from orchestration.session_registry import list_mappings, update_mapping_status

logger = logging.getLogger(__name__)


def _notify_completion(payload: dict[str, Any], outbox_path: str) -> None:
    # Slack thread closure is the primary user-visible completion signal.
    # OpenClaw delivery remains a secondary system-to-system channel.
    notify_slack_done(payload)
    notify_openclaw(payload, outbox_path=outbox_path)


def run_tmux_sessions() -> set[str]:
    """Return set of active tmux session names. Empty set if tmux not running."""
    try:
        result = subprocess.run(
            ["tmux", "ls", "-F", "#{session_name}"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return set()
        return {line.strip() for line in result.stdout.splitlines() if line.strip()}
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return set()


def _worktree_has_commits(worktree_path: str | None, start_sha: str = "") -> bool:
    """Return True if the agent made new commits since spawn.

    Uses start_sha..HEAD when available — only counts commits the agent made.
    Falls back to git status --porcelain (uncommitted changes) for legacy entries.
    """
    if not worktree_path:
        return False
    try:
        if start_sha:
            result = subprocess.run(
                ["git", "log", "--oneline", f"{start_sha}..HEAD"],
                cwd=worktree_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return bool(result.returncode == 0 and result.stdout.strip())
        # No start_sha: cannot distinguish agent commits from pre-existing history.
        # Default to False (→ needs_human) so humans review rather than silently
        # misclassifying a dirty-tree crash as task_finished.
        return False
    except Exception:
        return False


def _remote_branch_exists(branch: str, worktree_path: str | None) -> bool | None:
    """Return remote verification state for the local HEAD.

    Returns:
    - True: at least one configured remote ref contains local HEAD
    - False: remote verification succeeded and no remote ref contains local HEAD
    - None: remote verification could not be completed (transient failure)
    """
    if not worktree_path:
        return False

    def _git(args: list[str], timeout: int = 10) -> subprocess.CompletedProcess:
        return subprocess.run(
            args,
            cwd=worktree_path,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

    def _is_transient_fetch_error(stderr: str) -> bool:
        lowered = (stderr or "").lower()
        transient_markers = (
            "timed out",
            "timeout",
            "temporary failure",
            "could not resolve host",
            "network",
            "connection",
            "service unavailable",
            "internal server error",
            "remote end hung up unexpectedly",
            "tls",
        )
        return any(marker in lowered for marker in transient_markers)

    try:
        remotes_result = _git(["git", "remote"])
        remotes = [r.strip() for r in remotes_result.stdout.splitlines() if r.strip()]
        if remotes_result.returncode != 0 or not remotes:
            return False

        current_branch = ""
        current_branch_result = _git(["git", "branch", "--show-current"])
        if current_branch_result.returncode == 0:
            current_branch = current_branch_result.stdout.strip()

        upstream_ref = ""
        upstream_result = _git(
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"]
        )
        if upstream_result.returncode == 0:
            upstream_ref = upstream_result.stdout.strip()

        candidate_refs: set[str] = set()
        if branch:
            for remote in remotes:
                candidate_refs.add(f"{remote}/{branch}")
        if current_branch:
            for remote in remotes:
                candidate_refs.add(f"{remote}/{current_branch}")
        if upstream_ref and "/" in upstream_ref:
            candidate_refs.add(upstream_ref)

        deterministic_failure_seen = False
        transient_fetch_failure_seen = False
        for remote in remotes:
            fetch_result = _git(
                ["git", "fetch", "--no-tags", "--prune", remote], timeout=15
            )
            if fetch_result.returncode != 0:
                stderr = (fetch_result.stderr or "").strip()
                if _is_transient_fetch_error(stderr):
                    transient_fetch_failure_seen = True
                    logger.warning(
                        "Transient fetch failure for remote %s in %s: %s",
                        remote,
                        worktree_path,
                        stderr,
                    )
                    continue
                logger.warning(
                    "Non-transient fetch failure for remote %s in %s: %s",
                    remote,
                    worktree_path,
                    stderr,
                )
                deterministic_failure_seen = True
                continue

            for remote_ref in sorted(candidate_refs):
                if not remote_ref.startswith(f"{remote}/"):
                    continue
                remote_result = _git(["git", "rev-parse", "--verify", remote_ref])
                if remote_result.returncode != 0:
                    continue
                ancestry_result = _git(
                    ["git", "merge-base", "--is-ancestor", "HEAD", remote_ref]
                )
                if ancestry_result.returncode == 0:
                    return True
                if ancestry_result.returncode == 1:
                    deterministic_failure_seen = True
                    continue
                transient_fetch_failure_seen = True

        if transient_fetch_failure_seen:
            return None
        if deterministic_failure_seen:
            return False
        return False
    except Exception as exc:
        logger.warning(
            "Remote verification failed for %s in %s: %s",
            branch,
            worktree_path,
            exc,
        )
        return None


def reconcile_registry_once(
    *,
    registry_path: str,
    outbox_path: str,
    dead_letter_path: str | None = None,
) -> list[dict[str, Any]]:
    """Reconcile bead/session mappings when session is gone.

    Only checks in_progress mappings. Distinguishes two exit outcomes:
    - task_finished: worktree branch has new commits → agent completed work
    - task_needs_human: no commits found → agent stalled, crashed, or timed out
    """
    # Retry any previously failed notifications before emitting new ones.
    drain_outbox(outbox_path=outbox_path, dead_letter_path=dead_letter_path)

    active = run_tmux_sessions()
    emitted: list[dict[str, Any]] = []

    for mapping in list_mappings(registry_path=registry_path):
        # Only check in_progress tasks - queued tasks may have session_name pre-assigned
        # but the session hasn't started yet (pre-allocation state)
        if mapping.status != "in_progress":
            continue
        if mapping.session_name in active:
            continue

        # Determine exit outcome by checking for commits the agent made
        has_commits = _worktree_has_commits(mapping.worktree_path, mapping.start_sha)
        pushed_remote = has_commits and _remote_branch_exists(mapping.branch, mapping.worktree_path)
        if has_commits and pushed_remote is None:
            logger.info(
                "Deferred reconciliation for %s due to transient remote verification failure",
                mapping.bead_id,
            )
            continue
        finished = has_commits and pushed_remote

        if finished:
            new_status = "finished"
            event_type = "task_finished"
            summary = "ai_orch session completed — branch is reviewable on a configured remote"
            action = "review_and_merge"
        elif has_commits:
            new_status = "needs_human"
            event_type = "task_needs_human"
            summary = "ai_orch session committed locally but did not push a reviewable branch to a configured remote"
            action = "push_or_salvage"
        else:
            new_status = "needs_human"
            event_type = "task_needs_human"
            summary = "ai_orch session exited without committing — may have stalled or failed"
            action = "human_decision"

        changed = update_mapping_status(
            mapping.bead_id,
            new_status,
            from_status="in_progress",
            registry_path=registry_path,
        )
        if not changed:
            continue

        payload = {
            "event": event_type,
            "bead_id": mapping.bead_id,
            "session": mapping.session_name,
            "summary": summary,
            "action_required": action,
            "worktree_path": mapping.worktree_path,
            "branch": mapping.branch,
            "agent_cli": mapping.agent_cli,
            "slack_trigger_ts": mapping.slack_trigger_ts,
            "slack_trigger_channel": mapping.slack_trigger_channel,
        }
        # Emit a single channel-agnostic notification to OpenClaw.
        t_openclaw = threading.Thread(
            target=_notify_completion,
            args=(payload, outbox_path),
            daemon=True,
        )
        t_openclaw.start()
        t_openclaw.join(timeout=openclaw_notification_max_runtime_seconds())
        emitted.append(payload)

    # Attempt to drain any previously failed notifications now that we're in a live code path
    drain_outbox(outbox_path=outbox_path, dead_letter_path=dead_letter_path)

    return emitted
