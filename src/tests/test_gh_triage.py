"""Tests for orchestration.gh_triage — GitHub notification triage."""

from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

from orchestration.gh_integration import MergeReadiness, PRInfo
from orchestration.gh_triage import triage_github_notifications


class TestGHTriage:
    """Tests for triage_github_notifications()."""

    def test_triage_filters_reasons(self):
        """Only matching notification reasons are triaged."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.create_task.return_value = {"id": "task-1"}

        def fake_gh(args):
            return json.dumps([
                {
                    "id": "n1",
                    "reason": "review_requested",
                    "subject": {
                        "type": "PullRequest",
                        "title": "Fix bug",
                        "url": "https://github.com/owner/repo/pull/101",
                    },
                    "repository": {"nameWithOwner": "owner/repo"},
                },
                {
                    "id": "n2",
                    "reason": "mention",
                    "subject": {"type": "PullRequest", "title": "Other", "url": "https://github.com/owner/repo/pull/102"},
                    "repository": {"nameWithOwner": "owner/repo"},
                },
            ])

        with patch(
            "orchestration.gh_triage.get_merge_readiness",
            return_value=MergeReadiness(
                mergeable=True,
                ci_passing=True,
                approved=True,
                no_conflicts=True,
                blockers=[],
            ),
        ) as mock_readiness:
            created = triage_github_notifications(
                "board-123",
                mock_client,
                reasons={"review_requested"},
                gh_fn=fake_gh,
            )

        assert len(created) == 1
        assert mock_readiness.call_count == 1
        mock_client.create_task.assert_called_once()
        created_payload = mock_client.create_task.call_args[0][0]
        assert created_payload["title"].startswith("[review_requested]")
        assert created_payload["board_id"] == "board-123"

    def test_triage_builds_task_with_readiness_details(self):
        """Created tasks include merge-readiness context in custom fields."""
        mock_client = MagicMock()
        mock_client.is_configured = True
        mock_client.create_task.return_value = {"id": "task-2"}

        def fake_gh(args):
            return json.dumps([
                {
                    "id": "n3",
                    "reason": "ci_activity",
                    "subject": {
                        "type": "PullRequest",
                        "title": "Feature",
                        "url": "https://github.com/owner/repo/pull/77",
                    },
                    "repository": {"nameWithOwner": "owner/repo"},
                },
            ])

        expected_readiness = MergeReadiness(
            mergeable=False,
            ci_passing=False,
            approved=False,
            no_conflicts=False,
            blockers=["CI checks are failing", "Merge conflicts"],
        )

        with patch("orchestration.gh_triage.get_merge_readiness", return_value=expected_readiness) as mock_readiness:
            created = triage_github_notifications(
                "board-123",
                mock_client,
                reasons={"ci_activity"},
                gh_fn=fake_gh,
            )

        assert len(created) == 1
        assert mock_readiness.call_count == 1
        created_payload = mock_client.create_task.call_args[0][0]
        assert created_payload["source"] == "github_notification"
        assert created_payload["custom_fields"]["repo"] == "owner/repo"
        assert created_payload["custom_fields"]["pr_number"] == 77
        assert created_payload["custom_fields"]["notification_reason"] == "ci_activity"
        assert created_payload["custom_fields"]["merge_ready"] is False
        assert "CI checks are failing" in created_payload["description"]

        pr_info = mock_readiness.call_args[0][0]
        assert isinstance(pr_info, PRInfo)
        assert pr_info.owner == "owner"
        assert pr_info.repo == "repo"
        assert pr_info.number == 77

    def test_triage_skips_invalid_github_payload(self):
        """Invalid notifications JSON is ignored and returns no tasks."""
        mock_client = MagicMock()
        mock_client.is_configured = True

        with patch("orchestration.gh_triage.get_merge_readiness") as mock_readiness:
            created = triage_github_notifications(
                "board-123",
                mock_client,
                gh_fn=lambda args: "not-json",
            )

        assert created == []
        mock_readiness.assert_not_called()
        mock_client.create_task.assert_not_called()

