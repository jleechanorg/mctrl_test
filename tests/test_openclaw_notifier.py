from __future__ import annotations

import json
from pathlib import Path
import subprocess
from subprocess import CompletedProcess
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from orchestration.openclaw_notifier import (
    DeliveryAttempt,
    _RETRY_DELAYS_SECONDS,
    openclaw_notification_max_runtime_seconds,
    _send_via_mcp_agent_mail,
    _send_with_retries,
    _send_via_openclaw_agent,
    default_outbox_path,
    drain_outbox,
    notify_openclaw,
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


def test_default_outbox_path_uses_mctrl_home(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MCTRL_OUTBOX_PATH", raising=False)
    monkeypatch.setenv("MCTRL_HOME", "/tmp/mctrl-home")

    assert default_outbox_path() == "/tmp/mctrl-home/messages/outbox.jsonl"


def test_default_outbox_path_prefers_explicit_outbox_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MCTRL_HOME", "/tmp/mctrl-home")
    monkeypatch.setenv("MCTRL_OUTBOX_PATH", "/tmp/custom/outbox.jsonl")

    assert default_outbox_path() == "/tmp/custom/outbox.jsonl"


def test_notify_openclaw_retries_transient_sender_before_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    attempts: list[int] = []

    def flaky_sender(_payload: dict[str, object]) -> DeliveryAttempt:
        attempts.append(1)
        if len(attempts) < 3:
            return DeliveryAttempt(delivered=False, transient=True)
        return DeliveryAttempt(delivered=True)

    monkeypatch.setattr("orchestration.openclaw_notifier.time.sleep", lambda _seconds: None)
    outbox = tmp_path / "outbox.jsonl"

    delivered = notify_openclaw(
        {"event": "task_finished", "bead_id": "ORCH-3"},
        send_fn=flaky_sender,
        outbox_path=str(outbox),
    )

    assert delivered is True
    assert len(attempts) == 3
    assert read_outbox(outbox_path=str(outbox)) == []


def test_send_with_retries_treats_timeout_exception_as_transient() -> None:
    attempts: list[int] = []
    sleeps: list[float] = []

    def flaky_sender(_payload: dict[str, object]) -> bool:
        attempts.append(1)
        if len(attempts) < 3:
            raise TimeoutError("temporary timeout")
        return True

    attempt = _send_with_retries(
        {"event": "task_finished", "bead_id": "ORCH-timeout"},
        sender=flaky_sender,
        sleep_fn=sleeps.append,
    )

    assert attempt.delivered is True
    assert len(attempts) == 3
    assert sleeps == [1, 3]


def test_send_with_retries_treats_missing_binary_as_non_transient() -> None:
    attempt = _send_with_retries(
        {"event": "task_finished", "bead_id": "ORCH-missing-bin"},
        sender=lambda _payload: (_ for _ in ()).throw(FileNotFoundError("openclaw not found")),
        sleep_fn=lambda _seconds: None,
    )

    assert attempt.delivered is False
    assert attempt.transient is False


def test_notify_openclaw_enqueues_after_non_transient_failure(tmp_path: Path) -> None:
    outbox = tmp_path / "outbox.jsonl"

    delivered = notify_openclaw(
        {"event": "task_needs_human", "bead_id": "ORCH-4"},
        send_fn=lambda _payload: DeliveryAttempt(delivered=False, transient=False),
        outbox_path=str(outbox),
    )

    assert delivered is False
    assert read_outbox(outbox_path=str(outbox)) == [
        {"event": "task_needs_human", "bead_id": "ORCH-4"}
    ]


def test_notify_openclaw_monkeypatched_sleep_avoids_real_retry_delay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    attempts: list[int] = []
    sleeps: list[float] = []

    def flaky_sender(_payload: dict[str, object]) -> DeliveryAttempt:
        attempts.append(1)
        if len(attempts) < 3:
            return DeliveryAttempt(delivered=False, transient=True)
        return DeliveryAttempt(delivered=True)

    monkeypatch.setattr("orchestration.openclaw_notifier.time.sleep", sleeps.append)
    outbox = tmp_path / "outbox.jsonl"

    delivered = notify_openclaw(
        {"event": "task_finished", "bead_id": "ORCH-sleep"},
        send_fn=flaky_sender,
        outbox_path=str(outbox),
    )

    assert delivered is True
    assert sleeps == [1, 3]
    assert read_outbox(outbox_path=str(outbox)) == []


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


@patch.dict("os.environ", {"OPENCLAW_NOTIFY_AGENT": "jleechanclaw"}, clear=False)
@patch("orchestration.openclaw_notifier.subprocess.run")
def test_notify_openclaw_uses_openclaw_agent_when_configured(mock_run, tmp_path: Path) -> None:
    outbox = tmp_path / "outbox.jsonl"
    payload = {"event": "task_finished", "bead_id": "ORCH-9"}
    mock_run.return_value = CompletedProcess(args=["openclaw"], returncode=0)

    delivered = notify_openclaw(payload, outbox_path=str(outbox))

    assert delivered is True
    assert mock_run.call_args.args[0][:6] == [
        "openclaw",
        "agent",
        "--agent",
        "jleechanclaw",
        "--thinking",
        "minimal",
    ]
    assert read_outbox(outbox_path=str(outbox)) == []


def test_send_via_openclaw_agent_marks_server_error_transient(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENCLAW_NOTIFY_AGENT", "main")
    result = SimpleNamespace(
        returncode=0,
        stdout=json.dumps({"error": "type:error,code:server_error,message:retry later"}),
        stderr="",
    )
    monkeypatch.setattr("orchestration.openclaw_notifier.subprocess.run", lambda *args, **kwargs: result)

    attempt = _send_via_openclaw_agent({"event": "task_finished", "bead_id": "ORCH-9"})

    assert attempt.delivered is False
    assert attempt.transient is True


def test_send_via_mcp_agent_mail_tries_fallback_after_transient_agent_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "orchestration.openclaw_notifier._send_via_openclaw_agent",
        lambda _payload: DeliveryAttempt(delivered=False, transient=True),
    )
    monkeypatch.setenv("OPENCLAW_PROJECT_KEY", "proj")
    monkeypatch.setenv("OPENCLAW_SENDER_NAME", "sender")
    monkeypatch.setenv("OPENCLAW_TO", "receiver")
    monkeypatch.setattr(
        "orchestration.openclaw_notifier.subprocess.run",
        lambda *args, **kwargs: CompletedProcess(args=["openclaw"], returncode=0, stdout="", stderr=""),
    )

    attempt = _send_via_mcp_agent_mail({"event": "task_finished", "bead_id": "ORCH-fallback"})

    assert attempt.delivered is True


def test_send_via_mcp_agent_mail_preserves_transient_state_when_fallback_fails_without_retry_hint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "orchestration.openclaw_notifier._send_via_openclaw_agent",
        lambda _payload: DeliveryAttempt(delivered=False, transient=True),
    )
    monkeypatch.setenv("OPENCLAW_PROJECT_KEY", "proj")
    monkeypatch.setenv("OPENCLAW_SENDER_NAME", "sender")
    monkeypatch.setenv("OPENCLAW_TO", "receiver")
    monkeypatch.setattr(
        "orchestration.openclaw_notifier.subprocess.run",
        lambda *args, **kwargs: CompletedProcess(
            args=["openclaw"],
            returncode=1,
            stdout="",
            stderr="permanent failure",
        ),
    )

    attempt = _send_via_mcp_agent_mail({"event": "task_finished", "bead_id": "ORCH-fallback-fail"})

    assert attempt.delivered is False
    assert attempt.transient is True


def test_send_via_mcp_agent_mail_fallback_runs_when_agent_call_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _raise_timeout(_payload: dict[str, object]) -> DeliveryAttempt:
        raise subprocess.TimeoutExpired(cmd=["openclaw", "agent"], timeout=60)

    monkeypatch.setattr(
        "orchestration.openclaw_notifier._send_via_openclaw_agent",
        _raise_timeout,
    )
    monkeypatch.setenv("OPENCLAW_PROJECT_KEY", "proj")
    monkeypatch.setenv("OPENCLAW_SENDER_NAME", "sender")
    monkeypatch.setenv("OPENCLAW_TO", "receiver")
    monkeypatch.setattr(
        "orchestration.openclaw_notifier.subprocess.run",
        lambda *args, **kwargs: CompletedProcess(args=["openclaw"], returncode=0, stdout="", stderr=""),
    )

    attempt = _send_via_mcp_agent_mail({"event": "task_finished", "bead_id": "ORCH-fallback-timeout"})

    assert attempt.delivered is True


def test_send_via_mcp_agent_mail_uses_openclaw_message_send_dm_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "orchestration.openclaw_notifier._send_via_openclaw_agent",
        lambda _payload: DeliveryAttempt(delivered=False, transient=True),
    )
    monkeypatch.delenv("OPENCLAW_PROJECT_KEY", raising=False)
    monkeypatch.delenv("OPENCLAW_SENDER_NAME", raising=False)
    monkeypatch.delenv("OPENCLAW_TO", raising=False)
    monkeypatch.setenv("OPENCLAW_NOTIFY_TARGET", "DTEST123")

    seen_commands: list[list[str]] = []

    def _fake_run(cmd: list[str], **kwargs) -> CompletedProcess[str]:
        seen_commands.append(cmd)
        return CompletedProcess(
            args=cmd,
            returncode=0,
            stdout=json.dumps(
                {"payload": {"ok": True, "result": {"messageId": "1.23", "channelId": "DTEST123"}}}
            ),
            stderr="",
        )

    monkeypatch.setattr("orchestration.openclaw_notifier.subprocess.run", _fake_run)

    attempt = _send_via_mcp_agent_mail({"event": "task_finished", "bead_id": "ORCH-message-send"})

    assert attempt.delivered is True
    assert seen_commands
    assert seen_commands[0][:4] == ["openclaw", "message", "send", "--channel"]
    assert "--target" in seen_commands[0]
    assert "DTEST123" in seen_commands[0]


def test_send_via_mcp_agent_mail_posts_thread_reply_when_trigger_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "orchestration.openclaw_notifier._send_via_openclaw_agent",
        lambda _payload: DeliveryAttempt(delivered=False, transient=True),
    )
    monkeypatch.delenv("OPENCLAW_PROJECT_KEY", raising=False)
    monkeypatch.delenv("OPENCLAW_SENDER_NAME", raising=False)
    monkeypatch.delenv("OPENCLAW_TO", raising=False)
    monkeypatch.setenv("OPENCLAW_NOTIFY_TARGET", "DTEST123")

    seen_commands: list[list[str]] = []

    def _fake_run(cmd: list[str], **kwargs) -> CompletedProcess[str]:
        seen_commands.append(cmd)
        return CompletedProcess(
            args=cmd,
            returncode=0,
            stdout=json.dumps({"payload": {"ok": True}}),
            stderr="",
        )

    monkeypatch.setattr("orchestration.openclaw_notifier.subprocess.run", _fake_run)

    attempt = _send_via_mcp_agent_mail(
        {
            "event": "task_finished",
            "bead_id": "ORCH-thread",
            "slack_trigger_ts": "123.456",
            "slack_trigger_channel": "CCHAN1",
        }
    )

    assert attempt.delivered is True
    assert len(seen_commands) == 2
    assert "--reply-to" not in seen_commands[0]
    assert "--reply-to" in seen_commands[1]
    assert "123.456" in seen_commands[1]
    assert "CCHAN1" in seen_commands[1]


def test_send_via_mcp_agent_mail_prefers_thread_delivery_before_agent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called: dict[str, int] = {"agent": 0}

    def _agent_stub(_payload: dict[str, object]) -> DeliveryAttempt:
        called["agent"] += 1
        return DeliveryAttempt(delivered=True)

    monkeypatch.setattr("orchestration.openclaw_notifier._send_via_openclaw_agent", _agent_stub)
    monkeypatch.setenv("OPENCLAW_NOTIFY_TARGET", "DTEST123")

    seen_commands: list[list[str]] = []

    def _fake_run(cmd: list[str], **kwargs) -> CompletedProcess[str]:
        seen_commands.append(cmd)
        return CompletedProcess(
            args=cmd,
            returncode=0,
            stdout=json.dumps({"payload": {"ok": True}}),
            stderr="",
        )

    monkeypatch.setattr("orchestration.openclaw_notifier.subprocess.run", _fake_run)

    attempt = _send_via_mcp_agent_mail(
        {
            "event": "task_finished",
            "bead_id": "ORCH-thread-first",
            "slack_trigger_ts": "123.456",
            "slack_trigger_channel": "CCHAN1",
        }
    )

    assert attempt.delivered is True
    assert called["agent"] == 0
    assert len(seen_commands) == 2
    assert "--reply-to" in seen_commands[1]


def test_send_via_mcp_agent_mail_prefers_message_delivery_before_agent_non_threaded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called: dict[str, int] = {"agent": 0}

    def _agent_stub(_payload: dict[str, object]) -> DeliveryAttempt:
        called["agent"] += 1
        return DeliveryAttempt(delivered=True)

    monkeypatch.setattr("orchestration.openclaw_notifier._send_via_openclaw_agent", _agent_stub)
    monkeypatch.setenv("OPENCLAW_NOTIFY_TARGET", "DTEST123")

    def _fake_run(cmd: list[str], **kwargs) -> CompletedProcess[str]:
        return CompletedProcess(
            args=cmd,
            returncode=0,
            stdout=json.dumps({"payload": {"ok": True}}),
            stderr="",
        )

    monkeypatch.setattr("orchestration.openclaw_notifier.subprocess.run", _fake_run)

    attempt = _send_via_mcp_agent_mail({"event": "task_finished", "bead_id": "ORCH-non-thread-first"})

    assert attempt.delivered is True
    assert called["agent"] == 0


def test_openclaw_notification_max_runtime_includes_agent_and_mcp_fallback_timeouts() -> None:
    expected = ((60 + 30) * (len(_RETRY_DELAYS_SECONDS) + 1)) + sum(_RETRY_DELAYS_SECONDS)
    assert openclaw_notification_max_runtime_seconds() == expected
