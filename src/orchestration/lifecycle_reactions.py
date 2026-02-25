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
