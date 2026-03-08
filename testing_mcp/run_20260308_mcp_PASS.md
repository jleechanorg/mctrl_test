# Real MCP ACP Verification — 2026-03-08 Run PASS

Run timestamp: 20260308T021500Z
Bead: ORCH-mcp-fa1d77
Branch: feat/mvp-loopback-supervisor
Agent CLI: minimax (real MiniMax-routed Claude)
Duration: 173.56s (2 passed)

---

## Trigger Path

- Input: `openclaw agent --agent main --message "..." --json` (ACP gateway)
- NOT Slack Socket Mode — direct ACP subprocess call
- Smoke run_id: `7f0760b8` — status=ok, non-empty reply confirmed

---

## Proved

- ACP smoke: `openclaw agent` returned status=ok with non-empty reply (run_id=7f0760b8)
- Real ai_orch session spawned: `session=ai-minimax-dfa2c0 worktree=/tmp/ai-orch-worktrees/ai-orch-35735`
- Real tmux session ran and exited within timeout
- `reconcile_registry_once` ran with ZERO monkeypatching; detected dead session
- Event emitted: `task_finished`
- Agent commit confirmed from git log: `89f2d45b79 e2e: done`
- outbox drained 0 (supervisor delivered via notify_slack_done during reconcile)
- Slack DM landed in D0AFTLEJGJU: `:white_check_mark: *Task done: ORCH-mcp-fa1d77*` at ts=1772935887.653769
- Raw Slack API response saved: `artifacts/slack_dm_fa1d77.json` (ok=true, 2 messages)
- pytest result: **2 passed in 173.56s**

## Not Proved

- Slack thread reply: not attempted by design (`slack_trigger_ts=None` — trigger was ACP, not Slack)

---

## Claim-to-Artifact Map

| Claim | Artifact | Key Field |
|---|---|---|
| ACP smoke: status=ok, run_id=7f0760b8 | `mcp_pytest_run.txt` line 11 | `status=ok reply non-empty` |
| bead ORCH-mcp-fa1d77 dispatched | `mcp_pytest_run.txt` line 15 | `session=ai-minimax-dfa2c0` |
| agent commit 89f2d45b79 "e2e: done" | `mcp_pytest_run.txt` line 21; on-disk `git show 89f2d45b79` | `+e2e-done.txt: ORCH-mcp-fa1d77 done` |
| 2 passed in 173.56s | `mcp_pytest_run.txt` line 28 | verbatim pytest result line |
| Slack DM landed | `slack_dm_fa1d77.json` | `ok=true`, `ts=1772935887.653769`, text contains `ORCH-mcp-fa1d77` |
| No Slack thread reply | `test_mcp_dispatch_roundtrip.py` line 194 | `slack_trigger_ts=None` |

---

## Evidence Artifacts

| File | Purpose |
|---|---|
| `mcp_pytest_run.txt` | Raw pytest -v -s transcript (collection_log) |
| `slack_dm_fa1d77.json` | Raw `conversations.history` API response for ORCH-mcp-fa1d77 DMs |
| `run_20260308_mcp_PASS.md` | This run report |
| `test_mcp_dispatch_roundtrip.py` | Test source (no mocks, no monkeypatching) |

## Key Difference from testing_llm/

| | testing_llm/ | testing_mcp/ |
|---|---|---|
| Input trigger | Slack Socket Mode (`_slack_post`) | `openclaw agent` ACP gateway |
| Slack Socket Mode required | Yes (input + output) | Output only (DM) |
| Thread reply verified | Yes (`conversations.replies`) | No (not proved — by design) |
| Determinism | Depends on Slack connection | Direct subprocess |
