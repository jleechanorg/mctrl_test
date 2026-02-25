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


def notify_mission_control(event: WebhookEvent | str, payload: dict) -> None:
    """POST an event to Mission Control webhook. Best-effort, never blocks.

    Args:
        event: The event type string.
        payload: Dict of event-specific data (agent_name, task, etc.)
    """
    webhook_url = os.environ.get("MISSION_CONTROL_WEBHOOK_URL")
    if not webhook_url:
        return

    try:
        body = json.dumps({"event": str(event), **payload}).encode("utf-8")
        req = Request(
            webhook_url,
            data=body,
            headers={"Content-type": "application/json"},
            method="POST",
        )
        urlopen(req, timeout=5)
    except Exception:
        pass  # Never block orchestration for dashboard
