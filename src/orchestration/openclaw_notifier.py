from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass
from errno import EAGAIN, ECONNREFUSED, ECONNRESET, EHOSTUNREACH, ENETUNREACH, ETIMEDOUT
from pathlib import Path
from typing import Any, Callable

@dataclass(frozen=True)
class DeliveryAttempt:
    delivered: bool
    transient: bool = False


EventSender = Callable[[dict[str, Any]], bool | DeliveryAttempt]

_TRANSIENT_ERROR_MARKERS = (
    "server_error",
    "timeout",
    "timed out",
    "temporarily unavailable",
    "temporary unavailable",
    "rate limit",
    "rate_limit",
    "too many requests",
    "429",
    "503",
    "504",
    "overloaded",
    "try again",
)
_RETRY_DELAYS_SECONDS = (1, 3)
_OPENCLAW_AGENT_TIMEOUT_SECONDS = 60
_OPENCLAW_MCP_TIMEOUT_SECONDS = 30
_DEFAULT_NOTIFY_AGENT = "main"
_DEFAULT_NOTIFY_CHANNEL = "slack"
# jleechan direct-message channel (documented in openclaw-config/SOUL.md).
_DEFAULT_NOTIFY_TARGET = "D0AFTLEJGJU"


def openclaw_notification_max_runtime_seconds() -> int:
    attempts = len(_RETRY_DELAYS_SECONDS) + 1
    per_attempt_timeout = _OPENCLAW_AGENT_TIMEOUT_SECONDS + _OPENCLAW_MCP_TIMEOUT_SECONDS
    return (per_attempt_timeout * attempts) + sum(_RETRY_DELAYS_SECONDS)


def default_outbox_path() -> str:
    explicit_outbox = os.environ.get("MCTRL_OUTBOX_PATH", "").strip()
    if explicit_outbox:
        return str(Path(explicit_outbox).expanduser())
    mctrl_home = Path(os.environ.get("MCTRL_HOME", "~/.mctrl")).expanduser()
    return str(mctrl_home / "messages" / "outbox.jsonl")


def _resolve_outbox_path(outbox_path: str | None) -> str:
    return outbox_path or default_outbox_path()


def _normalize_trigger_ts(value: Any) -> str:
    if value is None:
        return ""
    trigger_ts = str(value).strip()
    if not trigger_ts or trigger_ts.lower() == "none":
        return ""
    return trigger_ts


def _normalize_trigger_channel(value: Any) -> str:
    if value is None:
        return ""
    trigger_channel = str(value).strip()
    if not trigger_channel or trigger_channel.lower() == "none":
        return ""
    return trigger_channel


def _coerce_delivery_attempt(result: bool | DeliveryAttempt) -> DeliveryAttempt:
    if isinstance(result, DeliveryAttempt):
        return result
    return DeliveryAttempt(delivered=bool(result))


def _is_transient_error_text(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in _TRANSIENT_ERROR_MARKERS)


def _is_transient_exception(exc: Exception) -> bool:
    if isinstance(exc, (subprocess.TimeoutExpired, TimeoutError, ConnectionError)):
        return True
    if isinstance(exc, OSError):
        return exc.errno in {
            EAGAIN,
            ECONNREFUSED,
            ECONNRESET,
            EHOSTUNREACH,
            ENETUNREACH,
            ETIMEDOUT,
        }
    return False


def _send_with_retries(
    payload: dict[str, Any],
    *,
    sender: EventSender,
    sleep_fn: Callable[[float], None] | None = None,
) -> DeliveryAttempt:
    retry_sleep = sleep_fn or time.sleep
    for attempt_index in range(len(_RETRY_DELAYS_SECONDS) + 1):
        try:
            attempt = _coerce_delivery_attempt(sender(payload))
        except Exception as exc:
            transient = _is_transient_exception(exc)
            transient = transient or _is_transient_error_text(str(exc))
            attempt = DeliveryAttempt(delivered=False, transient=transient)
        if attempt.delivered:
            return attempt
        if not attempt.transient or attempt_index >= len(_RETRY_DELAYS_SECONDS):
            return attempt
        retry_sleep(_RETRY_DELAYS_SECONDS[attempt_index])
    return DeliveryAttempt(delivered=False, transient=False)


def notify_openclaw(
    payload: dict[str, Any],
    *,
    send_fn: EventSender | None = None,
    outbox_path: str | None = None,
) -> bool:
    """Send loopback payload to OpenClaw; fallback to JSONL outbox on failure."""
    sender = send_fn or _send_via_mcp_agent_mail
    attempt = _send_with_retries(payload, sender=sender)
    if attempt.delivered:
        return True

    enqueue_outbox(payload, outbox_path=outbox_path)
    return False


def drain_outbox(
    *,
    send_fn: EventSender | None = None,
    outbox_path: str | None = None,
) -> int:
    """Attempt to deliver queued outbox events, returning count delivered.

    Uses an atomic snapshot rename so events enqueued concurrently by
    enqueue_outbox are never overwritten by the rewrite of remaining items.
    """
    sender = send_fn or _send_via_mcp_agent_mail
    path = Path(_resolve_outbox_path(outbox_path))

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
            ok = _send_with_retries(payload, sender=sender).delivered
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


def enqueue_outbox(payload: dict[str, Any], *, outbox_path: str | None = None) -> None:
    path = Path(_resolve_outbox_path(outbox_path))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, sort_keys=True))
        fh.write("\n")


def read_outbox(*, outbox_path: str | None = None) -> list[dict[str, Any]]:
    path = Path(_resolve_outbox_path(outbox_path))
    try:
        return _parse_jsonl_lines(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []


def _send_via_mcp_agent_mail(payload: dict[str, Any]) -> DeliveryAttempt:
    """Best-effort OpenClaw delivery.

    Preferred env vars:
    - OPENCLAW_NOTIFY_AGENT

    Legacy env vars:
    - OPENCLAW_PROJECT_KEY
    - OPENCLAW_SENDER_NAME
    - OPENCLAW_TO

    Prefer direct OpenClaw message-send first so Slack delivery is deterministic
    (DM + optional thread reply). Fall back to the live OpenClaw agent route,
    then legacy MCP send_message as last resort.
    """
    message_attempt = _send_via_openclaw_message_channel(payload)
    if message_attempt.delivered:
        return message_attempt

    try:
        agent_attempt = _send_via_openclaw_agent(payload)
    except Exception as exc:
        transient = isinstance(exc, (subprocess.TimeoutExpired, TimeoutError))
        transient = transient or _is_transient_error_text(str(exc))
        agent_attempt = DeliveryAttempt(delivered=False, transient=transient)
    if agent_attempt.delivered:
        return agent_attempt

    project_key = os.environ.get("OPENCLAW_PROJECT_KEY", "").strip()
    sender_name = os.environ.get("OPENCLAW_SENDER_NAME", "").strip()
    to = os.environ.get("OPENCLAW_TO", "").strip()
    if not project_key or not sender_name or not to:
        return agent_attempt

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
        timeout=_OPENCLAW_MCP_TIMEOUT_SECONDS,
    )
    error_text = "\n".join(part for part in (result.stdout, result.stderr) if part).strip()
    fallback_attempt = DeliveryAttempt(
        delivered=result.returncode == 0,
        transient=_is_transient_error_text(error_text),
    )
    if fallback_attempt.delivered:
        return fallback_attempt
    return DeliveryAttempt(
        delivered=False,
        transient=agent_attempt.transient or message_attempt.transient or fallback_attempt.transient,
    )


def _send_via_openclaw_agent(payload: dict[str, Any]) -> DeliveryAttempt:
    """Deliver the notification to a configured OpenClaw agent."""
    agent_name = os.environ.get("OPENCLAW_NOTIFY_AGENT", _DEFAULT_NOTIFY_AGENT).strip()
    if not agent_name:
        return DeliveryAttempt(delivered=False)

    event_type = str(payload.get("event", "task_update"))
    bead_id = str(payload.get("bead_id", "unknown"))
    body = json.dumps(payload, indent=2, sort_keys=True)
    delivery_instruction = (
        "Deliver this event to the user through configured notification channels now. "
        "If Slack is configured, send a DM and include a threaded reply when "
        "`slack_trigger_ts`/`slack_trigger_channel` are present."
    )
    message = (
        f"Notification from mctrl.\n"
        f"Action required: {delivery_instruction}\n"
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
            "--thinking",
            "minimal",
            "--message",
            message,
            "--json",
        ],
        capture_output=True,
        text=True,
        timeout=_OPENCLAW_AGENT_TIMEOUT_SECONDS,
    )
    error_text = "\n".join(part for part in (result.stdout, result.stderr) if part).strip()
    if result.returncode != 0:
        return DeliveryAttempt(delivered=False, transient=_is_transient_error_text(error_text))
    # Validate the JSON response indicates successful delivery, not just clean exit.
    # openclaw --json returns {"success": true} or {"error": "..."} on failure.
    try:
        response = json.loads(result.stdout)
        # Accept if response explicitly says success, or has no error field
        if isinstance(response, dict):
            if response.get("error"):
                return DeliveryAttempt(
                    delivered=False,
                    transient=_is_transient_error_text(str(response.get("error", ""))),
                )
            if "success" in response:
                return DeliveryAttempt(delivered=bool(response["success"]))
        # Non-dict or unknown shape but exit 0 — treat as delivered
        return DeliveryAttempt(delivered=True)
    except (json.JSONDecodeError, ValueError, TypeError):
        # stdout wasn't JSON or was None — exit 0 still means delivery command ran
        return DeliveryAttempt(delivered=True)


def _notification_text(payload: dict[str, Any]) -> str:
    event_type = str(payload.get("event", "task_update"))
    bead_id = str(payload.get("bead_id", "unknown"))
    branch = str(payload.get("branch", "")).strip()
    summary = str(payload.get("summary", "")).strip()
    action = str(payload.get("action_required", "")).strip()
    if event_type == "task_finished":
        branch_ref = (f" (`{branch}`)" if branch else "")
        return (
            f"task_finished: {bead_id}\n"
            f"ai_orch agent committed work{branch_ref}. Ready for review."
        )
    lines = [f"{event_type}: {bead_id}"]
    if summary:
        lines.append(summary)
    if action:
        lines.append(f"action_required={action}")
    return "\n".join(lines)


def _extract_openclaw_send_ok(stdout: str) -> bool:
    try:
        parsed = json.loads(stdout or "{}")
    except json.JSONDecodeError:
        return False
    payload = parsed.get("payload", {})
    return bool(payload.get("ok"))


def _send_openclaw_message(
    *,
    channel: str,
    target: str,
    text: str,
    reply_to: str = "",
) -> DeliveryAttempt:
    cmd = [
        "openclaw",
        "message",
        "send",
        "--channel",
        channel,
        "--target",
        target,
        "--message",
        text,
        "--json",
    ]
    if reply_to:
        cmd.extend(["--reply-to", reply_to])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=_OPENCLAW_MCP_TIMEOUT_SECONDS,
    )
    error_text = "\n".join(part for part in (result.stdout, result.stderr) if part).strip()
    delivered = result.returncode == 0 and _extract_openclaw_send_ok(result.stdout)
    return DeliveryAttempt(delivered=delivered, transient=_is_transient_error_text(error_text))


def _send_via_openclaw_message_channel(payload: dict[str, Any]) -> DeliveryAttempt:
    """Fallback channel delivery through OpenClaw CLI message send."""
    channel = os.environ.get("OPENCLAW_NOTIFY_CHANNEL", _DEFAULT_NOTIFY_CHANNEL).strip().lower()
    target = os.environ.get("OPENCLAW_NOTIFY_TARGET", _DEFAULT_NOTIFY_TARGET).strip()
    if not target:
        return DeliveryAttempt(delivered=False)

    text = _notification_text(payload)
    dm_attempt = _send_openclaw_message(channel=channel, target=target, text=text)
    if not dm_attempt.delivered:
        return dm_attempt

    thread_ts = str(payload.get("slack_trigger_ts", "")).strip()
    thread_channel = str(payload.get("slack_trigger_channel", "")).strip()
    if channel != "slack" or not thread_ts or not thread_channel:
        return dm_attempt

    thread_attempt = _send_openclaw_message(
        channel=channel,
        target=thread_channel,
        text=text,
        reply_to=thread_ts,
    )
    return DeliveryAttempt(
        delivered=dm_attempt.delivered and thread_attempt.delivered,
        transient=dm_attempt.transient or thread_attempt.transient,
    )
