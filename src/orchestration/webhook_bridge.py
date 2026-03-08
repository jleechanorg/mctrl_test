"""Webhook bridge — fire-and-forget Mission Control notifier.

Design principle: NEVER block orchestration for dashboard.
If Mission Control is down, this is a silent no-op.
"""

from __future__ import annotations

import json
import os
from enum import StrEnum
from urllib.request import Request, urlopen


class WebhookEvent(StrEnum):
    """Events emitted to Mission Control."""
    AGENT_STARTED = "agent_started"
    AGENT_FAILED = "agent_failed"
    TASK_COMPLETE = "task_complete"
    AGENT_KILLED = "agent_killed"

    # Hook event used by PostToolUse integration
    TOOL_USE = "tool_use"


def _parse_tool_use_command(payload: dict) -> str:
    """Extract a shell command from Claude PostToolUse payload."""
    tool_name = (payload.get("tool_name") or payload.get("toolName") or "").lower()
    if tool_name not in {"bash", "shell", "terminal"}:
        return ""

    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        tool_input = {}

    command = (
        payload.get("command")
        or tool_input.get("command")
        or tool_input.get("cmd")
        or ""
    )
    return str(command).strip()


def _is_shell_command_of_interest(command: str) -> bool:
    """Return true when command should be sent to Mission Control."""
    lowered = command.strip().lower()
    if not lowered:
        return False
    return lowered.startswith("git ") or lowered.startswith("gh ")


def notify_tool_use(
    payload: str | dict,
    webhook_url: str | None = None,
    repo: str | None = None,
) -> bool:
    """Post a PostToolUse payload to webhook when command is git/gh.

    Returns True when an event is sent, False when filtered out.
    """
    if isinstance(payload, str):
        try:
            payload_obj = json.loads(payload)
        except json.JSONDecodeError:
            return False
    else:
        payload_obj = payload

    if not isinstance(payload_obj, dict):
        return False

    command = _parse_tool_use_command(payload_obj)
    if not _is_shell_command_of_interest(command):
        return False

    notify_mission_control(
        WebhookEvent.TOOL_USE,
        {
            "agent_name": payload_obj.get("agent_name", "claude-hook"),
            "tool_name": payload_obj.get("tool_name") or payload_obj.get("tool"),
            "command": command,
            "raw": payload_obj,
        },
        webhook_url=webhook_url,
        repo=repo,
    )
    return True


def notify_mission_control(
    event: WebhookEvent | str,
    payload: dict,
    webhook_url: str | None = None,
    repo: str | None = None,
) -> None:
    """POST an event to Mission Control webhook. Best-effort, never blocks.

    Args:
        event: The event type string.
        payload: Dict of event-specific data (agent_name, task, etc.)
        webhook_url: Optional explicit URL. Falls back to env var.
        repo: Optional repo field to include on payload.
    """
    webhook_url = webhook_url or os.environ.get("MISSION_CONTROL_WEBHOOK_URL")
    if not webhook_url:
        return

    try:
        body_payload = {"event": str(event), **payload}
        if repo is not None:
            body_payload["repo"] = repo
        body = json.dumps(body_payload).encode("utf-8")
        req = Request(
            webhook_url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req, timeout=5) as resp:
            resp.read()  # Drain response to fully close connection
    except Exception:
        pass  # Never block orchestration for dashboard


# ---------------------------------------------------------------------------
# GitHub event bridge (webhook-first with polling fallback)
# ---------------------------------------------------------------------------


TRUSTED_AUTHOR_ASSOCIATIONS: frozenset[str] = frozenset({
    "OWNER",
    "MEMBER",
    "COLLABORATOR",
})


class GitHubEventMode(StrEnum):
    """How GitHub events are received by the pipeline."""

    WEBHOOK = "webhook"
    POLLING = "polling"


def receive_github_event(
    payload: dict,
    event_type: str,
    *,
    trusted_associations: frozenset[str] | None = None,
    webhook_secret: str | None = None,
    signature_header: str | None = None,
    raw_body: bytes | None = None,
) -> dict | None:
    """Normalize an incoming GitHub webhook payload into a pipeline event."""
    import hashlib
    import hmac

    from orchestration.gh_integration import (
        parse_github_webhook_actor,
        parse_github_webhook_author_association,
        parse_github_webhook_pr_number,
        parse_github_webhook_repo,
    )

    secret = webhook_secret or os.environ.get("GITHUB_WEBHOOK_SECRET")
    if secret:
        # Use 'is None' to allow empty body (b"") while rejecting missing body
        if signature_header is None or raw_body is None:
            return None
        try:
            expected = "sha256=" + hmac.new(
                secret.encode(), raw_body, hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(expected, signature_header):
                return None
        except Exception:
            return None

    supported_events = {"issue_comment", "pull_request_review", "pull_request"}
    if event_type not in supported_events:
        return None

    pr_number = parse_github_webhook_pr_number(payload)
    if not pr_number:
        return None

    repo = parse_github_webhook_repo(payload)
    if not repo:
        return None

    actor = parse_github_webhook_actor(payload)
    author_association = parse_github_webhook_author_association(payload)

    if event_type == "issue_comment":
        allowed = TRUSTED_AUTHOR_ASSOCIATIONS if trusted_associations is None else trusted_associations
        if author_association not in allowed:
            return None

    return {
        "event_type": event_type,
        "pr_number": pr_number,
        "repo": repo,
        "actor": actor,
        "author_association": author_association,
        "raw": payload,
    }


def current_github_event_mode() -> GitHubEventMode:
    """Return active GitHub event mode based on webhook secret presence."""
    return GitHubEventMode.WEBHOOK if os.environ.get("GITHUB_WEBHOOK_SECRET") else GitHubEventMode.POLLING
