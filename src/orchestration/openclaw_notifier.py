from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable
from urllib.request import Request, urlopen

# DM channel: jleechan direct message; trigger channel: #ai-slack-test (legacy constant)
SLACK_DM_CHANNEL = "D0AFTLEJGJU"
SLACK_TRIGGER_CHANNEL = "C0AKALZ4CKW"  # #ai-slack-test

EventSender = Callable[[dict[str, Any]], bool]

DEFAULT_OUTBOX_PATH = ".messages/outbox.jsonl"


def _normalize_trigger_ts(value: Any) -> str:
    """Return a usable Slack thread ts, treating None-like values as missing."""
    if value is None:
        return ""
    trigger_ts = str(value).strip()
    if not trigger_ts or trigger_ts.lower() == "none":
        return ""
    return trigger_ts


def _normalize_trigger_channel(value: Any) -> str:
    """Return a usable Slack channel id, treating None-like values as missing."""
    if value is None:
        return ""
    trigger_channel = str(value).strip()
    if not trigger_channel or trigger_channel.lower() == "none":
        return ""
    return trigger_channel


def notify_openclaw(
    payload: dict[str, Any],
    *,
    send_fn: EventSender | None = None,
    outbox_path: str = DEFAULT_OUTBOX_PATH,
) -> bool:
    """Send loopback payload to OpenClaw; fallback to JSONL outbox on failure."""
    sender = send_fn or _send_via_mcp_agent_mail
    try:
        delivered = sender(payload)
    except Exception:
        delivered = False

    if delivered:
        return True

    enqueue_outbox(payload, outbox_path=outbox_path)
    return False


def drain_outbox(
    *,
    send_fn: EventSender | None = None,
    outbox_path: str = DEFAULT_OUTBOX_PATH,
) -> int:
    """Attempt to deliver queued outbox events, returning count delivered.

    Uses an atomic snapshot rename so events enqueued concurrently by
    enqueue_outbox are never overwritten by the rewrite of remaining items.
    """
    sender = send_fn or _send_via_mcp_agent_mail
    path = Path(outbox_path)

    # Atomically take a snapshot: rename the live file so new enqueue_outbox
    # calls write to a fresh file, while we drain from the snapshot only.
    drain_path = path.with_suffix(".drain")
    try:
        os.replace(path, drain_path)
    except FileNotFoundError:
        return 0

    delivered = 0
    remaining: list[dict[str, Any]] = []
    for payload in _parse_jsonl_lines(drain_path.read_text(encoding="utf-8")):
        try:
            ok = sender(payload)
        except Exception:
            ok = False
        if ok:
            delivered += 1
        else:
            remaining.append(payload)

    # Re-enqueue failed items via append so they merge with any new events.
    for item in remaining:
        enqueue_outbox(item, outbox_path=outbox_path)

    try:
        drain_path.unlink()
    except OSError:
        pass

    return delivered


def _parse_jsonl_lines(text: str) -> list[dict[str, Any]]:
    """Parse JSONL text, skipping blank and malformed lines."""
    items: list[dict[str, Any]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except (json.JSONDecodeError, KeyError, ValueError):
            continue
    return items


def enqueue_outbox(payload: dict[str, Any], *, outbox_path: str = DEFAULT_OUTBOX_PATH) -> None:
    normalized_payload = dict(payload)
    if "slack_trigger_ts" in normalized_payload:
        normalized_payload["slack_trigger_ts"] = _normalize_trigger_ts(
            normalized_payload.get("slack_trigger_ts")
        )
    if "slack_trigger_channel" in normalized_payload:
        normalized_payload["slack_trigger_channel"] = _normalize_trigger_channel(
            normalized_payload.get("slack_trigger_channel")
        )
    path = Path(outbox_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(normalized_payload, sort_keys=True))
        fh.write("\n")


def read_outbox(*, outbox_path: str = DEFAULT_OUTBOX_PATH) -> list[dict[str, Any]]:
    path = Path(outbox_path)
    try:
        return _parse_jsonl_lines(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []


def notify_slack_started(payload: dict[str, Any]) -> bool:
    """Post task-started notification to Slack. Best-effort, never blocks.

    Posts a DM to jleechan. If slack_trigger_ts is set, also threads a reply
    under the original trigger message channel/thread.
    """
    token = os.environ.get("OPENCLAW_SLACK_BOT_TOKEN") or os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        return False

    bead_id = str(payload.get("bead_id", "unknown"))
    branch = str(payload.get("branch", "unknown"))
    worktree = str(payload.get("worktree_path", "unknown"))
    session = str(payload.get("session", "unknown"))
    agent_cli = str(payload.get("agent_cli", "unknown"))
    trigger_ts = _normalize_trigger_ts(payload.get("slack_trigger_ts"))
    trigger_channel = _normalize_trigger_channel(payload.get("slack_trigger_channel"))

    dm_text = (
        f":rocket: *Task started: {bead_id}*\n\n"
        f"Agent `{agent_cli}` running in session `{session}`.\n"
        f"Branch: `{branch}`\n"
        f"Worktree: `{worktree}`"
    )
    thread_text = f":rocket: Agent started — *{bead_id}* running in `{session}` on `{branch}`."

    posts: list[dict[str, Any]] = [{"channel": SLACK_DM_CHANNEL, "text": dm_text}]
    if trigger_ts and trigger_channel:
        posts.append({
            "channel": trigger_channel,
            "text": thread_text,
            "thread_ts": trigger_ts,
        })

    success = True
    for post_body in posts:
        try:
            body = json.dumps(post_body).encode("utf-8")
            req = Request(
                "https://slack.com/api/chat.postMessage",
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                },
                method="POST",
            )
            with urlopen(req, timeout=5) as resp:
                result = json.loads(resp.read())
                if not result.get("ok"):
                    success = False
        except Exception:
            success = False
    return success


def notify_slack_done(payload: dict[str, Any]) -> bool:
    """Post task-done notification to Slack. Best-effort, never blocks.

    Posts a DM to jleechan. If slack_trigger_ts is set, also threads a reply
    under the original trigger message channel/thread.
    Uses OPENCLAW_SLACK_BOT_TOKEN only — never falls back to user token.
    """
    # Use bot token only — never fall back to SLACK_USER_TOKEN (that posts as
    # jleechan, not the openclaw bot, which is the wrong sender for completions).
    token = os.environ.get("OPENCLAW_SLACK_BOT_TOKEN") or os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        return False

    bead_id = str(payload.get("bead_id", "unknown"))
    branch = str(payload.get("branch", "unknown"))
    worktree = str(payload.get("worktree_path", "unknown"))
    event = payload.get("event", "task_needs_human")
    session = str(payload.get("session", "unknown"))
    trigger_ts = _normalize_trigger_ts(payload.get("slack_trigger_ts"))
    trigger_channel = _normalize_trigger_channel(payload.get("slack_trigger_channel"))

    if event == "task_finished":
        dm_text = (
            f":white_check_mark: *Task done: {bead_id}*\n\n"
            f"Agent committed work to `{branch}`.\n"
            f"Worktree: `{worktree}`\n"
            f"Review and merge when ready."
        )
        thread_text = f":done: Agent done — *{bead_id}* committed to `{branch}`. Ready for review."
    else:
        # task_needs_human: agent exited without committing (stall/crash/timeout)
        action_required = str(payload.get("action_required", "human_decision"))
        if action_required == "push_or_salvage":
            dm_text = (
                f":warning: *Task stranded: {bead_id}*\n\n"
                f"Agent session `{session}` committed locally but did not push to origin.\n"
                f"Branch: `{branch}`\n"
                f"Worktree: `{worktree}`\n"
                f"Push or salvage the branch before cleanup."
            )
            thread_text = (
                f":warning: Agent for *{bead_id}* committed locally but did not push `{branch}`. "
                "Human follow-up required."
            )
        else:
            dm_text = (
                f":warning: *Task stalled: {bead_id}*\n\n"
                f"Agent session `{session}` exited without committing.\n"
                f"Branch: `{branch}`\n"
                f"Worktree: `{worktree}`\n"
                f"Investigate and relaunch if needed."
            )
            thread_text = f":warning: Agent for *{bead_id}* exited without commits — may need relaunch. Branch: `{branch}`."

    posts: list[dict[str, Any]] = [{"channel": SLACK_DM_CHANNEL, "text": dm_text}]
    # Thread the completion reply under the original trigger message if we have its ts.
    if trigger_ts and trigger_channel:
        posts.append({
            "channel": trigger_channel,
            "text": thread_text,
            "thread_ts": trigger_ts,
        })

    success = True
    for post_body in posts:
        try:
            body = json.dumps(post_body).encode("utf-8")
            req = Request(
                "https://slack.com/api/chat.postMessage",
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                },
                method="POST",
            )
            with urlopen(req, timeout=5) as resp:
                result = json.loads(resp.read())
                if not result.get("ok"):
                    success = False
        except Exception:
            success = False
    return success


def _send_via_mcp_agent_mail(payload: dict[str, Any]) -> bool:
    """Best-effort OpenClaw delivery.

    Preferred env vars:
    - OPENCLAW_NOTIFY_AGENT

    Legacy env vars:
    - OPENCLAW_PROJECT_KEY
    - OPENCLAW_SENDER_NAME
    - OPENCLAW_TO

    We try the live OpenClaw agent route first because current OpenClaw CLI
    builds do not expose an `mcp` subcommand consistently.
    """
    if _send_via_openclaw_agent(payload):
        return True

    project_key = os.environ.get("OPENCLAW_PROJECT_KEY", "").strip()
    sender_name = os.environ.get("OPENCLAW_SENDER_NAME", "").strip()
    to = os.environ.get("OPENCLAW_TO", "").strip()
    if not project_key or not sender_name or not to:
        return False

    event_type = str(payload.get("event", "task_update"))
    bead_id = str(payload.get("bead_id", "unknown"))
    subject = f"{event_type}: {bead_id}"
    body = json.dumps(payload, indent=2, sort_keys=True)

    result = subprocess.run(
        [
            "openclaw",
            "mcp",
            "call",
            "mcp-agent-mail",
            "send_message",
            "--project_key",
            project_key,
            "--sender_name",
            sender_name,
            "--to",
            to,
            "--subject",
            subject,
            "--body_md",
            f"```json\n{body}\n```",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.returncode == 0


def _send_via_openclaw_agent(payload: dict[str, Any]) -> bool:
    """Deliver the notification to a configured OpenClaw agent."""
    agent_name = os.environ.get("OPENCLAW_NOTIFY_AGENT", "").strip()
    if not agent_name:
        return False

    event_type = str(payload.get("event", "task_update"))
    bead_id = str(payload.get("bead_id", "unknown"))
    body = json.dumps(payload, indent=2, sort_keys=True)
    message = (
        f"Notification from mctrl.\n"
        f"Event: {event_type}\n"
        f"Bead: {bead_id}\n\n"
        f"```json\n{body}\n```"
    )
    result = subprocess.run(
        [
            "openclaw",
            "agent",
            "--agent",
            agent_name,
            "--message",
            message,
            "--json",
        ],
        capture_output=True,
        text=True,
        timeout=30,  # Prevent indefinite hang on OpenClaw CLI issues
    )
    if result.returncode != 0:
        return False
    # Validate the JSON response indicates successful delivery, not just clean exit.
    # openclaw --json returns {"success": true} or {"error": "..."} on failure.
    try:
        response = json.loads(result.stdout)
        # Accept if response explicitly says success, or has no error field
        if isinstance(response, dict):
            if response.get("error"):
                return False
            if "success" in response:
                return bool(response["success"])
        # Non-dict or unknown shape but exit 0 — treat as delivered
        return True
    except (json.JSONDecodeError, ValueError, TypeError):
        # stdout wasn't JSON or was None — exit 0 still means delivery command ran
        return True
