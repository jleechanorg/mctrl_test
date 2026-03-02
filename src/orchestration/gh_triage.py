"""GitHub notification triage.

Fetches GitHub notifications, filters actionable ones, evaluates merge readiness,
and creates Mission Control tasks for follow-up work.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Callable, Iterable

from orchestration.gh_integration import PRInfo, MergeReadiness, gh, get_merge_readiness
from orchestration.mc_client import MissionControlClient

logger = logging.getLogger(__name__)

DEFAULT_ACTIONABLE_REASONS: frozenset[str] = frozenset(
    {
        "review_requested",
        "ci_activity",
        "security_alert",
        "mention",
        "state_change",
    },
)


def _normalize_repo(notification: dict) -> str | None:
    """Return owner/repo from a GH notification payload."""
    repo = notification.get("repository") or {}
    if not isinstance(repo, dict):
        return None

    name_with_owner = repo.get("nameWithOwner")
    if isinstance(name_with_owner, str) and "/" in name_with_owner:
        return name_with_owner

    owner = repo.get("owner")
    if isinstance(owner, dict):
        owner_login = owner.get("login")
        if isinstance(owner_login, str):
            owner = owner_login
    if not isinstance(owner, str):
        owner = ""
    repo_name = repo.get("name", "")
    if not owner or not repo_name:
        return None
    return f"{owner}/{repo_name}"


def _extract_pull_number(subject_url: str) -> int | None:
    """Extract PR number from a notification subject URL."""
    for marker in ("/pulls/", "/pull/"):
        if marker not in subject_url:
            continue
        tail = subject_url.split(marker, 1)[1]
        candidate = re.split(r"[/?#]", tail, maxsplit=1)[0]
        if candidate.isdigit():
            return int(candidate)
    return None


def _notification_to_pr_info(notification: dict) -> PRInfo | None:
    """Build a PRInfo object from a GH notification payload."""
    subject = notification.get("subject") or {}
    if not isinstance(subject, dict):
        return None
    if (subject.get("type") or "").lower() != "pullrequest":
        return None

    repo = _normalize_repo(notification)
    if not isinstance(repo, str) or "/" not in repo:
        return None
    owner, repo_name = repo.split("/", 1)

    subject_url = subject.get("url")
    if not isinstance(subject_url, str):
        return None
    number = _extract_pull_number(subject_url)
    if not number:
        return None

    return PRInfo(
        number=number,
        url=subject_url,
        title=(subject.get("title") or "Pull request"),
        owner=owner,
        repo=repo_name,
        branch="",
        base_branch="",
        is_draft=False,
    )


def _build_task_payload(
    notification: dict,
    pr: PRInfo,
    reason: str,
    readiness: MergeReadiness,
    board_id: str,
) -> dict:
    """Build a Mission Control task payload for a triaged notification."""
    blockers = readiness.blockers or ["No blockers."]
    description = "\n".join([
        f"Repository: {pr.owner}/{pr.repo}",
        f"Reason: {reason}",
        f"PR #{pr.number}: {pr.url}",
        f"Merge ready: {'yes' if readiness.mergeable else 'no'}",
        "",
        "Blockers:",
        *blockers,
        "",
        f"CI passing: {readiness.ci_passing}",
        f"Approved: {readiness.approved}",
        f"No conflicts: {readiness.no_conflicts}",
    ])

    return {
        "board_id": board_id,
        "title": f"[{reason}] {pr.title}",
        "description": description,
        "status": "inbox",
        "source": "github_notification",
        "custom_fields": {
            "notification_id": notification.get("id"),
            "notification_reason": reason,
            "pr_number": pr.number,
            "repo": f"{pr.owner}/{pr.repo}",
            "merge_ready": readiness.mergeable,
            "ci_passing": readiness.ci_passing,
            "approved": readiness.approved,
            "no_conflicts": readiness.no_conflicts,
            "blockers": blockers,
        },
    }


def _load_notifications(
    gh_fn: Callable[[list[str]], str] = gh,
) -> list[dict]:
    """Load GitHub notifications payload."""
    try:
        raw = gh_fn([
            "api",
            "notifications",
            "--json",
            "id,reason,subject,repository",
        ])
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def triage_github_notifications(
    board_id: str,
    client: MissionControlClient,
    *,
    reasons: Iterable[str] | None = None,
    gh_fn: Callable[[list[str]], str] | None = None,
    readiness_fn: Callable[[PRInfo], MergeReadiness] | None = None,
) -> list[dict]:
    """Create Mission Control tasks from actionable GitHub notifications.

    Args:
        board_id: Mission Control board UUID.
        client: MissionControlClient instance.
        reasons: Optional override for actionable notification reasons.
        gh_fn: Optional custom GitHub command function.
        readiness_fn: Optional custom readiness function.

    Returns:
        List of created Mission Control tasks (as returned by client).
    """
    if not client or not client.is_configured:
        return []

    readiness_fn = readiness_fn or get_merge_readiness
    gh_fn = gh_fn or gh
    actionable_reasons = set(reasons or DEFAULT_ACTIONABLE_REASONS)
    created: list[dict] = []

    for notification in _load_notifications(gh_fn=gh_fn):
        if not isinstance(notification, dict):
            continue

        reason = notification.get("reason")
        if reason not in actionable_reasons:
            continue

        pr = _notification_to_pr_info(notification)
        if pr is None:
            continue

        try:
            readiness = readiness_fn(pr)
        except Exception:
            logger.exception("Failed to evaluate merge readiness for notification %s", notification.get("id"))
            continue

        payload = _build_task_payload(notification, pr, str(reason), readiness, board_id)
        created_task = client.create_task(payload)
        if isinstance(created_task, dict):
            created.append(created_task)

    return created

