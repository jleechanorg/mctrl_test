"""Tests for dispatch_task cross-repo and worktree functions."""
from __future__ import annotations

import pytest

from orchestration.dispatch_task import (
    _is_cross_repo_task,
    _CROSS_REPO_CONTEXT,
    _extract_repo_name_hint,
)


class TestIsCrossRepoTask:
    """Tests for _is_cross_repo_task function."""

    @pytest.mark.parametrize(
        "task,expected",
        [
            # Cross-repo indicators (from implementation)
            ("fix comments worldai mcp PR to worldarchitect.ai", True),
            ("make a PR against jleechanorg/mctrl_test", True),
            ("create a PR to jleechanorg/worldarchitect.ai", True),
            # Non-cross-repo
            ("fix the bug in this repo", False),
            ("add tests for the new feature", False),
            ("", False),
        ],
    )
    def test_cross_repo_detection(self, task: str, expected: bool):
        """Test cross-repo task detection."""
        assert _is_cross_repo_task(task) is expected

    def test_cross_repo_context_not_empty(self):
        """Test that CROSS_REPO_CONTEXT is defined and non-empty."""
        assert _CROSS_REPO_CONTEXT
        assert "worktree" in _CROSS_REPO_CONTEXT.lower()
        assert "pr" in _CROSS_REPO_CONTEXT.lower()


class TestExtractRepoNameHint:
    """Tests for _extract_repo_name_hint function."""

    @pytest.mark.parametrize(
        "task,expected",
        [
            ("fix in mctrl_test repo", "mctrl_test"),
            ("do something generic", ""),
        ],
    )
    def test_repo_name_extraction(self, task: str, expected: str):
        """Test repo name hint extraction."""
        assert _extract_repo_name_hint(task) == expected
