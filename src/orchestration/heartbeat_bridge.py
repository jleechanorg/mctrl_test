"""Heartbeat bridge — syncs tmux agent sessions to Mission Control.

Periodically lists running tmux sessions and POSTs heartbeats.
Detects disappeared sessions and reports agent_failed events.
"""

from __future__ import annotations

import json
import os
import subprocess
from urllib.request import Request, urlopen


# ---------------------------------------------------------------------------
# tmux session listing
# ---------------------------------------------------------------------------


def list_tmux_sessions() -> list[str]:
    """List running tmux session names.

    Returns empty list if tmux is not installed or no server is running.
    """
    try:
        result = subprocess.run(
            ["tmux", "list-sessions", "-F", "#{session_name}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return []
        return [s.strip() for s in result.stdout.strip().split("\n") if s.strip()]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


# ---------------------------------------------------------------------------
# Heartbeat bridge
# ---------------------------------------------------------------------------


class HeartbeatBridge:
    """Tracks tmux agent sessions and detects changes."""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.known_agents: set[str] = set()

    def update_known(self, agents: list[str]) -> None:
        """Update the set of known agents."""
        self.known_agents = set(agents)

    def detect_disappeared(self, current: list[str]) -> set[str]:
        """Detect agents that disappeared since last check."""
        return self.known_agents - set(current)

    def detect_new(self, current: list[str]) -> set[str]:
        """Detect new agents since last check."""
        return set(current) - self.known_agents


# ---------------------------------------------------------------------------
# Sync function
# ---------------------------------------------------------------------------


def sync_agents_to_mission_control() -> None:
    """One-shot sync: list tmux sessions, POST heartbeats.

    Reads MISSION_CONTROL_WEBHOOK_URL from env. Silent on failure.
    """
    webhook_url = os.environ.get("MISSION_CONTROL_WEBHOOK_URL")
    if not webhook_url:
        return

    sessions = list_tmux_sessions()
    if not sessions:
        return

    for session_name in sessions:
        try:
            body = json.dumps({
                "event": "agent_heartbeat",
                "agent_name": session_name,
            }).encode("utf-8")
            req = Request(
                webhook_url,
                data=body,
                headers={"Content-type": "application/json"},
                method="POST",
            )
            urlopen(req, timeout=5)
        except Exception:
            pass  # Never block — fire and forget
