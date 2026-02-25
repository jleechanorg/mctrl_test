"""Tests for orchestration.lifecycle_reactions — state machine + reaction engine."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from orchestration.lifecycle_reactions import (
    SessionStatus,
    ReactionConfig,
    ReactionTracker,
    LifecycleManager,
    status_to_event_type,
    event_to_reaction_key,
    infer_priority,
)


# ---------------------------------------------------------------------------
# SessionStatus enum
# ---------------------------------------------------------------------------


class TestSessionStatus:
    def test_working(self):
        assert SessionStatus.WORKING == "working"

    def test_pr_open(self):
        assert SessionStatus.PR_OPEN == "pr_open"

    def test_ci_failed(self):
        assert SessionStatus.CI_FAILED == "ci_failed"

    def test_review_pending(self):
        assert SessionStatus.REVIEW_PENDING == "review_pending"

    def test_changes_requested(self):
        assert SessionStatus.CHANGES_REQUESTED == "changes_requested"

    def test_approved(self):
        assert SessionStatus.APPROVED == "approved"

    def test_mergeable(self):
        assert SessionStatus.MERGEABLE == "mergeable"

    def test_merged(self):
        assert SessionStatus.MERGED == "merged"

    def test_stuck(self):
        assert SessionStatus.STUCK == "stuck"

    def test_needs_input(self):
        assert SessionStatus.NEEDS_INPUT == "needs_input"

    def test_errored(self):
        assert SessionStatus.ERRORED == "errored"

    def test_killed(self):
        assert SessionStatus.KILLED == "killed"


# ---------------------------------------------------------------------------
# status_to_event_type()
# ---------------------------------------------------------------------------


class TestStatusToEventType:
    def test_working(self):
        assert status_to_event_type(None, SessionStatus.WORKING) == "session.working"

    def test_pr_created(self):
        assert status_to_event_type(SessionStatus.WORKING, SessionStatus.PR_OPEN) == "pr.created"

    def test_ci_failing(self):
        assert status_to_event_type(SessionStatus.PR_OPEN, SessionStatus.CI_FAILED) == "ci.failing"

    def test_review_approved(self):
        assert status_to_event_type(SessionStatus.REVIEW_PENDING, SessionStatus.APPROVED) == "review.approved"

    def test_merge_ready(self):
        assert status_to_event_type(SessionStatus.APPROVED, SessionStatus.MERGEABLE) == "merge.ready"

    def test_merge_completed(self):
        assert status_to_event_type(SessionStatus.MERGEABLE, SessionStatus.MERGED) == "merge.completed"

    def test_stuck(self):
        assert status_to_event_type(None, SessionStatus.STUCK) == "session.stuck"


# ---------------------------------------------------------------------------
# event_to_reaction_key()
# ---------------------------------------------------------------------------


class TestEventToReactionKey:
    def test_ci_failing(self):
        assert event_to_reaction_key("ci.failing") == "ci-failed"

    def test_changes_requested(self):
        assert event_to_reaction_key("review.changes_requested") == "changes-requested"

    def test_merge_ready(self):
        assert event_to_reaction_key("merge.ready") == "approved-and-green"

    def test_agent_stuck(self):
        assert event_to_reaction_key("session.stuck") == "agent-stuck"

    def test_unknown(self):
        assert event_to_reaction_key("unknown.event") is None


# ---------------------------------------------------------------------------
# infer_priority()
# ---------------------------------------------------------------------------


class TestInferPriority:
    def test_stuck_is_urgent(self):
        assert infer_priority("session.stuck") == "urgent"

    def test_needs_input_is_urgent(self):
        assert infer_priority("session.needs_input") == "urgent"

    def test_approved_is_action(self):
        assert infer_priority("review.approved") == "action"

    def test_failing_is_warning(self):
        assert infer_priority("ci.failing") == "warning"

    def test_working_is_info(self):
        assert infer_priority("session.working") == "info"


# ---------------------------------------------------------------------------
# ReactionConfig
# ---------------------------------------------------------------------------


class TestReactionConfig:
    def test_defaults(self):
        rc = ReactionConfig(action="notify")
        assert rc.action == "notify"
        assert rc.retries is None
        assert rc.escalate_after is None

    def test_with_retries(self):
        rc = ReactionConfig(action="send-to-agent", retries=3, escalate_after="10m")
        assert rc.retries == 3
        assert rc.escalate_after == "10m"


# ---------------------------------------------------------------------------
# ReactionTracker
# ---------------------------------------------------------------------------


class TestReactionTracker:
    def test_initial_attempts(self):
        tracker = ReactionTracker()
        assert tracker.attempts == 0

    def test_increment(self):
        tracker = ReactionTracker()
        tracker.attempts += 1
        assert tracker.attempts == 1


# ---------------------------------------------------------------------------
# LifecycleManager
# ---------------------------------------------------------------------------


class TestLifecycleManager:
    def test_creation(self):
        lm = LifecycleManager(reactions={})
        assert lm is not None

    def test_get_states_initially_empty(self):
        lm = LifecycleManager(reactions={})
        assert lm.get_states() == {}

    def test_record_transition(self):
        lm = LifecycleManager(reactions={})
        lm.record_state("session-1", SessionStatus.WORKING)
        assert lm.get_states()["session-1"] == SessionStatus.WORKING

    def test_state_transition_detected(self):
        lm = LifecycleManager(reactions={})
        lm.record_state("session-1", SessionStatus.WORKING)
        old, new = lm.check_transition("session-1", SessionStatus.PR_OPEN)
        assert old == SessionStatus.WORKING
        assert new == SessionStatus.PR_OPEN

    def test_no_transition_same_state(self):
        lm = LifecycleManager(reactions={})
        lm.record_state("session-1", SessionStatus.WORKING)
        result = lm.check_transition("session-1", SessionStatus.WORKING)
        assert result is None

    def test_reaction_tracking(self):
        reactions = {
            "ci-failed": ReactionConfig(action="send-to-agent", retries=3,
                                         message="Fix CI"),
        }
        lm = LifecycleManager(reactions=reactions)
        result = lm.execute_reaction("session-1", "ci-failed")
        assert result["success"] is True
        assert result["action"] == "send-to-agent"

    def test_escalation_after_max_retries(self):
        reactions = {
            "ci-failed": ReactionConfig(action="send-to-agent", retries=2,
                                         message="Fix CI"),
        }
        lm = LifecycleManager(reactions=reactions)
        lm.execute_reaction("session-1", "ci-failed")  # attempt 1
        lm.execute_reaction("session-1", "ci-failed")  # attempt 2
        result = lm.execute_reaction("session-1", "ci-failed")  # attempt 3 → escalate
        assert result["escalated"] is True

    def test_unknown_reaction_key(self):
        lm = LifecycleManager(reactions={})
        result = lm.execute_reaction("session-1", "nonexistent")
        assert result["success"] is False

    def test_clear_tracker_on_state_change(self):
        reactions = {
            "ci-failed": ReactionConfig(action="send-to-agent", retries=2,
                                         message="Fix CI"),
        }
        lm = LifecycleManager(reactions=reactions)
        lm.record_state("s1", SessionStatus.CI_FAILED)
        lm.execute_reaction("s1", "ci-failed")  # attempt 1
        lm.execute_reaction("s1", "ci-failed")  # attempt 2

        # State changes — trackers should reset
        lm.record_state("s1", SessionStatus.WORKING)
        lm.record_state("s1", SessionStatus.CI_FAILED)
        result = lm.execute_reaction("s1", "ci-failed")  # should be attempt 1 again
        assert result["escalated"] is False
