"""Security-focused checks for the PR agent trigger workflow."""

from __future__ import annotations

from pathlib import Path


def _workflow_text() -> str:
    repo_root = Path(__file__).resolve().parents[2]
    return (repo_root / ".github" / "workflows" / "pr-agent-trigger.yml").read_text(
        encoding="utf-8"
    )


def test_workflow_restricts_to_pr_comments_and_trusted_actors() -> None:
    text = _workflow_text()
    assert "github.event.issue.pull_request" in text
    assert "github.event.comment.author_association" in text


def test_workflow_avoids_direct_shell_interpolation_for_comment_body() -> None:
    text = _workflow_text()
    assert 'COMMENT_BODY="${{ github.event.comment.body }}"' not in text
    assert "COMMENT_BODY: ${{ github.event.comment.body }}" in text


def test_workflow_uses_json_safe_payload_construction() -> None:
    text = _workflow_text()
    assert "jq -n" in text


def test_workflow_declares_least_privilege_permissions() -> None:
    text = _workflow_text()
    assert "permissions:" in text
    assert "contents: read" in text
    assert "issues: read" in text
    assert "pull-requests: read" in text


def test_workflow_avoids_xargs_on_untrusted_comment_body() -> None:
    text = _workflow_text()
    assert "xargs" not in text
