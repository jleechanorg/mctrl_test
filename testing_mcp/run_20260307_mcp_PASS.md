# Real MCP ACP Verification — 2026-03-07 PASS

Run timestamp: 20260307T020000Z (approx)
Bead: ORCH-mcp-e63de9
Branch: feat/mvp-loopback-supervisor
Agent CLI: minimax (real MiniMax-routed Claude)
Duration: 115.61s

---

## Trigger Path

- Input: `openclaw agent --agent main --message "ACK ORCH-mcp-e63de9" --json`
- NOT Slack Socket Mode — direct ACP gateway call
- OpenClaw replied: `ACK ORCH-mcp-e63de9`

## Proved

- `openclaw agent` ACP trigger confirmed (status=ok, reply='ACK ORCH-mcp-e63de9')
- Real ai_orch session spawned via `dispatch()` → `ai_orch run --async --agent-cli minimax`
- Real tmux session ran and exited
- `reconcile_registry_once` ran with ZERO monkeypatching; detected dead session
- Event emitted: `task_finished`
- Agent commits captured from git log:
  - `866adf45b4 e2e: done`
- Slack DM landed in D0AFTLEJGJU mentioning `ORCH-mcp-e63de9`
- pytest result: **2 passed** (smoke + full roundtrip)

## Not Proved

(none — all pass criteria met)

---

## Evidence Artifacts

- ACP trigger reply: `ACK ORCH-mcp-e63de9` (printed in pytest -s output)
- Agent commit evidence: `866adf45b4 e2e: done` (printed in pytest -s output)
- Slack DM: confirmed via conversations.history poll within 30s
- pytest output: `1 passed in 115.61s`

## Key Difference from testing_llm/

| | testing_llm/ | testing_mcp/ |
|---|---|---|
| Input trigger | Slack Socket Mode (`_slack_post`) | `openclaw agent` ACP gateway |
| Slack Socket Mode required | Yes (input + output) | Output only (DM) |
| Thread reply verified | Yes (`conversations.replies`) | No (no trigger_ts) |
| Determinism | Depends on Slack connection | Direct subprocess |
