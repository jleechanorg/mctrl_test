"""Heartbeat bridge — syncs tmux agent sessions to Mission Control.

Periodically lists running tmux sessions and POSTs heartbeats.
Detects disappeared sessions and emits agent_failed events via webhook.
Detects new sessions and emits agent_started events via webhook.
"""

from __future__ import annotations

import json
import os
import subprocess
import threading
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


def _post_event(webhook_url: str, event: str, agent_name: str) -> None:
    """POST a single event to Mission Control. Silent on failure."""
    try:
        body = json.dumps({
            "event": event,
            "agent_name": agent_name,
        }).encode("utf-8")
        req = Request(
            webhook_url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req, timeout=5) as resp:
            resp.read()
    except Exception:
        pass  # Never block — fire and forget


def sync_agents_to_mission_control(webhook_url: str | None = None) -> None:
    """One-shot sync: list tmux sessions, POST heartbeats.

    Args:
        webhook_url: Optional explicit URL. Falls back to env var.
    """
    url = webhook_url or os.environ.get("MISSION_CONTROL_WEBHOOK_URL")
    if not url:
        return

    sessions = list_tmux_sessions()
    if not sessions:
        return

    for session_name in sessions:
        _post_event(url, "agent_heartbeat", session_name)


# ---------------------------------------------------------------------------
# Heartbeat poller — threaded polling loop
# ---------------------------------------------------------------------------


class HeartbeatPoller:
    """Threaded polling loop for heartbeat syncing.

    Periodically lists tmux sessions, detects disappeared/new agents,
    emits agent_failed/agent_started events, and syncs heartbeats.
    Start/stop are idempotent.
    """

    def __init__(self, webhook_url: str, interval_seconds: int = 60):
        self.webhook_url = webhook_url
        self.interval_seconds = interval_seconds
        self.bridge = HeartbeatBridge(webhook_url=webhook_url)
        self._running = False
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self) -> None:
        """Start the polling loop in a daemon thread."""
        if self._running:
            return
        self._stop_event.clear()
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the polling loop."""
        if not self._running:
            return
        self._stop_event.set()
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None

    def _run(self) -> None:
        """Internal polling loop — syncs tmux sessions at interval."""
        while not self._stop_event.is_set():
            try:
                sessions = list_tmux_sessions()

                # Emit agent_failed for disappeared sessions
                disappeared = self.bridge.detect_disappeared(sessions)
                for agent in disappeared:
                    _post_event(self.webhook_url, "agent_failed", agent)

                # Emit agent_started for new sessions
                new = self.bridge.detect_new(sessions)
                for agent in new:
                    _post_event(self.webhook_url, "agent_started", agent)

                self.bridge.update_known(sessions)

                # POST heartbeats for all live sessions
                sync_agents_to_mission_control(webhook_url=self.webhook_url)
            except Exception:
                pass  # Never crash the polling loop
            self._stop_event.wait(self.interval_seconds)
