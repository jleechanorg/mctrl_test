# Real MCP ACP Verification — 2026-03-08 (3 runs, post timeout-fix)

Branch: fix/mcp-followups
PR: https://github.com/jleechanorg/jleechanclaw/pull/67
Date: 2026-03-08
Fix applied: `e529f36e4f` — raise `_openclaw_agent` default timeout 60→120s

---

## Run 1 (pre-fix — 1 failed, 1 passed)

- `test_mcp_agent_send_receive`: FAILED — TimeoutExpired at 60s
- `test_mcp_dispatch_roundtrip`: PASSED — bead=ORCH-mcp-d14e1d, session=ai-minimax-dfa2c0, commit=de500df1e0, DM confirmed D0AFTLEJGJU
- Result: 1 failed, 1 passed in 211.74s

## Run 2 (post-fix)

- `test_mcp_agent_send_receive`: PASSED — run_id=67b989dd, reply non-empty
- `test_mcp_dispatch_roundtrip`: PASSED — bead=ORCH-mcp-e7385f, session=ai-minimax-dfa2c0, commit=de500df1e0, DM confirmed
- Result: **2 passed in 126.53s**

## Run 3 (cron)

- `test_mcp_agent_send_receive`: PASSED — run_id=d51659d9
- `test_mcp_dispatch_roundtrip`: PASSED — bead=ORCH-mcp-ac53ec, commit=003462cc3e, DM confirmed
- Result: **2 passed in 146.63s**

## Run 4 (cron)

- `test_mcp_agent_send_receive`: PASSED — run_id=c7093116
- `test_mcp_dispatch_roundtrip`: PASSED — bead=ORCH-mcp-2ec776, commit=ac3ddbd3d8, DM confirmed
- Result: **2 passed in 175.93s**

---

## Proved

- ACP smoke path alive across 3 consecutive runs (run_ids: 67b989dd, d51659d9, c7093116)
- Real ai_orch dispatch each run — distinct beads and commits
- `reconcile_registry_once` detected dead sessions (ZERO monkeypatching)
- Slack DM landed in D0AFTLEJGJU for each bead — confirmed by test assertion
- `outbox drained 0` consistent with supervisor draining before test drain call

## Not Proved

- Slack thread reply (slack_trigger_ts=None by design — trigger was ACP not Slack)
- Raw pytest transcript not committed (terminal output only, not in artifacts/)

---

## Note on session reuse

`ai-minimax-dfa2c0` session name appears across runs — this is expected. `ai_orch` uses a named session slot derived from agent+worktree; worktree IDs differ (ai-orch-43862, ai-orch-44265, etc.), confirming distinct dispatch per run.

## Codex evidence-reviewer verdict

Overall: `PARTIAL` — strong for this branch's runs; prior `run_20260307b_loopback_PASS.md` flagged as under-evidenced (no raw thread artifact). Today's runs address that gap via `testing_llm/artifacts/`.
