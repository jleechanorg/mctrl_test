"""Lifecycle reactions — state machine + reaction engine.

Ported from agent-orchestrator lifecycle-manager.ts.
Detects state transitions and triggers reactions (auto-retry, escalation).

State machine:
  working → pr_open → ci_failed ──(auto-retry)──→ working
                    → review_pending → changes_requested ──(auto-retry)──→ working
                    → approved → mergeable → merged
  Terminal: stuck, needs_input, errored, killed, done
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Optional


# ---------------------------------------------------------------------------
# Session status enum
# ---------------------------------------------------------------------------


class SessionStatus(StrEnum):
    SPAWNING = "spawning"
    WORKING = "working"
    PR_OPEN = "pr_open"
    CI_FAILED = "ci_failed"
    REVIEW_PENDING = "review_pending"
    CHANGES_REQUESTED = "changes_requested"
    APPROVED = "approved"
    MERGEABLE = "mergeable"
    MERGED = "merged"
    STUCK = "stuck"
    NEEDS_INPUT = "needs_input"
    ERRORED = "errored"
    KILLED = "killed"
    DONE = "done"


# ---------------------------------------------------------------------------
# Event mapping
# ---------------------------------------------------------------------------


def status_to_event_type(
    from_status: Optional[SessionStatus],
    to_status: SessionStatus,
) -> Optional[str]:
    """Map a status transition to an event type string."""
    mapping = {
        SessionStatus.WORKING: "session.working",
        SessionStatus.PR_OPEN: "pr.created",
        SessionStatus.CI_FAILED: "ci.failing",
        SessionStatus.REVIEW_PENDING: "review.pending",
        SessionStatus.CHANGES_REQUESTED: "review.changes_requested",
        SessionStatus.APPROVED: "review.approved",
        SessionStatus.MERGEABLE: "merge.ready",
        SessionStatus.MERGED: "merge.completed",
        SessionStatus.NEEDS_INPUT: "session.needs_input",
        SessionStatus.STUCK: "session.stuck",
        SessionStatus.ERRORED: "session.errored",
        SessionStatus.KILLED: "session.killed",
    }
    return mapping.get(to_status)


def event_to_reaction_key(event_type: str) -> Optional[str]:
    """Map an event type to a reaction config key."""
    mapping = {
        "ci.failing": "ci-failed",
        "review.changes_requested": "changes-requested",
        "automated_review.found": "bugbot-comments",
        "merge.conflicts": "merge-conflicts",
        "merge.ready": "approved-and-green",
        "session.stuck": "agent-stuck",
        "session.needs_input": "agent-needs-input",
        "session.killed": "agent-exited",
        "summary.all_complete": "all-complete",
    }
    return mapping.get(event_type)


def infer_priority(event_type: str) -> str:
    """Infer a reasonable priority from event type."""
    if "stuck" in event_type or "needs_input" in event_type or "errored" in event_type:
        return "urgent"
    if event_type.startswith("summary."):
        return "info"
    if any(k in event_type for k in ("approved", "ready", "merged", "completed")):
        return "action"
    if any(k in event_type for k in ("fail", "changes_requested", "conflicts")):
        return "warning"
    return "info"


# ---------------------------------------------------------------------------
# Reaction config
# ---------------------------------------------------------------------------


@dataclass
class ReactionConfig:
    """Configuration for an automated reaction."""
    action: str  # "send-to-agent", "notify", "auto-merge"
    retries: Optional[int] = None
    escalate_after: Optional[str] = None  # duration like "10m"
    message: Optional[str] = None
    priority: str = "info"
    auto: bool = True


# ---------------------------------------------------------------------------
# Reaction tracker
# ---------------------------------------------------------------------------


@dataclass
class ReactionTracker:
    """Tracks reaction attempts per session per reaction key."""
    attempts: int = 0
    first_triggered: datetime = field(default_factory=datetime.now)


# ---------------------------------------------------------------------------
# Lifecycle manager
# ---------------------------------------------------------------------------


class LifecycleManager:
    """State machine + reaction engine for agent lifecycle management.

    Tracks sessions, detects state transitions, and executes reactions
    with escalation after max retries.
    """

    def __init__(self, reactions: dict[str, ReactionConfig]):
        self._states: dict[str, SessionStatus] = {}
        self._reactions = reactions
        self._trackers: dict[str, ReactionTracker] = {}  # "session_id:reaction_key"

    def get_states(self) -> dict[str, SessionStatus]:
        """Return a copy of all tracked session states."""
        return dict(self._states)

    def record_state(self, session_id: str, status: SessionStatus) -> None:
        """Record/update the state of a session.

        When state changes, clears associated reaction trackers.
        """
        old_status = self._states.get(session_id)
        self._states[session_id] = status

        # Clear reaction trackers on state change
        if old_status is not None and old_status != status:
            keys_to_clear = [
                k for k in self._trackers
                if k.startswith(f"{session_id}:")
            ]
            for k in keys_to_clear:
                del self._trackers[k]

    def check_transition(
        self,
        session_id: str,
        new_status: SessionStatus,
    ) -> Optional[tuple[SessionStatus, SessionStatus]]:
        """Check if a state transition occurred.

        Returns (old_status, new_status) if transition detected, None if same.
        """
        old_status = self._states.get(session_id)
        if old_status == new_status:
            return None
        return (old_status, new_status) if old_status else (new_status, new_status)

    def execute_reaction(
        self,
        session_id: str,
        reaction_key: str,
    ) -> dict:
        """Execute a reaction for a session.

        Returns dict with keys: success, action, escalated, reaction_type.
        """
        config = self._reactions.get(reaction_key)
        if config is None:
            return {
                "success": False,
                "action": None,
                "escalated": False,
                "reaction_type": reaction_key,
            }

        tracker_key = f"{session_id}:{reaction_key}"
        tracker = self._trackers.get(tracker_key)
        if tracker is None:
            tracker = ReactionTracker()
            self._trackers[tracker_key] = tracker

        tracker.attempts += 1

        # Check escalation
        should_escalate = False
        if config.retries is not None and tracker.attempts > config.retries:
            should_escalate = True

        if should_escalate:
            return {
                "success": True,
                "action": "escalated",
                "escalated": True,
                "reaction_type": reaction_key,
                "attempts": tracker.attempts,
            }

        return {
            "success": True,
            "action": config.action,
            "escalated": False,
            "reaction_type": reaction_key,
            "message": config.message,
        }


# ---------------------------------------------------------------------------
# determine_status — infers session status from SCM state
# ---------------------------------------------------------------------------


def determine_status(
    session: dict,
    *,
    scm_state: Optional[dict],
) -> SessionStatus:
    """Infer the session status from SCM/runtime state.

    Args:
        session: Dict with at least 'id', 'status', 'pr', 'branch'.
        scm_state: Dict with 'pr_state', 'ci_status', 'review_decision', 'mergeable'.
                   None if no PR detected.
    """
    # No PR → still working
    if scm_state is None or session.get("pr") is None:
        return SessionStatus.WORKING

    pr_state = scm_state.get("pr_state", "open")

    # Terminal states
    if pr_state == "merged":
        return SessionStatus.MERGED
    if pr_state == "closed":
        return SessionStatus.KILLED

    # PR is open — check CI first
    ci_status = scm_state.get("ci_status", "none")
    if ci_status == "failing":
        return SessionStatus.CI_FAILED

    # CI passing — check review
    review = scm_state.get("review_decision", "none")
    if review == "changes_requested":
        return SessionStatus.CHANGES_REQUESTED
    if review == "approved":
        if scm_state.get("mergeable", False):
            return SessionStatus.MERGEABLE
        return SessionStatus.APPROVED
    if review == "pending":
        return SessionStatus.REVIEW_PENDING

    # PR is open, CI passing, no review decision
    return SessionStatus.PR_OPEN


# ---------------------------------------------------------------------------
# Lifecycle poller — threaded polling loop
# ---------------------------------------------------------------------------


class LifecyclePoller:
    """Threaded polling loop for the lifecycle manager.

    Calls poll function at regular intervals. Start/stop are idempotent.
    """

    def __init__(
        self,
        lifecycle_manager: LifecycleManager,
        interval_seconds: int = 60,
    ):
        self.lifecycle_manager = lifecycle_manager
        self.interval_seconds = interval_seconds
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self) -> None:
        """Start the polling loop in a daemon thread."""
        if self._running:
            return
        self._stop_event.clear()
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the polling loop."""
        if not self._running:
            return
        self._stop_event.set()
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None

    def _run(self) -> None:
        """Internal polling loop."""
        while not self._stop_event.is_set():
            self._stop_event.wait(self.interval_seconds)

