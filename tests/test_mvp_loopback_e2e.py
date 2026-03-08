"""MVP loopback E2E tests.

test_e2e_registry_to_outbox_to_delivery
  Pure unit-level flow: registry → reconciler → outbox → drain.
  No network calls; fully deterministic.

test_slack_loopback_roundtrip  [REAL — always runs, requires Slack tokens + ai_orch in env]
  Full end-to-end proof through every real system path:
  1. jleechan posts trigger to #ai-slack-test (SLACK_USER_TOKEN)
  2. dispatch() spawns a real ai_orch agent in a real git worktree via real tmux
  3. Agent commits and exits — supervisor detects the real tmux session death
  4. reconcile_registry_once runs with ZERO monkeypatching
  5. notify_slack_done posts real DM + threaded reply under trigger_ts
  6. Test polls DM + conversations.replies to assert both landed

  No monkeypatching of any kind.
  Real: ai_orch, tmux, git, Slack inbound, Slack outbound, OpenClaw notifier.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

import pytest

from orchestration.dispatch_task import dispatch
from orchestration.openclaw_notifier import (
    SLACK_DM_CHANNEL as _DM_CHANNEL,
    SLACK_TRIGGER_CHANNEL as _AI_GENERAL,
    drain_outbox,
    read_outbox,
)
from orchestration.reconciliation import reconcile_registry_once
from orchestration.session_registry import BeadSessionMapping, get_mapping, upsert_mapping

MCTRL_ROOT = Path(__file__).resolve().parent.parent.parent


def _slack_post(token: str, channel: str, text: str) -> dict[str, Any]:
    body = json.dumps({"channel": channel, "text": text}).encode()
    req = Request(
        "https://slack.com/api/chat.postMessage",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def _slack_history(token: str, channel: str, oldest: str, limit: int = 20) -> list[dict[str, Any]]:
    url = (
        f"https://slack.com/api/conversations.history"
        f"?channel={channel}&oldest={oldest}&limit={limit}&inclusive=false"
    )
    req = Request(url, headers={"Authorization": f"Bearer {token}"})
    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read()).get("messages", [])


def _poll_for_text(
    token: str, channel: str, needle: str, oldest: str,
    timeout: float = 20.0, interval: float = 2.0,
) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            msgs = _slack_history(token, channel, oldest)
            if any(needle in m.get("text", "") for m in msgs):
                return True
        except URLError:
            pass
        time.sleep(interval)
    return False


def _poll_for_thread_reply(
    token: str, channel: str, thread_ts: str, needle: str,
    timeout: float = 20.0, interval: float = 2.0,
) -> bool:
    """Poll conversations.replies for a message containing needle in the given thread."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            url = (
                f"https://slack.com/api/conversations.replies"
                f"?channel={channel}&ts={thread_ts}&limit=20"
            )
            req = Request(url, headers={"Authorization": f"Bearer {token}"})
            with urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
            msgs = data.get("messages", [])
            # Skip index 0 (the parent message itself); check replies
            if any(needle in m.get("text", "") for m in msgs[1:]):
                return True
        except URLError:
            pass
        time.sleep(interval)
    return False


def test_e2e_registry_to_outbox_to_delivery(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    registry = tmp_path / "registry.jsonl"
    outbox = tmp_path / "outbox.jsonl"

    upsert_mapping(
        BeadSessionMapping.create(
            bead_id="ORCH-e2e",
            session_name="session-e2e",
            worktree_path="/tmp/wt-e2e",
            branch="feat/orch-e2e",
            agent_cli="codex",
            status="in_progress",
        ),
        registry_path=str(registry),
    )

    # Supervisor sees missing session, so it should transition and queue loopback.
    # Unit test must not post real Slack or OpenClaw messages.
    # Stub the underlying sender (not notify_openclaw itself) so enqueue_outbox
    # still runs on failure — that is what this test exercises.
    monkeypatch.setattr("orchestration.reconciliation.run_tmux_sessions", lambda: set())
    monkeypatch.setattr("orchestration.openclaw_notifier._send_via_mcp_agent_mail", lambda p: False)
    monkeypatch.setattr("orchestration.reconciliation.notify_slack_done", lambda p: False)
    emitted = reconcile_registry_once(
        registry_path=str(registry),
        outbox_path=str(outbox),
    )

    assert len(emitted) == 1
    assert emitted[0]["event"] == "task_needs_human"
    assert emitted[0]["bead_id"] == "ORCH-e2e"

    mapping = get_mapping("ORCH-e2e", registry_path=str(registry))
    assert mapping is not None
    assert mapping.status == "needs_human"

    queued = read_outbox(outbox_path=str(outbox))
    assert len(queued) == 1
    assert queued[0]["bead_id"] == "ORCH-e2e"

    delivered = drain_outbox(send_fn=lambda _: True, outbox_path=str(outbox))
    assert delivered == 1
    assert read_outbox(outbox_path=str(outbox)) == []


def test_slack_loopback_roundtrip(tmp_path: Path) -> None:
    """Full real-system loopback proof. No monkeypatching of any kind.

    Proves the complete chain through every real system path:
      1. jleechan posts trigger to #ai-slack-test (real Slack, SLACK_USER_TOKEN)
      2. dispatch() calls ai_orch → real tmux session + real git worktree
      3. Agent makes a real git commit and exits — tmux session dies for real
      4. reconcile_registry_once detects the real dead session (no patches)
      5. notify_slack_done posts real DM + real threaded reply
      6. Poll Slack API to confirm DM and thread reply both landed

    Requires: SLACK_USER_TOKEN, OPENCLAW_SLACK_BOT_TOKEN, ai_orch in PATH
    Duration: 3–10 minutes (real agent execution time)
    """
    user_token = os.environ.get("SLACK_USER_TOKEN", "")
    bot_token = (
        os.environ.get("OPENCLAW_SLACK_BOT_TOKEN")
        or os.environ.get("SLACK_BOT_TOKEN")
        or ""
    )
    assert user_token, "SLACK_USER_TOKEN must be set (source ~/.profile)"
    assert bot_token, "OPENCLAW_SLACK_BOT_TOKEN must be set — bot token required to verify bot posted"
    assert subprocess.run(["which", "ai_orch"], capture_output=True).returncode == 0, (
        "ai_orch must be in PATH"
    )

    bead_id = f"ORCH-e2e-{uuid.uuid4().hex[:6]}"
    registry = tmp_path / "registry.jsonl"
    outbox = tmp_path / "outbox.jsonl"

    # Step 1: Post real trigger as jleechan.
    ts_before = str(time.time() - 2)
    trigger_text = f"[mctrl-e2e] dispatch test {bead_id}"
    result = _slack_post(user_token, _AI_GENERAL, trigger_text)
    assert result.get("ok"), f"Trigger post failed: {result.get('error')}"
    trigger_ts = result["ts"]

    # Step 2: Real dispatch via ai_orch. Creates real tmux session + real git worktree.
    # Task is minimal: write one file and commit so _worktree_has_commits detects it.
    task = (
        f"Create a file named e2e-done.txt containing the text '{bead_id} done'. "
        "Then run: git add e2e-done.txt && git commit -m 'e2e: done'. Then stop."
    )
    mapping = dispatch(
        bead_id=bead_id,
        task=task,
        slack_trigger_ts=trigger_ts,
        agent_cli="minimax",
        registry_path=str(registry),
    )
    session_name = mapping.session_name

    # Step 3: Wait for the real tmux session to exit (agent finished).
    # Timeout 8 minutes — real agent execution for a trivial task.
    deadline = time.monotonic() + 480
    while time.monotonic() < deadline:
        if subprocess.run(
            ["tmux", "has-session", "-t", session_name],
            capture_output=True,
        ).returncode != 0:
            break
        time.sleep(5)
    else:
        pytest.fail(f"tmux session {session_name!r} still alive after 8 minutes")

    # Step 4: Run the real reconciler — ZERO monkeypatching.
    # It reads the real registry, checks real tmux (session is dead), checks real git.
    emitted = reconcile_registry_once(
        registry_path=str(registry),
        outbox_path=str(outbox),
    )

    assert len(emitted) == 1, f"Expected 1 event, got {len(emitted)}: {emitted}"
    assert emitted[0]["event"] == "task_finished", (
        f"Expected task_finished but got {emitted[0]['event']} — "
        "agent may not have committed; check session logs"
    )
    assert emitted[0]["bead_id"] == bead_id

    # Capture git log evidence: commits the agent made since spawn.
    final_mapping = get_mapping(bead_id, registry_path=str(registry))
    assert final_mapping is not None
    assert final_mapping.status == "finished"

    git_log_result = subprocess.run(
        ["git", "log", "--oneline", f"{final_mapping.start_sha}..HEAD"],
        cwd=final_mapping.worktree_path,
        capture_output=True,
        text=True,
        timeout=10,
    )
    agent_commits = git_log_result.stdout.strip()
    assert agent_commits, (
        f"git log {final_mapping.start_sha}..HEAD in {final_mapping.worktree_path} "
        "returned no commits — contradicts task_finished classification"
    )
    # Print for evidence capture in CI / test output
    print(f"\n[evidence] agent commits:\n{agent_commits}")

    # Step 5: Verify real Slack DM landed.
    dm_found = _poll_for_text(bot_token, _DM_CHANNEL, bead_id, ts_before, timeout=30)
    assert dm_found, f"No DM mentioning {bead_id} in {_DM_CHANNEL} within 30s"

    # Step 6: Verify real threaded reply under original trigger.
    thread_found = _poll_for_thread_reply(
        bot_token, _AI_GENERAL, trigger_ts, bead_id, timeout=30
    )
    assert thread_found, (
        f"No threaded reply mentioning {bead_id} under trigger {trigger_ts} "
        f"in {_AI_GENERAL} within 30s"
    )
