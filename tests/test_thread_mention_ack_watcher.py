"""Tests for orchestration.thread_mention_ack_watcher."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

from orchestration.thread_mention_ack_watcher import (
    ThreadMentionAckConfig,
    is_thread_mention_for_bot,
    load_config,
    mention_key,
    process_channel,
    run_watcher,
)


class FakeSlackApi:
    """Minimal fake Slack API for watcher unit tests."""

    def __init__(
        self,
        *,
        history_messages: list[dict[str, Any]],
        thread_replies: dict[str, list[dict[str, Any]]],
    ) -> None:
        self._history_messages = history_messages
        self._thread_replies = thread_replies
        self.sent_messages: list[tuple[str, str, str]] = []
        self.history_calls: list[dict[str, str | None | int]] = []
        self.history_oldest_ts_calls: list[str | None] = []
        self.replies_oldest_ts_calls: list[str] = []

    def conversations_history(
        self,
        *,
        channel_id: str,
        oldest_ts: str | None,
        cursor: str | None,
        limit: int,
    ) -> dict[str, Any]:
        self.history_calls.append(
            {
                "channel_id": channel_id,
                "oldest_ts": oldest_ts,
                "cursor": cursor,
                "limit": limit,
            }
        )
        self.history_oldest_ts_calls.append(oldest_ts)
        return {"ok": True, "messages": list(self._history_messages)}

    def conversations_replies(
        self,
        *,
        channel_id: str,
        thread_ts: str,
        oldest_ts: str,
        cursor: str | None = None,
        limit: int,
    ) -> dict[str, Any]:
        del channel_id, limit, cursor
        self.replies_oldest_ts_calls.append(oldest_ts)
        return {"ok": True, "messages": list(self._thread_replies.get(thread_ts, []))}

    def post_thread_message(self, *, channel_id: str, thread_ts: str, text: str) -> dict[str, Any]:
        self.sent_messages.append((channel_id, thread_ts, text))
        return {"ok": True, "ts": "1770000000.000001"}


def test_load_config_supports_legacy_fields(tmp_path: Path) -> None:
    cfg_path = tmp_path / "thread_ack.json"
    cfg_path.write_text(
        """{
  "enabled": true,
  "botUserId": "U_BOT",
  "watchIntervalSeconds": 123,
  "defaultAckMessage": "ack-now",
  "ledgerPath": "LEDGER_PLACEHOLDER",
  "channelId": "C_SINGLE"
}""".replace("LEDGER_PLACEHOLDER", str(tmp_path / "ledger.json")),
        encoding="utf-8",
    )

    cfg = load_config(cfg_path)

    assert cfg.enabled is True
    assert cfg.bot_user_id == "U_BOT"
    assert cfg.watch_interval_seconds == 123
    assert cfg.default_ack_message == "ack-now"
    assert cfg.ledger_path == (tmp_path / "ledger.json")
    assert cfg.channel_ids == ["C_SINGLE"]


def test_is_thread_mention_for_bot_filters_non_candidates() -> None:
    allowed_authors = {"U_JEFF"}

    assert is_thread_mention_for_bot(
        {
            "ts": "100.2",
            "thread_ts": "100.2",
            "user": "U_JEFF",
            "text": "<@U_BOT> hi",
        },
        bot_user_id="U_BOT",
        allowed_author_user_ids=allowed_authors,
        ack_any_thread_message_from_allowed_users=False,
    ) is False

    assert is_thread_mention_for_bot(
        {
            "ts": "100.3",
            "thread_ts": "100.1",
            "user": "U_OTHER",
            "text": "<@U_BOT> hi",
        },
        bot_user_id="U_BOT",
        allowed_author_user_ids=allowed_authors,
        ack_any_thread_message_from_allowed_users=False,
    ) is False

    assert is_thread_mention_for_bot(
        {
            "ts": "100.4",
            "thread_ts": "100.1",
            "user": "U_JEFF",
            "text": "<@U_BOT> hi",
        },
        bot_user_id="U_BOT",
        allowed_author_user_ids=allowed_authors,
        ack_any_thread_message_from_allowed_users=False,
    ) is True

    assert is_thread_mention_for_bot(
        {
            "ts": "100.5",
            "thread_ts": "100.1",
            "user": "U_JEFF",
            "text": "no explicit mention",
        },
        bot_user_id="U_BOT",
        allowed_author_user_ids=allowed_authors,
        ack_any_thread_message_from_allowed_users=True,
    ) is True


def test_is_thread_mention_for_bot_does_not_ack_unmentioned_when_allowlist_empty() -> None:
    assert is_thread_mention_for_bot(
        {
            "ts": "101.5",
            "thread_ts": "101.1",
            "user": "U_ANYONE",
            "text": "no explicit mention",
        },
        bot_user_id="U_BOT",
        allowed_author_user_ids=set(),
        ack_any_thread_message_from_allowed_users=True,
    ) is False


def test_thread_ack_config_has_no_dead_fields() -> None:
    cfg_path = Path(__file__).resolve().parents[2] / "scripts" / "thread_mention_ack_config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    assert "ackMethod" not in cfg
    assert "openclawBinary" not in cfg


def test_process_channel_sends_ack_for_missing_reply() -> None:
    cfg = ThreadMentionAckConfig(
        bot_user_id="U_BOT",
        default_ack_message="thread ack",
        allowed_author_user_ids=["U_JEFF"],
        history_page_limit=100,
        history_pages_per_channel=1,
    )
    api = FakeSlackApi(
        history_messages=[
            {
                "ts": "200.5",
                "thread_ts": "200.1",
                "user": "U_JEFF",
                "text": "hey <@U_BOT>",
            }
        ],
        thread_replies={
            "200.1": [
                {"ts": "200.1", "user": "U_JEFF", "text": "start"},
                {"ts": "200.5", "user": "U_JEFF", "text": "hey <@U_BOT>"},
            ]
        },
    )
    ledger = {"acked_mentions": {}, "last_scanned_ts": {}, "bot_user_id": "U_BOT"}

    stats = process_channel(
        api,
        channel_id="C_TEST",
        cfg=cfg,
        ledger=ledger,
        bot_user_id="U_BOT",
    )

    assert stats["mentions"] == 1
    assert stats["sent"] == 1
    assert api.sent_messages == [("C_TEST", "200.1", "thread ack")]

    key = mention_key("C_TEST", "200.1", "200.5")
    assert key in ledger["acked_mentions"]
    assert float(ledger["last_scanned_ts"]["C_TEST"]) >= 200.5


def test_process_channel_marks_already_replied_without_sending() -> None:
    cfg = ThreadMentionAckConfig(
        bot_user_id="U_BOT",
        default_ack_message="thread ack",
        allowed_author_user_ids=["U_JEFF"],
        history_page_limit=100,
        history_pages_per_channel=1,
    )
    api = FakeSlackApi(
        history_messages=[
            {
                "ts": "300.5",
                "thread_ts": "300.1",
                "user": "U_JEFF",
                "text": "ping <@U_BOT>",
            }
        ],
        thread_replies={
            "300.1": [
                {"ts": "300.1", "user": "U_JEFF", "text": "start"},
                {"ts": "300.6", "user": "U_BOT", "text": "already replied"},
            ]
        },
    )
    ledger = {"acked_mentions": {}, "last_scanned_ts": {}, "bot_user_id": "U_BOT"}

    stats = process_channel(
        api,
        channel_id="C_TEST",
        cfg=cfg,
        ledger=ledger,
        bot_user_id="U_BOT",
    )

    assert stats["mentions"] == 1
    assert stats["already_replied"] == 1
    assert stats["sent"] == 0
    assert api.sent_messages == []

    key = mention_key("C_TEST", "300.1", "300.5")
    assert key in ledger["acked_mentions"]


def test_process_channel_scans_active_thread_roots_for_mentions() -> None:
    """Mentions in replies to old thread roots should still be detected."""
    cfg = ThreadMentionAckConfig(
        bot_user_id="U_BOT",
        default_ack_message="thread ack",
        allowed_author_user_ids=["U_JEFF"],
        history_page_limit=100,
        history_pages_per_channel=1,
    )
    api = FakeSlackApi(
        history_messages=[
            {
                "ts": "400.1",
                "thread_ts": "400.1",
                "user": "U_JEFF",
                "text": "root",
                "reply_count": 2,
                "latest_reply": "401.2",
            }
        ],
        thread_replies={
            "400.1": [
                {"ts": "400.1", "user": "U_JEFF", "text": "root"},
                {"ts": "401.2", "thread_ts": "400.1", "user": "U_JEFF", "text": "hey <@U_BOT>"},
            ]
        },
    )
    ledger = {
        "acked_mentions": {},
        "last_scanned_ts": {"C_TEST": "300.0"},
        "bot_user_id": "U_BOT",
    }

    stats = process_channel(
        api,
        channel_id="C_TEST",
        cfg=cfg,
        ledger=ledger,
        bot_user_id="U_BOT",
    )

    assert stats["mentions"] == 1
    assert stats["sent"] == 1
    assert api.sent_messages == [("C_TEST", "400.1", "thread ack")]

    key = mention_key("C_TEST", "400.1", "401.2")
    assert key in ledger["acked_mentions"]


def test_process_channel_passes_ledger_watermark_to_history() -> None:
    cfg = ThreadMentionAckConfig(
        bot_user_id="U_BOT",
        default_ack_message="thread ack",
        allowed_author_user_ids=["U_JEFF"],
        history_page_limit=100,
        history_pages_per_channel=1,
    )
    api = FakeSlackApi(
        history_messages=[],
        thread_replies={},
    )
    ledger = {
        "acked_mentions": {},
        "last_scanned_ts": {"C_TEST": "123.456789"},
        "bot_user_id": "U_BOT",
    }

    process_channel(
        api,
        channel_id="C_TEST",
        cfg=cfg,
        ledger=ledger,
        bot_user_id="U_BOT",
    )

    assert api.history_calls
    assert api.history_calls[0]["oldest_ts"] == "123.456789"


def test_process_channel_can_ack_unmentioned_allowed_user_thread_message() -> None:
    cfg = ThreadMentionAckConfig(
        bot_user_id="U_BOT",
        default_ack_message="thread ack",
        allowed_author_user_ids=["U_JEFF"],
        ack_any_thread_message_from_allowed_users=True,
        history_page_limit=100,
        history_pages_per_channel=1,
    )
    api = FakeSlackApi(
        history_messages=[
            {
                "ts": "500.5",
                "thread_ts": "500.1",
                "user": "U_JEFF",
                "text": "follow-up without mention",
            }
        ],
        thread_replies={
            "500.1": [
                {"ts": "500.1", "user": "U_JEFF", "text": "root"},
                {"ts": "500.5", "user": "U_JEFF", "text": "follow-up without mention"},
            ]
        },
    )
    ledger = {"acked_mentions": {}, "last_scanned_ts": {}, "bot_user_id": "U_BOT"}

    stats = process_channel(
        api,
        channel_id="C_TEST",
        cfg=cfg,
        ledger=ledger,
        bot_user_id="U_BOT",
    )

    assert stats["mentions"] == 1
    assert stats["sent"] == 1
    assert api.sent_messages == [("C_TEST", "500.1", "thread ack")]


def test_process_channel_passes_computed_oldest_ts_to_history() -> None:
    cfg = ThreadMentionAckConfig(
        bot_user_id="U_BOT",
        default_ack_message="thread ack",
        allowed_author_user_ids=["U_JEFF"],
        history_page_limit=100,
        history_pages_per_channel=1,
    )
    api = FakeSlackApi(
        history_messages=[
            {
                "ts": "600.5",
                "thread_ts": "600.1",
                "user": "U_JEFF",
                "text": "hey <@U_BOT>",
            }
        ],
        thread_replies={
            "600.1": [
                {"ts": "600.1", "user": "U_JEFF", "text": "root"},
                {"ts": "600.5", "user": "U_JEFF", "text": "hey <@U_BOT>"},
            ]
        },
    )
    ledger = {
        "acked_mentions": {},
        "last_scanned_ts": {"C_TEST": "599.123456"},
        "bot_user_id": "U_BOT",
    }

    stats = process_channel(
        api,
        channel_id="C_TEST",
        cfg=cfg,
        ledger=ledger,
        bot_user_id="U_BOT",
    )

    assert stats["mentions"] == 1
    assert api.history_oldest_ts_calls
    assert api.history_oldest_ts_calls[0] == "599.123456"


def test_run_watcher_once_returns_zero_on_success(tmp_path: Path) -> None:
    cfg_path = tmp_path / "watcher.json"
    ledger_path = tmp_path / "ledger.json"
    cfg_path.write_text(
        """{
  "enabled": true,
  "botUserId": "U_BOT",
  "slackBotToken": "xoxb-test-token",
  "ledgerPath": "LEDGER_PLACEHOLDER"
}""".replace("LEDGER_PLACEHOLDER", str(ledger_path)),
        encoding="utf-8",
    )

    with (
        patch(
            "orchestration.thread_mention_ack_watcher.resolve_bot_user_id",
            return_value="U_BOT",
        ),
        patch(
            "orchestration.thread_mention_ack_watcher.run_single_pass",
            return_value={
                "channels": 1,
                "scanned": 0,
                "mentions": 0,
                "already_replied": 0,
                "sent": 0,
            },
        ),
    ):
        assert run_watcher(config_path=cfg_path, once=True) == 0


def test_run_watcher_once_returns_nonzero_on_pass_error(tmp_path: Path) -> None:
    cfg_path = tmp_path / "watcher.json"
    ledger_path = tmp_path / "ledger.json"
    cfg_path.write_text(
        """{
  "enabled": true,
  "botUserId": "U_BOT",
  "slackBotToken": "xoxb-test-token",
  "ledgerPath": "LEDGER_PLACEHOLDER"
}""".replace("LEDGER_PLACEHOLDER", str(ledger_path)),
        encoding="utf-8",
    )

    with (
        patch(
            "orchestration.thread_mention_ack_watcher.resolve_bot_user_id",
            return_value="U_BOT",
        ),
        patch(
            "orchestration.thread_mention_ack_watcher.run_single_pass",
            side_effect=RuntimeError("boom"),
        ),
    ):
        assert run_watcher(config_path=cfg_path, once=True) == 1


class PaginatedRepliesFakeSlackApi(FakeSlackApi):
    """FakeSlackApi that returns thread replies across multiple pages."""

    def __init__(
        self,
        *,
        history_messages: list[dict[str, Any]],
        thread_replies_pages: dict[str, list[list[dict[str, Any]]]],
    ) -> None:
        # Flatten all pages for the base class (not used directly here)
        flat = {ts: [m for page in pages for m in page] for ts, pages in thread_replies_pages.items()}
        super().__init__(history_messages=history_messages, thread_replies=flat)
        self._pages = thread_replies_pages
        self._page_cursors: dict[str, int] = {}

    def conversations_replies(
        self,
        *,
        channel_id: str,
        thread_ts: str,
        oldest_ts: str,
        cursor: str | None = None,
        limit: int,
    ) -> dict[str, Any]:
        del channel_id, limit
        self.replies_oldest_ts_calls.append(oldest_ts)
        pages = self._pages.get(thread_ts, [[]])
        page_index = int(cursor) if cursor else 0
        messages = pages[page_index] if page_index < len(pages) else []
        next_index = page_index + 1
        next_cursor = str(next_index) if next_index < len(pages) else None
        response: dict[str, Any] = {"ok": True, "messages": list(messages)}
        if next_cursor:
            response["response_metadata"] = {"next_cursor": next_cursor}
        return response


def test_thread_has_bot_reply_after_paginates_all_pages() -> None:
    """Bot reply on second page should be detected without sending a duplicate ACK."""
    from orchestration.thread_mention_ack_watcher import thread_has_bot_reply_after

    api = PaginatedRepliesFakeSlackApi(
        history_messages=[],
        thread_replies_pages={
            "100.0": [
                # page 0: no bot reply
                [{"ts": "101.0", "user": "U_HUMAN", "text": "hi"}],
                # page 1: bot reply
                [{"ts": "102.0", "user": "U_BOT", "text": "ack"}],
            ]
        },
    )

    result = thread_has_bot_reply_after(
        api,
        channel_id="C_TEST",
        thread_ts="100.0",
        message_ts="100.5",
        bot_user_id="U_BOT",
        page_limit=1,
    )

    assert result is True
    assert len(api.replies_oldest_ts_calls) == 2  # fetched both pages


def test_process_channel_paginates_active_thread_replies() -> None:
    """Mentions on page 2 of a thread should still be detected and ACKed."""
    cfg = ThreadMentionAckConfig(
        bot_user_id="U_BOT",
        default_ack_message="ack",
        allowed_author_user_ids=["U_JEFF"],
        history_page_limit=1,
        history_pages_per_channel=1,
    )
    api = PaginatedRepliesFakeSlackApi(
        history_messages=[
            {
                "ts": "400.0",
                "thread_ts": "400.0",
                "user": "U_JEFF",
                "text": "root",
                "reply_count": 3,
                "latest_reply": "402.0",
            }
        ],
        thread_replies_pages={
            "400.0": [
                # page 0: root + first reply (no mention)
                [
                    {"ts": "400.0", "user": "U_JEFF", "text": "root"},
                    {"ts": "401.0", "thread_ts": "400.0", "user": "U_JEFF", "text": "hello"},
                ],
                # page 1: mention on second page
                [{"ts": "402.0", "thread_ts": "400.0", "user": "U_JEFF", "text": "hey <@U_BOT>"}],
            ]
        },
    )
    ledger: dict[str, Any] = {
        "acked_mentions": {},
        "last_scanned_ts": {"C_TEST": "300.0"},
        "bot_user_id": "U_BOT",
    }

    stats = process_channel(api, channel_id="C_TEST", cfg=cfg, ledger=ledger, bot_user_id="U_BOT")

    assert stats["mentions"] == 1
    assert stats["sent"] == 1
    assert api.sent_messages == [("C_TEST", "400.0", "ack")]


def test_process_channel_no_n_plus_1_replies_calls_for_thread_root_mentions() -> None:
    """process_channel must not call conversations_replies once per mention via
    thread_has_bot_reply_after when processing thread_roots_to_scan — it should
    check already-fetched replies in memory instead.

    With 2 mentions in one thread and no prior bot reply, the current (broken)
    code makes 3 conversations_replies calls (1 fetch + 1 per mention).
    The fix should produce exactly 1 call.
    """
    cfg = ThreadMentionAckConfig(
        bot_user_id="U_BOT",
        default_ack_message="ack",
        allowed_author_user_ids=["U_JEFF"],
        history_page_limit=10,
        history_pages_per_channel=1,
    )
    # Thread root with two mentions from U_JEFF, no bot reply.
    api = PaginatedRepliesFakeSlackApi(
        history_messages=[
            {
                "ts": "500.0",
                "thread_ts": "500.0",
                "user": "U_JEFF",
                "text": "root",
                "reply_count": 2,
                "latest_reply": "502.0",
            }
        ],
        thread_replies_pages={
            "500.0": [
                [
                    {"ts": "500.0", "user": "U_JEFF", "text": "root"},
                    {"ts": "501.0", "thread_ts": "500.0", "user": "U_JEFF", "text": "hey <@U_BOT>"},
                    {"ts": "502.0", "thread_ts": "500.0", "user": "U_JEFF", "text": "also <@U_BOT>"},
                ]
            ]
        },
    )
    ledger: dict[str, Any] = {
        "acked_mentions": {},
        "last_scanned_ts": {"C_TEST": "400.0"},
        "bot_user_id": "U_BOT",
    }

    stats = process_channel(api, channel_id="C_TEST", cfg=cfg, ledger=ledger, bot_user_id="U_BOT")

    assert stats["mentions"] == 2
    # The ack posted for mention 501 is after mention 502 (current-time ts), so
    # the second mention should be covered and only 1 ack should be sent.
    assert stats["sent"] == 1
    assert stats["already_replied"] == 1
    # Only 1 conversations_replies call: the initial fetch of the thread's replies.
    # A second call per mention (N+1) is the bug this test guards against.
    assert len(api.replies_oldest_ts_calls) == 1, (
        f"Expected 1 conversations_replies call (in-memory check), "
        f"got {len(api.replies_oldest_ts_calls)}: {api.replies_oldest_ts_calls}"
    )


def test_process_channel_does_not_duplicate_ack_for_multiple_mentions_in_same_thread() -> None:
    """A second mention in the same thread should see the ack just posted for
    the first mention and be marked already_replied — not trigger a duplicate ack.

    This is a regression test for the bug introduced when switching from
    thread_has_bot_reply_after (fresh API call) to in-memory replies check:
    the freshly-posted ack wasn't in `replies`, so every mention got its own ack.
    """
    cfg = ThreadMentionAckConfig(
        bot_user_id="U_BOT",
        default_ack_message="ack",
        allowed_author_user_ids=["U_JEFF"],
        history_page_limit=10,
        history_pages_per_channel=1,
    )
    api = PaginatedRepliesFakeSlackApi(
        history_messages=[
            {
                "ts": "600.0",
                "thread_ts": "600.0",
                "user": "U_JEFF",
                "text": "root",
                "reply_count": 2,
                "latest_reply": "602.0",
            }
        ],
        thread_replies_pages={
            "600.0": [
                [
                    {"ts": "600.0", "user": "U_JEFF", "text": "root"},
                    {"ts": "601.0", "thread_ts": "600.0", "user": "U_JEFF", "text": "first <@U_BOT>"},
                    {"ts": "602.0", "thread_ts": "600.0", "user": "U_JEFF", "text": "second <@U_BOT>"},
                ]
            ]
        },
    )
    ledger: dict[str, Any] = {
        "acked_mentions": {},
        "last_scanned_ts": {"C_TEST": "500.0"},
        "bot_user_id": "U_BOT",
    }

    stats = process_channel(api, channel_id="C_TEST", cfg=cfg, ledger=ledger, bot_user_id="U_BOT")

    assert stats["mentions"] == 2
    # Only 1 ack should be sent — the second mention is covered by the first ack.
    assert stats["sent"] == 1, (
        f"Expected 1 ack (first ack covers second mention), got {stats['sent']}"
    )
    assert stats["already_replied"] == 1
    assert len(api.sent_messages) == 1
