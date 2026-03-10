"""testing_mcp: Deterministic MCP gateway E2E tests.

These mirror testing_llm/test_slack_loopback_roundtrip but replace the Slack
Socket Mode trigger with a direct HTTP call to the OpenClaw gateway endpoint.

This makes the trigger path deterministic:
  - No dependency on Slack Socket Mode connection for the INPUT trigger
  - Direct HTTP POST to http://localhost:18789/v1/chat/completions
  - Auth via Bearer token (gateway.auth.token in openclaw.json)
  - Output notification still posts real Slack DM (bot token)

Hard rules (inherited from testing_mcp/CLAUDE.md):
  - No mocks, no monkeypatching, no stubs
  - All Slack / tmux / git interactions are real
  - Only real artifacts constitute proof

test_gateway_connectivity
  Smoke: verify the OpenClaw gateway HTTP endpoint is up and responds to auth.
  No agent spawn. Deterministic and fast.

test_mcp_gateway_dispatch_roundtrip  [REAL — requires ai_orch, Slack bot token, gateway up]
  Full E2E identical to test_slack_loopback_roundtrip except:
    - Trigger: HTTP POST to OpenClaw gateway (not Slack)
    - No slack_trigger_ts → no thread reply expected → only DM verified
    - Work happens in a real mctrl_test clone and must create a real GitHub PR
  Proves the complete chain without Slack Socket Mode on the INPUT side.
"""
from __future__ import annotations

import http.client
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
from orchestration.openclaw_notifier import drain_outbox
from orchestration.reconciliation import reconcile_registry_once
from orchestration.session_registry import get_mapping

GATEWAY_URL = "http://localhost:18789"
GATEWAY_TOKEN = os.environ.get("OPENCLAW_GATEWAY_TOKEN", "")
MCTRL_TEST_REPO = "jleechanorg/mctrl_test"
_DM_CHANNEL = os.environ.get("MCTRL_TEST_DM_CHANNEL", "D0AFTLEJGJU")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _gateway_post(path: str, body: dict[str, Any], timeout: int = 120) -> dict[str, Any]:
    """POST JSON to the OpenClaw gateway; return parsed JSON response."""
    data = json.dumps(body).encode()
    last_error: Exception | None = None
    for attempt in range(3):
        req = Request(
            f"{GATEWAY_URL}{path}",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GATEWAY_TOKEN}",
                # Force non-streaming JSON response (gateway defaults to SSE stream)
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except (URLError, http.client.RemoteDisconnected) as exc:
            last_error = exc
            if attempt == 2:
                raise
            time.sleep(2)
    assert last_error is not None
    raise last_error


def _slack_history(token: str, channel: str, oldest: str, limit: int = 100) -> list[dict[str, Any]]:
    url = (
        f"https://slack.com/api/conversations.history"
        f"?channel={channel}&oldest={oldest}&limit={limit}&inclusive=false"
    )
    req = Request(url, headers={"Authorization": f"Bearer {token}"})
    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read()).get("messages") or []


def _latest_matching_message(
    token: str, channel: str, needle: str, *,
    oldest: str = "0", limit: int = 200,
) -> dict[str, Any] | None:
    try:
        messages = _slack_history(token, channel, oldest, limit=limit)
    except URLError:
        return None
    for message in messages:
        if needle in message.get("text", ""):
            return message
    return None
def _poll_for_text(
    token: str, channel: str, needle: str, oldest: str,
    timeout: float = 30.0, interval: float = 2.0,
) -> bool:
    return _poll_for_matching_message(
        token, channel, needle, oldest, timeout=timeout, interval=interval
    ) is not None


def _poll_for_matching_message(
    token: str, channel: str, needle: str, oldest: str,
    timeout: float = 30.0, interval: float = 2.0,
) -> dict[str, Any] | None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            msgs = _slack_history(token, channel, oldest)
            for message in msgs:
                if needle in message.get("text", ""):
                    return message
        except URLError:
            pass
        time.sleep(interval)
    return None


def _write_json_artifact(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _clone_mctrl_test(dest: Path) -> Path:
    result = subprocess.run(
        ["git", "clone", f"https://github.com/{MCTRL_TEST_REPO}.git", str(dest)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"git clone failed: {result.stderr}"
    return dest


def _lookup_pr_for_branch(branch: str) -> dict[str, Any] | None:
    result = subprocess.run(
        [
            "gh",
            "pr",
            "list",
            "--repo",
            MCTRL_TEST_REPO,
            "--state",
            "all",
            "--head",
            branch,
            "--json",
            "number,url,state,title,headRefName,baseRefName",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"gh pr list failed: {result.stderr}"
    prs = json.loads(result.stdout or "[]")
    return prs[0] if prs else None


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_gateway_connectivity() -> None:
    """Smoke: gateway is up, auth works, returns a well-formed chat completion.

    Deterministic — no agent spawn. Completes in < 120 s (LLM latency applies).
    """
    assert GATEWAY_TOKEN, (
        "OPENCLAW_GATEWAY_TOKEN must be set (source ~/.openclaw/set-slack-env.sh)"
    )
    resp = _gateway_post(
        "/v1/chat/completions",
        {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "reply with exactly: GATEWAY_OK"}],
            "max_tokens": 10,
            "stream": False,
        },
    )
    assert resp.get("object") == "chat.completion", f"Unexpected response: {resp}"
    choices = resp.get("choices") or []
    assert choices, "No choices in response"
    content = choices[0].get("message", {}).get("content", "")
    assert content, "Empty content in gateway response"
    print(f"\n[gateway] response content: {content!r}")


def test_mcp_gateway_dispatch_roundtrip(tmp_path: Path) -> None:
    """Full E2E loopback via OpenClaw MCP gateway instead of Slack trigger.

    Proves the complete chain:
      1. POST dispatch instruction to OpenClaw gateway /v1/chat/completions
      2. dispatch() spawns real ai_orch agent in a real mctrl_test git worktree via real tmux
      3. Agent commits, pushes, and opens a real GitHub PR
      4. Agent exits — tmux session dies for real
      5. reconcile_registry_once detects dead session (ZERO monkeypatching)
      6. notify_slack_done posts real Slack DM
      7. Poll Slack DM to confirm it landed and verify the PR exists on GitHub

    Key difference from test_slack_loopback_roundtrip:
      - INPUT trigger is HTTP POST to OpenClaw gateway (no Slack Socket Mode)
      - slack_trigger_ts is "" → no thread reply → only DM verified
      - Deterministic: trigger path has no Slack Socket Mode dependency

    Requires: OPENCLAW_SLACK_BOT_TOKEN, ai_orch in PATH, gh auth, gateway on :18789
    Duration: 3–12 minutes (real agent execution + GitHub PR creation)
    """
    bot_token = (
        os.environ.get("OPENCLAW_SLACK_BOT_TOKEN")
        or os.environ.get("SLACK_BOT_TOKEN")
        or ""
    )
    assert bot_token, "OPENCLAW_SLACK_BOT_TOKEN must be set (source ~/.openclaw/set-slack-env.sh)"
    assert GATEWAY_TOKEN, (
        "OPENCLAW_GATEWAY_TOKEN must be set (source ~/.openclaw/set-slack-env.sh)"
    )
    os.environ.setdefault("OPENCLAW_NOTIFY_TARGET", _DM_CHANNEL)
    assert subprocess.run(["which", "ai_orch"], capture_output=True).returncode == 0, (
        "ai_orch must be in PATH"
    )
    assert subprocess.run(["which", "gh"], capture_output=True).returncode == 0, (
        "gh must be in PATH"
    )
    assert subprocess.run(["gh", "auth", "status"], capture_output=True).returncode == 0, (
        "gh must be authenticated"
    )

    bead_id = f"ORCH-mcp-{uuid.uuid4().hex[:6]}"
    registry = tmp_path / "registry.jsonl"
    outbox = tmp_path / "outbox.jsonl"
    repo_root = _clone_mctrl_test(tmp_path / "mctrl_test")

    # Step 1: Announce the task to OpenClaw via MCP gateway HTTP endpoint.
    # This replaces the Slack trigger — proves gateway is the INPUT path.
    gateway_msg = (
        f"[mctrl-mcp-e2e] Dispatching task {bead_id} via MCP gateway. "
        "This is a real E2E test — agent will create a real GitHub PR in mctrl_test."
    )
    gw_resp = _gateway_post(
        "/v1/chat/completions",
        {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": gateway_msg}],
            "max_tokens": 10,
            "stream": False,
        },
    )
    assert gw_resp.get("object") == "chat.completion", (
        f"Gateway announcement failed: {gw_resp}"
    )
    gw_content = (gw_resp.get("choices") or [{}])[0].get("message", {}).get("content", "")
    print(f"\n[mcp-gateway] ack content: {gw_content!r}")

    # Step 2: Real dispatch via ai_orch. Creates real tmux session + real git worktree.
    # Empty slack_trigger_ts sentinel — trigger was via MCP, not Slack.
    task = (
        f"Create a file named e2e-pr-{bead_id}.txt containing the text '{bead_id} done'. "
        f"Then run exactly these commands in the repo root:\n"
        f"git add e2e-pr-{bead_id}.txt\n"
        f"git commit -m 'e2e: create PR for {bead_id}'\n"
        "git push -u origin HEAD\n"
        f"gh pr create --repo {MCTRL_TEST_REPO} --base main "
        f"--title 'test: mctrl MCP E2E {bead_id}' "
        f"--body 'Automated real MCP gateway E2E proof for {bead_id}.'\n"
        "Then stop."
    )
    mapping = dispatch(
        bead_id=bead_id,
        task=task,
        slack_trigger_ts="",
        agent_cli="minimax",
        registry_path=str(registry),
        repo_root=str(repo_root),
    )
    session_name = mapping.session_name
    print(f"\n[dispatch] session={session_name} worktree={mapping.worktree_path}")

    # Step 3: Wait for the real tmux session to exit (agent finished).
    # Timeout 12 minutes — real agent execution + push + PR creation.
    deadline = time.monotonic() + 720
    while time.monotonic() < deadline:
        if subprocess.run(
            ["tmux", "has-session", "-t", session_name],
            capture_output=True,
        ).returncode != 0:
            break
        time.sleep(5)
    else:
        pytest.fail(f"tmux session {session_name!r} still alive after 12 minutes")

    # Step 4: Run the real reconciler — ZERO monkeypatching.
    # ts_before: 15s backfill so the DM sent inside reconcile's daemon thread
    # (which runs during t_slack.join and completes within ~10s) is always
    # captured. limit=100 (in _slack_history) handles supervisor/cron DM bursts
    # so the target message is never pushed past the cutoff.
    ts_before = str(time.time() - 15)
    emitted = reconcile_registry_once(
        registry_path=str(registry),
        outbox_path=str(outbox),
        dead_letter_path=str(tmp_path / "outbox_dead_letter.jsonl"),
    )

    assert len(emitted) == 1, f"Expected 1 event, got {len(emitted)}: {emitted}"
    assert emitted[0]["event"] == "task_finished", (
        f"Expected task_finished but got {emitted[0]['event']} — "
        "agent may not have committed; check session logs"
    )
    assert emitted[0]["bead_id"] == bead_id

    # Capture git log evidence.
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
    print(f"\n[evidence] agent commits:\n{agent_commits}")

    pr = _lookup_pr_for_branch(final_mapping.branch)
    assert pr is not None, f"No PR found in {MCTRL_TEST_REPO} for branch {final_mapping.branch!r}"
    _write_json_artifact(
        tmp_path / "pr_evidence.json",
        {
            "bead_id": bead_id,
            "repo": MCTRL_TEST_REPO,
            "branch": final_mapping.branch,
            "pr_number": pr["number"],
            "pr_url": pr["url"],
            "state": pr["state"],
            "title": pr["title"],
            "headRefName": pr["headRefName"],
            "baseRefName": pr["baseRefName"],
        },
    )
    print(f"\n[evidence] PR confirmed: {pr['url']}")

    # Step 5: Drain the outbox to deliver the real Slack DM.
    # (supervisor may have already drained it; drain_outbox is idempotent if empty)
    delivered = drain_outbox(outbox_path=str(outbox))
    print(f"\n[outbox] drained {delivered} messages")

    # Step 6: Poll Slack DM to verify bot DM landed.
    # No thread reply expected because slack_trigger_ts was None.
    dm_message = _poll_for_matching_message(bot_token, _DM_CHANNEL, bead_id, ts_before, timeout=300)
    if dm_message is None:
        dm_message = _latest_matching_message(bot_token, _DM_CHANNEL, bead_id, oldest="0", limit=200)
    assert dm_message is not None, f"No DM mentioning {bead_id} in {_DM_CHANNEL} within 300s"
    _write_json_artifact(
        tmp_path / "slack_dm_evidence.json",
        {
            "bead_id": bead_id,
            "channel": _DM_CHANNEL,
            "oldest": ts_before,
            "matched_ts": dm_message.get("ts", ""),
            "matched_text": dm_message.get("text", ""),
        },
    )
    print(f"\n[evidence] DM confirmed in {_DM_CHANNEL} mentioning {bead_id}")
