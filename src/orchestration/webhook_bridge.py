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
