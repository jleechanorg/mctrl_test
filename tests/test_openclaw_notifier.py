from __future__ import annotations

import json
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import MagicMock, patch

from orchestration.openclaw_notifier import (
    SLACK_DM_CHANNEL,
    SLACK_TRIGGER_CHANNEL,
    drain_outbox,
    notify_openclaw,
    notify_slack_started,
    read_outbox,
)


def test_notify_openclaw_success_does_not_enqueue(tmp_path: Path) -> None:
    outbox = tmp_path / "outbox.jsonl"
    payload = {"event": "task_finished", "bead_id": "ORCH-1"}

    delivered = notify_openclaw(
        payload,
        send_fn=lambda _: True,
        outbox_path=str(outbox),
    )

    assert delivered is True
    assert read_outbox(outbox_path=str(outbox)) == []


def test_notify_openclaw_failure_enqueues(tmp_path: Path) -> None:
    outbox = tmp_path / "outbox.jsonl"
    payload = {"event": "task_needs_human", "bead_id": "ORCH-2"}

    delivered = notify_openclaw(
        payload,
        send_fn=lambda _: False,
        outbox_path=str(outbox),
    )

    assert delivered is False
    assert read_outbox(outbox_path=str(outbox)) == [payload]


def test_drain_outbox_delivers_and_clears(tmp_path: Path) -> None:
    outbox = tmp_path / "outbox.jsonl"
    payloads = [
        {"event": "task_needs_human", "bead_id": "ORCH-1"},
        {"event": "task_finished", "bead_id": "ORCH-2"},
    ]
    for payload in payloads:
        notify_openclaw(payload, send_fn=lambda _: False, outbox_path=str(outbox))

    delivered = drain_outbox(send_fn=lambda _: True, outbox_path=str(outbox))

    assert delivered == 2
    assert read_outbox(outbox_path=str(outbox)) == []


def _make_urlopen_mock(ok: bool = True):
    """Return a mock urlopen context manager that returns Slack ok/error JSON."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"ok": ok}).encode()
    mock_resp.__enter__ = lambda s: mock_resp
    mock_resp.__exit__ = MagicMock(return_value=False)
    return MagicMock(return_value=mock_resp)


@patch.dict("os.environ", {"OPENCLAW_SLACK_BOT_TOKEN": "xoxb-test"}, clear=False)
@patch("orchestration.openclaw_notifier.urlopen")
def test_notify_slack_started_posts_dm(mock_urlopen) -> None:
    mock_urlopen.side_effect = _make_urlopen_mock()
    payload = {
        "bead_id": "ORCH-1",
        "session": "ai-test-abc",
        "branch": "feat/x",
        "worktree_path": "/tmp/wt-x",
        "agent_cli": "minimax",
        "slack_trigger_ts": "",
    }

    result = notify_slack_started(payload)

    assert result is True
    assert mock_urlopen.call_count == 1  # DM only (no trigger_ts)
    body = json.loads(mock_urlopen.call_args.args[0].data)
    assert body["channel"] == SLACK_DM_CHANNEL
    assert "ORCH-1" in body["text"]
    assert ":rocket:" in body["text"]


@patch.dict("os.environ", {"OPENCLAW_SLACK_BOT_TOKEN": "xoxb-test"}, clear=False)
@patch("orchestration.openclaw_notifier.urlopen")
def test_notify_slack_started_threads_under_trigger(mock_urlopen) -> None:
    mock_urlopen.side_effect = _make_urlopen_mock()
    payload = {
        "bead_id": "ORCH-2",
        "session": "ai-test-def",
        "branch": "feat/y",
        "worktree_path": "/tmp/wt-y",
        "agent_cli": "minimax",
        "slack_trigger_ts": "1234567890.123456",
    }

    result = notify_slack_started(payload)

    assert result is True
    assert mock_urlopen.call_count == 2  # DM + thread reply
    calls = [json.loads(c.args[0].data) for c in mock_urlopen.call_args_list]
    assert any(c.get("thread_ts") == "1234567890.123456" for c in calls)
    assert any(c["channel"] == SLACK_TRIGGER_CHANNEL for c in calls)


@patch.dict("os.environ", {}, clear=True)
def test_notify_slack_started_no_token_returns_false() -> None:
    result = notify_slack_started({"bead_id": "ORCH-3"})
    assert result is False


@patch.dict("os.environ", {"OPENCLAW_SLACK_BOT_TOKEN": "xoxb-test"}, clear=False)
@patch("orchestration.openclaw_notifier.urlopen")
def test_notify_slack_started_includes_agent_cli_and_session(mock_urlopen) -> None:
    mock_urlopen.side_effect = _make_urlopen_mock()
    payload = {
        "bead_id": "ORCH-4",
        "session": "ai-minimax-xyz",
        "branch": "feat/z",
        "worktree_path": "/tmp/wt-z",
        "agent_cli": "minimax",
        "slack_trigger_ts": "",
    }

    notify_slack_started(payload)

    body = json.loads(mock_urlopen.call_args.args[0].data)
    assert "ai-minimax-xyz" in body["text"]
    assert "minimax" in body["text"]


@patch.dict("os.environ", {"OPENCLAW_NOTIFY_AGENT": "jleechanclaw"}, clear=False)
@patch("orchestration.openclaw_notifier.subprocess.run")
def test_notify_openclaw_uses_openclaw_agent_when_configured(mock_run, tmp_path: Path) -> None:
    outbox = tmp_path / "outbox.jsonl"
    payload = {"event": "task_finished", "bead_id": "ORCH-9"}
    mock_run.return_value = CompletedProcess(args=["openclaw"], returncode=0)

    delivered = notify_openclaw(payload, outbox_path=str(outbox))

    assert delivered is True
    assert mock_run.call_args.args[0][:4] == [
        "openclaw",
        "agent",
        "--agent",
        "jleechanclaw",
    ]
    assert read_outbox(outbox_path=str(outbox)) == []
