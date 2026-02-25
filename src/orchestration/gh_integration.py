"""GitHub SCM integration — ported from agent-orchestrator scm-github plugin.

Uses the `gh` CLI for all GitHub API interactions.
Key design choices preserved from TS original:
- PR detection by branch name (no ID tracking needed)
- Fail-closed error handling (CI fetch failure → "failing" not "none")
- GraphQL `-f` flag for safe variable passing
- BOT_AUTHORS filter for bot comment exclusion
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BOT_AUTHORS = frozenset({
    "cursor[bot]",
    "github-actions[bot]",
    "codecov[bot]",
    "sonarcloud[bot]",
    "dependabot[bot]",
    "renovate[bot]",
    "codeclimate[bot]",
    "deepsource-autofix[bot]",
    "snyk-bot",
    "lgtm-com[bot]",
})


class CIStatus(StrEnum):
    PASSING = "passing"
    FAILING = "failing"
    PENDING = "pending"
    NONE = "none"


class ReviewDecision(StrEnum):
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    PENDING = "pending"
    NONE = "none"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class PRInfo:
    """Pull request information."""
    number: int
    url: str
    title: str
    owner: str
    repo: str
    branch: str
    base_branch: str
    is_draft: bool


@dataclass
class MergeReadiness:
    """Aggregated merge readiness result."""
    mergeable: bool
    ci_passing: bool
    approved: bool
    no_conflicts: bool
    blockers: list[str]


# ---------------------------------------------------------------------------
# gh CLI wrapper
# ---------------------------------------------------------------------------


def gh(args: list[str]) -> str:
    """Run a `gh` CLI command and return stdout.

    Raises RuntimeError on non-zero exit.
    """
    try:
        result = subprocess.run(
            ["gh", *args],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"gh {' '.join(args[:3])} failed: {exc.stderr or exc}"
        ) from exc


def _repo_flag(pr: PRInfo) -> str:
    return f"{pr.owner}/{pr.repo}"


# ---------------------------------------------------------------------------
# PR detection
# ---------------------------------------------------------------------------


def detect_pr(branch: str, repo: str) -> Optional[PRInfo]:
    """Find a PR by branch name.

    Args:
        branch: The head branch name.
        repo: Repository in "owner/repo" format.

    Returns:
        PRInfo if found, None otherwise.
    """
    parts = repo.split("/")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(f'Invalid repo format "{repo}", expected "owner/repo"')

    owner, repo_name = parts
    try:
        raw = gh([
            "pr", "list",
            "--repo", repo,
            "--head", branch,
            "--json", "number,url,title,headRefName,baseRefName,isDraft",
            "--limit", "1",
        ])
        prs = json.loads(raw)
        if not prs:
            return None

        pr = prs[0]
        return PRInfo(
            number=pr["number"],
            url=pr["url"],
            title=pr["title"],
            owner=owner,
            repo=repo_name,
            branch=pr["headRefName"],
            base_branch=pr["baseRefName"],
            is_draft=pr["isDraft"],
        )
    except (RuntimeError, json.JSONDecodeError, KeyError):
        return None


# ---------------------------------------------------------------------------
# PR state
# ---------------------------------------------------------------------------


def get_pr_state(pr: PRInfo) -> str:
    """Get PR state: 'open', 'merged', or 'closed'."""
    raw = gh([
        "pr", "view", str(pr.number),
        "--repo", _repo_flag(pr),
        "--json", "state",
    ])
    data = json.loads(raw)
    state = data["state"].upper()
    if state == "MERGED":
        return "merged"
    if state == "CLOSED":
        return "closed"
    return "open"


# ---------------------------------------------------------------------------
# CI checks
# ---------------------------------------------------------------------------


def get_ci_checks(pr: PRInfo) -> list[dict]:
    """Get CI checks for a PR. Fail-closed: errors propagate.

    Returns list of dicts with keys: name, status, url, conclusion.
    """
    raw = gh([
        "pr", "checks", str(pr.number),
        "--repo", _repo_flag(pr),
        "--json", "name,state,link,startedAt,completedAt",
    ])
    checks = json.loads(raw)

    result = []
    for c in checks:
        state = (c.get("state") or "").upper()
        if state in ("PENDING", "QUEUED"):
            status = "pending"
        elif state == "IN_PROGRESS":
            status = "running"
        elif state == "SUCCESS":
            status = "passed"
        elif state in ("FAILURE", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED"):
            status = "failed"
        elif state in ("SKIPPED", "NEUTRAL"):
            status = "skipped"
        else:
            status = "failed"  # Fail closed for unknown states

        result.append({
            "name": c["name"],
            "status": status,
            "url": c.get("link") or None,
            "conclusion": state or None,
        })

    return result


def get_ci_summary(pr: PRInfo) -> CIStatus:
    """Aggregate CI status. Fail-closed for open PRs.

    Returns CIStatus enum value.
    """
    try:
        checks = get_ci_checks(pr)
    except RuntimeError:
        # Before fail-closing, check if PR is merged/closed
        try:
            state = get_pr_state(pr)
            if state in ("merged", "closed"):
                return CIStatus.NONE
        except RuntimeError:
            pass
        # Fail closed for open PRs
        return CIStatus.FAILING

    if not checks:
        return CIStatus.NONE

    if any(c["status"] == "failed" for c in checks):
        return CIStatus.FAILING

    if any(c["status"] in ("pending", "running") for c in checks):
        return CIStatus.PENDING

    if any(c["status"] == "passed" for c in checks):
        return CIStatus.PASSING

    return CIStatus.NONE


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------


def get_reviews(pr: PRInfo) -> list[dict]:
    """Get review list for a PR."""
    raw = gh([
        "pr", "view", str(pr.number),
        "--repo", _repo_flag(pr),
        "--json", "reviews",
    ])
    data = json.loads(raw)

    result = []
    for r in data.get("reviews", []):
        state_raw = (r.get("state") or "").upper()
        state_map = {
            "APPROVED": "approved",
            "CHANGES_REQUESTED": "changes_requested",
            "DISMISSED": "dismissed",
            "PENDING": "pending",
        }
        state = state_map.get(state_raw, "commented")

        result.append({
            "author": r.get("author", {}).get("login", "unknown"),
            "state": state,
            "body": r.get("body") or None,
            "submitted_at": r.get("submittedAt"),
        })

    return result


def get_review_decision(pr: PRInfo) -> ReviewDecision:
    """Get the aggregate review decision."""
    raw = gh([
        "pr", "view", str(pr.number),
        "--repo", _repo_flag(pr),
        "--json", "reviewDecision",
    ])
    data = json.loads(raw)
    decision = (data.get("reviewDecision") or "").upper()

    if decision == "APPROVED":
        return ReviewDecision.APPROVED
    if decision == "CHANGES_REQUESTED":
        return ReviewDecision.CHANGES_REQUESTED
    if decision == "REVIEW_REQUIRED":
        return ReviewDecision.PENDING
    return ReviewDecision.NONE


# ---------------------------------------------------------------------------
# Pending comments (GraphQL)
# ---------------------------------------------------------------------------


def get_pending_comments(pr: PRInfo) -> list[dict]:
    """Get unresolved review threads, excluding bot comments.

    Uses GraphQL with -f flag for injection-safe variable passing.
    """
    try:
        raw = gh([
            "api", "graphql",
            "-f", f"owner={pr.owner}",
            "-f", f"name={pr.repo}",
            "-F", f"number={pr.number}",
            "-f", (
                "query=query($owner: String!, $name: String!, $number: Int!) {"
                "  repository(owner: $owner, name: $name) {"
                "    pullRequest(number: $number) {"
                "      reviewThreads(first: 100) {"
                "        nodes {"
                "          isResolved"
                "          comments(first: 1) {"
                "            nodes {"
                "              id"
                "              author { login }"
                "              body"
                "              path"
                "              line"
                "              url"
                "              createdAt"
                "            }"
                "          }"
                "        }"
                "      }"
                "    }"
                "  }"
                "}"
            ),
        ])
        data = json.loads(raw)
        threads = data["data"]["repository"]["pullRequest"]["reviewThreads"]["nodes"]

        result = []
        for t in threads:
            if t["isResolved"]:
                continue
            comments = t["comments"]["nodes"]
            if not comments:
                continue
            c = comments[0]
            author = (c.get("author") or {}).get("login", "unknown")
            if author in BOT_AUTHORS:
                continue
            result.append({
                "id": c["id"],
                "author": author,
                "body": c["body"],
                "path": c.get("path") or None,
                "line": c.get("line"),
                "is_resolved": t["isResolved"],
                "created_at": c.get("createdAt"),
                "url": c.get("url"),
            })

        return result
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Merge readiness
# ---------------------------------------------------------------------------


def get_merge_readiness(pr: PRInfo) -> MergeReadiness:
    """Aggregate CI + approvals + conflicts into merge readiness.

    Returns MergeReadiness with blockers list.
    """
    # Merged PRs are always "ready"
    state = get_pr_state(pr)
    if state == "merged":
        return MergeReadiness(
            mergeable=True,
            ci_passing=True,
            approved=True,
            no_conflicts=True,
            blockers=[],
        )

    blockers: list[str] = []

    # Fetch PR merge details
    raw = gh([
        "pr", "view", str(pr.number),
        "--repo", _repo_flag(pr),
        "--json", "mergeable,reviewDecision,mergeStateStatus,isDraft",
    ])
    data = json.loads(raw)

    # CI
    ci_status = get_ci_summary(pr)
    ci_passing = ci_status in (CIStatus.PASSING, CIStatus.NONE)
    if not ci_passing:
        blockers.append(f"CI is {ci_status}")

    # Reviews
    review_decision = (data.get("reviewDecision") or "").upper()
    approved = review_decision == "APPROVED"
    if review_decision == "CHANGES_REQUESTED":
        blockers.append("Changes requested in review")
    elif review_decision == "REVIEW_REQUIRED":
        blockers.append("Review required")

    # Conflicts
    mergeable = (data.get("mergeable") or "").upper()
    merge_state = (data.get("mergeStateStatus") or "").upper()
    no_conflicts = mergeable == "MERGEABLE"
    if mergeable == "CONFLICTING":
        blockers.append("Merge conflicts")
    elif mergeable in ("UNKNOWN", ""):
        blockers.append("Merge status unknown (GitHub is computing)")
    if merge_state == "BEHIND":
        blockers.append("Branch is behind base branch")
    elif merge_state == "BLOCKED":
        blockers.append("Merge is blocked by branch protection")
    elif merge_state == "UNSTABLE":
        blockers.append("Required checks are failing")

    # Draft
    if data.get("isDraft"):
        blockers.append("PR is still a draft")

    return MergeReadiness(
        mergeable=len(blockers) == 0,
        ci_passing=ci_passing,
        approved=approved,
        no_conflicts=no_conflicts,
        blockers=blockers,
    )


# ---------------------------------------------------------------------------
# PR write operations
# ---------------------------------------------------------------------------


def merge_pr(pr: PRInfo, method: str = "squash") -> None:
    """Merge a PR. Default squash merge with branch deletion.

    Args:
        pr: The PR to merge.
        method: 'squash', 'rebase', or 'merge'.
    """
    flag = {"rebase": "--rebase", "merge": "--merge"}.get(method, "--squash")
    gh(["pr", "merge", str(pr.number), "--repo", _repo_flag(pr), flag, "--delete-branch"])


def close_pr(pr: PRInfo) -> None:
    """Close a PR without merging."""
    gh(["pr", "close", str(pr.number), "--repo", _repo_flag(pr)])


# ---------------------------------------------------------------------------
# PR summary
# ---------------------------------------------------------------------------


def get_pr_summary(pr: PRInfo) -> dict:
    """Get PR summary with additions/deletions."""
    raw = gh([
        "pr", "view", str(pr.number),
        "--repo", _repo_flag(pr),
        "--json", "state,title,additions,deletions",
    ])
    data = json.loads(raw)
    state_raw = data["state"].upper()
    state = "merged" if state_raw == "MERGED" else "closed" if state_raw == "CLOSED" else "open"
    return {
        "state": state,
        "title": data.get("title", ""),
        "additions": data.get("additions", 0),
        "deletions": data.get("deletions", 0),
    }


# ---------------------------------------------------------------------------
# Automated comments
# ---------------------------------------------------------------------------


def get_automated_comments(pr: PRInfo) -> list[dict]:
    """Get bot/automated review comments via REST API.

    Filters to only BOT_AUTHORS. Infers severity from body content.
    """
    try:
        raw = gh([
            "api",
            "-F", "per_page=100",
            f"repos/{_repo_flag(pr)}/pulls/{pr.number}/comments",
        ])
        comments = json.loads(raw)

        result = []
        for c in comments:
            login = (c.get("user") or {}).get("login", "")
            if login not in BOT_AUTHORS:
                continue

            # Determine severity from body
            body_lower = (c.get("body") or "").lower()
            if any(k in body_lower for k in ("error", "bug", "critical", "potential issue")):
                severity = "error"
            elif any(k in body_lower for k in ("warning", "suggest", "consider")):
                severity = "warning"
            else:
                severity = "info"

            result.append({
                "id": str(c["id"]),
                "bot_name": login,
                "body": c.get("body", ""),
                "path": c.get("path") or None,
                "line": c.get("line") or c.get("original_line"),
                "severity": severity,
                "created_at": c.get("created_at"),
                "url": c.get("html_url"),
            })

        return result
    except Exception:
        return []

