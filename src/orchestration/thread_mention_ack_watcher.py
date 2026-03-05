"""Slack thread mention ack watcher.

Purpose:
- Enforce deterministic fallback acknowledgements for missed Slack thread mentions.
- Do not depend on model memory/preferences.
- Persist dedupe state so behavior survives restarts.

The watcher scans recent thread replies, detects "<@BOT_ID>" mentions, and posts
an in-thread acknowledgement when no bot reply exists after that mention.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)


@dataclass
class ThreadMentionAckConfig:
    """Runtime config for Slack mention watcher."""

    enabled: bool = True
    bot_user_id: str | None = None
    watch_interval_seconds: int = 60
    lookback_seconds: int = 900
    default_ack_message: str = (
        "Thanks, I saw the mention. Replying in this thread now."
    )
    ledger_path: Path = Path.home() / ".openclaw" / "thread_ack_ledger.json"

    # If set, only these channel IDs are scanned. Empty means auto-discover.
    channel_ids: list[str] = field(default_factory=list)
    scan_conversation_types: str = "public_channel,private_channel"

    # If set, only mentions from these users are acked.
    allowed_author_user_ids: list[str] = field(default_factory=list)
    ack_any_thread_message_from_allowed_users: bool = False

    # Auth configuration.
    slack_bot_token_env: str = "SLACK_BOT_TOKEN"
    slack_bot_token: str | None = None

    # Scan behavior.
    history_page_limit: int = 200
    history_pages_per_channel: int = 4
    max_acked_mentions: int = 10_000

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ThreadMentionAckConfig":
        """Build config from JSON with backwards-compat aliases."""
        channel_ids: list[str] = []
        has_explicit_channel_ids = "channelIds" in raw

        ids_raw = raw.get("channelIds")
        if isinstance(ids_raw, list):
            channel_ids = [str(v).strip() for v in ids_raw if str(v).strip()]

        legacy_channel_id = str(raw.get("channelId") or "").strip()
        # Back-compat:
        # - If modern channelIds is explicitly configured (even []), respect it.
        # - Only fall back to legacy channelId when channelIds is absent.
        if not has_explicit_channel_ids and legacy_channel_id and legacy_channel_id not in channel_ids:
            channel_ids.append(legacy_channel_id)

        allowed_raw = raw.get("allowedAuthorUserIds")
        allowed_author_user_ids = (
            [str(v).strip() for v in allowed_raw if str(v).strip()]
            if isinstance(allowed_raw, list)
            else []
        )

        ledger_path_raw = str(raw.get("ledgerPath") or "").strip()
        ledger_path = Path(ledger_path_raw).expanduser() if ledger_path_raw else cls.ledger_path

        return cls(
            enabled=bool(raw.get("enabled", True)),
            bot_user_id=str(raw.get("botUserId") or "").strip() or None,
            watch_interval_seconds=max(5, int(raw.get("watchIntervalSeconds", 60))),
            lookback_seconds=max(60, int(raw.get("lookbackSeconds", 900))),
            default_ack_message=str(
                raw.get("defaultAckMessage")
                or "Thanks, I saw the mention. Replying in this thread now."
            ),
            ledger_path=ledger_path,
            channel_ids=channel_ids,
            scan_conversation_types=str(
                raw.get("scanConversationTypes") or "public_channel,private_channel"
            ),
            allowed_author_user_ids=allowed_author_user_ids,
            ack_any_thread_message_from_allowed_users=bool(
                raw.get("ackAnyThreadMessageFromAllowedUsers", False)
            ),
            slack_bot_token_env=str(raw.get("slackBotTokenEnv") or "SLACK_BOT_TOKEN"),
            slack_bot_token=str(raw.get("slackBotToken") or "").strip() or None,
            history_page_limit=max(10, int(raw.get("historyPageLimit", 200))),
            history_pages_per_channel=max(1, int(raw.get("historyPagesPerChannel", 4))),
            max_acked_mentions=max(100, int(raw.get("maxAckedMentions", 10_000))),
        )


class SlackWebApi:
    """Small Slack Web API client using urllib only."""

    def __init__(self, token: str, timeout_seconds: int = 20) -> None:
        self.token = token
        self.timeout_seconds = timeout_seconds

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        query: Optional[dict[str, Any]] = None,
        payload: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        query_str = f"?{urlencode(query)}" if query else ""
        url = f"https://slack.com/api/{endpoint}{query_str}"
        body = None
        headers = {"Authorization": f"Bearer {self.token}"}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json; charset=utf-8"
        req = Request(url, data=body, headers=headers, method=method)
        with urlopen(req, timeout=self.timeout_seconds) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if not data.get("ok"):
            raise RuntimeError(f"slack api {endpoint} failed: {data.get('error', 'unknown')}")
        return data

    def auth_test(self) -> dict[str, Any]:
        return self._request("POST", "auth.test")

    def conversations_list(
        self,
        *,
        conversation_types: str,
        cursor: str | None,
        limit: int,
    ) -> dict[str, Any]:
        query: dict[str, Any] = {
            "types": conversation_types,
            "exclude_archived": "true",
            "limit": str(limit),
        }
        if cursor:
            query["cursor"] = cursor
        return self._request("GET", "conversations.list", query=query)

    def conversations_history(
        self,
        *,
        channel_id: str,
        oldest_ts: str | None,
        cursor: str | None,
        limit: int,
    ) -> dict[str, Any]:
        query: dict[str, Any] = {
            "channel": channel_id,
            "limit": str(limit),
        }
        if oldest_ts:
            query["oldest"] = oldest_ts
            query["inclusive"] = "true"
        if cursor:
            query["cursor"] = cursor
        return self._request("GET", "conversations.history", query=query)

    def conversations_replies(
        self,
        *,
        channel_id: str,
        thread_ts: str,
        oldest_ts: str,
        cursor: str | None = None,
        limit: int,
    ) -> dict[str, Any]:
        query: dict[str, Any] = {
            "channel": channel_id,
            "ts": thread_ts,
            "oldest": oldest_ts,
            "inclusive": "true",
            "limit": str(limit),
        }
        if cursor:
            query["cursor"] = cursor
        return self._request("GET", "conversations.replies", query=query)

    def post_thread_message(self, *, channel_id: str, thread_ts: str, text: str) -> dict[str, Any]:
        return self._request(
            "POST",
            "chat.postMessage",
            payload={"channel": channel_id, "thread_ts": thread_ts, "text": text},
        )


def _parse_ts(value: str | float | int | None) -> float:
    """Parse Slack timestamp into float; returns 0 on invalid input."""
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0


def _now_ts() -> str:
    return f"{time.time():.6f}"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _looks_like_placeholder(value: str) -> bool:
    lowered = value.strip().lower()
    return (
        not lowered
        or lowered.startswith("placeholder")
        or lowered.startswith("your-")
        or lowered in {"set-me", "replace-me"}
    )


def _resolve_token_from_openclaw_config() -> str:
    """Try loading Slack bot token from ~/.openclaw/openclaw.json."""
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    raw = _load_json(config_path)
    if not isinstance(raw, dict):
        return ""

    channels = raw.get("channels")
    if not isinstance(channels, dict):
        return ""
    slack = channels.get("slack")
    if not isinstance(slack, dict):
        return ""

    candidates = [
        str(slack.get("botToken") or "").strip(),
    ]
    accounts = slack.get("accounts")
    if isinstance(accounts, dict):
        for account in accounts.values():
            if not isinstance(account, dict):
                continue
            candidates.append(str(account.get("botToken") or "").strip())

    for candidate in candidates:
        if _looks_like_placeholder(candidate):
            continue
        return candidate
    return ""


def load_config(config_path: Path) -> ThreadMentionAckConfig:
    """Load watcher config from JSON file."""
    raw = _load_json(config_path)
    if not isinstance(raw, dict):
        raw = {}
    return ThreadMentionAckConfig.from_dict(raw)


def load_ledger(ledger_path: Path) -> dict[str, Any]:
    """Load dedupe ledger from disk."""
    raw = _load_json(ledger_path)
    if not isinstance(raw, dict):
        raw = {}

    acked = raw.get("acked_mentions")
    if not isinstance(acked, dict):
        acked = {}

    last_scanned = raw.get("last_scanned_ts")
    if not isinstance(last_scanned, dict):
        last_scanned = {}

    bot_user_id = raw.get("bot_user_id")
    if not isinstance(bot_user_id, str):
        bot_user_id = None

    return {
        "acked_mentions": {str(k): str(v) for k, v in acked.items()},
        "last_scanned_ts": {str(k): str(v) for k, v in last_scanned.items()},
        "bot_user_id": bot_user_id,
    }


def save_ledger(ledger_path: Path, ledger: dict[str, Any]) -> None:
    """Persist ledger atomically to avoid truncation on crashes."""
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = ledger_path.with_suffix(ledger_path.suffix + ".tmp")
    temp_path.write_text(json.dumps(ledger, indent=2, sort_keys=True), encoding="utf-8")
    temp_path.replace(ledger_path)


def prune_acked_mentions(acked_mentions: dict[str, str], max_records: int) -> None:
    """Keep the newest N ack records by mention timestamp in key suffix."""
    if len(acked_mentions) <= max_records:
        return

    def mention_ts(record_key: str) -> float:
        # key format: "{channel}:{thread_ts}:{message_ts}"
        parts = record_key.split(":")
        if len(parts) < 3:
            return 0.0
        return _parse_ts(parts[-1])

    keys = sorted(acked_mentions.keys(), key=mention_ts)
    overflow = len(keys) - max_records
    for key in keys[:overflow]:
        acked_mentions.pop(key, None)


def discover_channel_ids(api: SlackWebApi, cfg: ThreadMentionAckConfig) -> list[str]:
    """Resolve channels to scan (explicit list or Slack discovery)."""
    if cfg.channel_ids:
        # Preserve order and de-duplicate.
        seen: set[str] = set()
        ordered: list[str] = []
        for channel_id in cfg.channel_ids:
            if channel_id in seen:
                continue
            seen.add(channel_id)
            ordered.append(channel_id)
        return ordered

    ids: list[str] = []
    seen: set[str] = set()
    cursor: str | None = None

    while True:
        data = api.conversations_list(
            conversation_types=cfg.scan_conversation_types,
            cursor=cursor,
            limit=min(1000, cfg.history_page_limit),
        )
        for convo in data.get("channels", []) or []:
            channel_id = str(convo.get("id") or "").strip()
            if not channel_id or channel_id in seen:
                continue
            seen.add(channel_id)
            ids.append(channel_id)
        cursor = (
            (data.get("response_metadata") or {}).get("next_cursor")  # type: ignore[assignment]
            if isinstance(data.get("response_metadata"), dict)
            else None
        )
        if not cursor:
            break

    return ids


def is_thread_mention_for_bot(
    message: dict[str, Any],
    *,
    bot_user_id: str,
    allowed_author_user_ids: set[str],
    ack_any_thread_message_from_allowed_users: bool,
) -> bool:
    """Return true when message is a thread reply that mentions the bot."""
    subtype = str(message.get("subtype") or "").strip()
    if subtype in {"bot_message", "message_changed", "message_deleted"}:
        return False

    thread_ts = str(message.get("thread_ts") or "").strip()
    message_ts = str(message.get("ts") or "").strip()
    if not thread_ts or not message_ts:
        return False

    # Must be a reply in an existing thread, not the root.
    if thread_ts == message_ts:
        return False

    author_user_id = str(message.get("user") or "").strip()
    if not author_user_id:
        return False
    if author_user_id == bot_user_id:
        return False
    if allowed_author_user_ids and author_user_id not in allowed_author_user_ids:
        return False

    text = str(message.get("text") or "")
    if f"<@{bot_user_id}>" in text:
        return True
    if (
        ack_any_thread_message_from_allowed_users
        and allowed_author_user_ids
        and author_user_id in allowed_author_user_ids
    ):
        # User-guidance mode: in threads, acknowledge allowed users even without mention
        # when no subsequent bot reply exists.
        return True
    return False


def mention_key(channel_id: str, thread_ts: str, message_ts: str) -> str:
    return f"{channel_id}:{thread_ts}:{message_ts}"


def thread_has_bot_reply_after(
    api: SlackWebApi,
    *,
    channel_id: str,
    thread_ts: str,
    message_ts: str,
    bot_user_id: str,
    page_limit: int,
) -> bool:
    """Check whether bot replied in thread after mention timestamp.

    Paginates all reply pages and stops early once a qualifying bot reply is found.
    """
    mention_ts_value = _parse_ts(message_ts)
    cursor: str | None = None
    while True:
        data = api.conversations_replies(
            channel_id=channel_id,
            thread_ts=thread_ts,
            oldest_ts=message_ts,
            cursor=cursor,
            limit=page_limit,
        )
        for msg in data.get("messages", []) or []:
            if str(msg.get("user") or "").strip() != bot_user_id:
                continue
            if _parse_ts(msg.get("ts")) > mention_ts_value:
                return True
        next_cursor = (data.get("response_metadata") or {}).get("next_cursor")
        if not next_cursor:
            break
        cursor = next_cursor
    return False


def process_channel(
    api: SlackWebApi,
    *,
    channel_id: str,
    cfg: ThreadMentionAckConfig,
    ledger: dict[str, Any],
    bot_user_id: str,
) -> dict[str, int]:
    """Scan a single channel and ack missing mentions."""
    stats = {"scanned": 0, "mentions": 0, "already_replied": 0, "sent": 0}
    acked_mentions: dict[str, str] = ledger["acked_mentions"]
    last_scanned_ts: dict[str, str] = ledger["last_scanned_ts"]

    oldest_ts = last_scanned_ts.get(channel_id)
    if not oldest_ts:
        oldest_ts = f"{max(0.0, time.time() - cfg.lookback_seconds):.6f}"

    cursor: str | None = None
    messages: list[dict[str, Any]] = []
    for _ in range(cfg.history_pages_per_channel):
        data = api.conversations_history(
            channel_id=channel_id,
            oldest_ts=oldest_ts,
            cursor=cursor,
            limit=cfg.history_page_limit,
        )
        page_messages = data.get("messages", []) or []
        if isinstance(page_messages, list):
            messages.extend(m for m in page_messages if isinstance(m, dict))
        response_meta = data.get("response_metadata")
        cursor = response_meta.get("next_cursor") if isinstance(response_meta, dict) else None
        if not cursor:
            break

    if not messages:
        return stats

    messages.sort(key=lambda msg: _parse_ts(msg.get("ts")))
    allowed_author_ids = {v for v in cfg.allowed_author_user_ids if v}
    max_seen_ts = _parse_ts(oldest_ts)
    thread_roots_to_scan: set[str] = set()

    # Scan any direct thread replies found in history (some Slack contexts may include these).
    # Also collect active thread roots so we can query replies explicitly.
    for message in messages:
        message_ts = str(message.get("ts") or "").strip()
        thread_ts = str(message.get("thread_ts") or "").strip()
        latest_reply_ts = str(message.get("latest_reply") or "").strip()
        reply_count = int(message.get("reply_count") or 0)
        ts_value = _parse_ts(message_ts)
        max_seen_ts = max(max_seen_ts, ts_value)

        is_root = bool(thread_ts and message_ts and thread_ts == message_ts)
        if is_root:
            latest_reply_value = _parse_ts(latest_reply_ts)
            if reply_count > 0 and latest_reply_value > _parse_ts(oldest_ts):
                thread_roots_to_scan.add(thread_ts)
            continue

        stats["scanned"] += 1
        if not is_thread_mention_for_bot(
            message,
            bot_user_id=bot_user_id,
            allowed_author_user_ids=allowed_author_ids,
            ack_any_thread_message_from_allowed_users=cfg.ack_any_thread_message_from_allowed_users,
        ):
            continue

        stats["mentions"] += 1
        key = mention_key(channel_id, thread_ts, message_ts)
        if key in acked_mentions:
            continue

        if thread_has_bot_reply_after(
            api,
            channel_id=channel_id,
            thread_ts=thread_ts,
            message_ts=message_ts,
            bot_user_id=bot_user_id,
            page_limit=cfg.history_page_limit,
        ):
            acked_mentions[key] = _now_ts()
            stats["already_replied"] += 1
            continue

        api.post_thread_message(
            channel_id=channel_id,
            thread_ts=thread_ts,
            text=cfg.default_ack_message,
        )
        acked_mentions[key] = _now_ts()
        stats["sent"] += 1
        logger.info(
            "sent thread mention ack: channel=%s thread_ts=%s mention_ts=%s",
            channel_id,
            thread_ts,
            message_ts,
        )

    # Explicitly scan replies for active thread roots so mentions in old threads
    # are still visible even when root message is older than lookback.
    for thread_ts in sorted(thread_roots_to_scan, key=_parse_ts):
        replies: list[dict[str, Any]] = []
        reply_cursor: str | None = None
        while True:
            data = api.conversations_replies(
                channel_id=channel_id,
                thread_ts=thread_ts,
                oldest_ts=oldest_ts,
                cursor=reply_cursor,
                limit=cfg.history_page_limit,
            )
            replies.extend(m for m in (data.get("messages", []) or []) if isinstance(m, dict))
            next_reply_cursor = (data.get("response_metadata") or {}).get("next_cursor")
            if not next_reply_cursor:
                break
            reply_cursor = next_reply_cursor
        replies.sort(key=lambda msg: _parse_ts(msg.get("ts")))

        for reply in replies:
            reply_ts = str(reply.get("ts") or "").strip()
            max_seen_ts = max(max_seen_ts, _parse_ts(reply_ts))

            # Skip root message returned by conversations.replies.
            if reply_ts == thread_ts:
                continue

            stats["scanned"] += 1
            if not is_thread_mention_for_bot(
                reply,
                bot_user_id=bot_user_id,
                allowed_author_user_ids=allowed_author_ids,
                ack_any_thread_message_from_allowed_users=cfg.ack_any_thread_message_from_allowed_users,
            ):
                continue

            stats["mentions"] += 1
            key = mention_key(channel_id, thread_ts, reply_ts)
            if key in acked_mentions:
                continue

            mention_ts_value = _parse_ts(reply_ts)
            already_replied = any(
                str(r.get("user") or "").strip() == bot_user_id
                and _parse_ts(r.get("ts")) > mention_ts_value
                for r in replies
            )
            if already_replied:
                acked_mentions[key] = _now_ts()
                stats["already_replied"] += 1
                continue

            api.post_thread_message(
                channel_id=channel_id,
                thread_ts=thread_ts,
                text=cfg.default_ack_message,
            )
            ack_ts = _now_ts()
            acked_mentions[key] = ack_ts
            # Reflect the just-posted ack in-memory so later mentions in this
            # same thread iteration see it as a qualifying bot reply.
            replies.append({"ts": ack_ts, "user": bot_user_id})
            stats["sent"] += 1
            logger.info(
                "sent thread mention ack: channel=%s thread_ts=%s mention_ts=%s",
                channel_id,
                thread_ts,
                reply_ts,
            )

    if max_seen_ts > 0:
        last_scanned_ts[channel_id] = f"{max_seen_ts:.6f}"
    return stats


def run_single_pass(
    api: SlackWebApi,
    *,
    cfg: ThreadMentionAckConfig,
    ledger: dict[str, Any],
    bot_user_id: str,
) -> dict[str, int]:
    """Run one watcher scan across channels."""
    totals = {"channels": 0, "scanned": 0, "mentions": 0, "already_replied": 0, "sent": 0}
    channel_ids = discover_channel_ids(api, cfg)
    for channel_id in channel_ids:
        totals["channels"] += 1
        try:
            stats = process_channel(
                api,
                channel_id=channel_id,
                cfg=cfg,
                ledger=ledger,
                bot_user_id=bot_user_id,
            )
            for key, value in stats.items():
                totals[key] += value
        except Exception as exc:
            logger.warning("channel scan failed channel=%s err=%s", channel_id, exc)

    prune_acked_mentions(ledger["acked_mentions"], cfg.max_acked_mentions)
    return totals


def resolve_bot_user_id(api: SlackWebApi, configured_bot_user_id: str | None) -> str:
    """Use configured bot ID if present, else resolve via auth.test."""
    if configured_bot_user_id:
        return configured_bot_user_id
    auth = api.auth_test()
    user_id = str(auth.get("user_id") or "").strip()
    if not user_id:
        raise RuntimeError("auth.test returned empty user_id")
    return user_id


def run_watcher(*, config_path: Path, once: bool = False) -> int:
    """Run mention watcher loop."""
    cfg = load_config(config_path)
    if not cfg.enabled:
        logger.info("thread mention ack watcher disabled in config")
        return 0
    if cfg.ack_any_thread_message_from_allowed_users and not cfg.allowed_author_user_ids:
        logger.warning(
            "ackAnyThreadMessageFromAllowedUsers is enabled but allowedAuthorUserIds is empty; "
            "non-mention ACK mode is disabled"
        )

    token = cfg.slack_bot_token or os.environ.get(cfg.slack_bot_token_env, "")
    if not token:
        token = _resolve_token_from_openclaw_config()
    if not token:
        logger.error("missing Slack bot token (env=%s)", cfg.slack_bot_token_env)
        return 1

    api = SlackWebApi(token=token)
    bot_user_id = resolve_bot_user_id(api, cfg.bot_user_id)
    ledger = load_ledger(cfg.ledger_path)
    ledger["bot_user_id"] = bot_user_id

    while True:
        had_error = False
        try:
            totals = run_single_pass(
                api,
                cfg=cfg,
                ledger=ledger,
                bot_user_id=bot_user_id,
            )
            save_ledger(cfg.ledger_path, ledger)
            logger.info(
                "watch pass complete channels=%d scanned=%d mentions=%d already_replied=%d sent=%d",
                totals["channels"],
                totals["scanned"],
                totals["mentions"],
                totals["already_replied"],
                totals["sent"],
            )
        except Exception:
            had_error = True
            logger.exception("watch pass failed")

        if once:
            return 1 if had_error else 0
        time.sleep(cfg.watch_interval_seconds)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Slack thread mention ack watcher")
    parser.add_argument(
        "--config",
        default=str(Path("scripts") / "thread_mention_ack_config.json"),
        help="Path to watcher JSON config.",
    )
    parser.add_argument("--once", action="store_true", help="Run one scan and exit.")
    parser.add_argument(
        "--log-level",
        default=os.environ.get("THREAD_ACK_LOG_LEVEL", "INFO"),
        help="Python logging level (DEBUG, INFO, WARNING, ERROR).",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    logging.basicConfig(
        level=getattr(logging, str(args.log_level).upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    config_path = Path(args.config).expanduser()
    try:
        return run_watcher(config_path=config_path, once=args.once)
    except KeyboardInterrupt:
        logger.info("stopped by keyboard interrupt")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
