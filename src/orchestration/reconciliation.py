from __future__ import annotations

import logging
import subprocess
import threading
from typing import Any

from orchestration.openclaw_notifier import drain_outbox, notify_openclaw, notify_slack_done
from orchestration.session_registry import list_mappings, update_mapping_status

logger = logging.getLogger(__name__)


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
    - True: origin/<branch> contains local HEAD
    - False: remote branch is reachable and does not contain local HEAD
    - None: remote verification could not be completed (transient failure)
    """
    if not branch or not worktree_path:
        return False
    try:
        fetch_result = subprocess.run(
            ["git", "fetch", "--no-tags", "origin", branch],
            cwd=worktree_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if fetch_result.returncode != 0:
            logger.warning(
                "Could not verify remote branch %s in %s: %s",
                branch,
                worktree_path,
                (fetch_result.stderr or "").strip(),
            )
            return None

        remote_ref = f"origin/{branch}"
        remote_result = subprocess.run(
            ["git", "rev-parse", "--verify", remote_ref],
            cwd=worktree_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if remote_result.returncode != 0:
            return False

        ancestry_result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", "HEAD", remote_ref],
            cwd=worktree_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return ancestry_result.returncode == 0
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
    dead_letter_path: str,
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
            summary = "ai_orch session completed — branch is reviewable on origin"
            action = "review_and_merge"
        elif has_commits:
            new_status = "needs_human"
            event_type = "task_needs_human"
            summary = "ai_orch session committed locally but did not push the branch to origin"
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
        # Fire both notifications in parallel: openclaw agent + Slack
        t_openclaw = threading.Thread(
            target=notify_openclaw,
            args=(payload,),
            kwargs={"outbox_path": outbox_path},
            daemon=True,
        )
        t_slack = threading.Thread(
            target=notify_slack_done,
            args=(payload,),
            daemon=True,
        )
        t_openclaw.start()
        t_slack.start()
        t_openclaw.join(timeout=35)
        # Slack posts two requests (DM + public channel) each with 5s network
        # timeout = 10s max, plus overhead. Use 30s so the join reliably waits
        # for completion rather than leaving a daemon thread racing the caller.
        t_slack.join(timeout=30)
        emitted.append(payload)

    # Attempt to drain any previously failed notifications now that we're in a live code path
    drain_outbox(outbox_path=outbox_path, dead_letter_path=dead_letter_path)

    return emitted
