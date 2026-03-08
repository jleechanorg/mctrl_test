# Real MCP Gateway Roundtrip Verification — 2026-03-08 (post-copilot fixes)

Branch: fix/mcp-followups  
PR: https://github.com/jleechanorg/jleechanclaw/pull/67  
Date: 2026-03-08  
Commits tested: `1910c6e270` (copilot fixes), `f5c49c2982` (test timeout fix)

---

## Run 1 — testing_mcp/test_mcp_gateway_roundtrip.py (2 tests)

```
testing_mcp/test_mcp_gateway_roundtrip.py::test_gateway_connectivity PASSED
testing_mcp/test_mcp_gateway_roundtrip.py::test_mcp_gateway_dispatch_roundtrip PASSED
2 passed in 167.69s (0:02:47)
```

- `test_gateway_connectivity`: Gateway HTTP endpoint responded, returned well-formed `chat.completion` JSON
- `test_mcp_gateway_dispatch_roundtrip`:
  - bead: `ORCH-mcp-<uuid>` (randomly generated)
  - session: `ai-minimax-dfa2c0`
  - worktree: `/tmp/ai-orch-worktrees/ai-orch-47813`
  - agent commit confirmed (task_finished classification)
  - DM `D0AFTLEJGJU` confirmed within 60s poll window

---

## Run 2 — tests/test_mvp_loopback_e2e.py (Slack trigger path, testing_llm equivalent)

```
tests/test_mvp_loopback_e2e.py::test_slack_loopback_roundtrip PASSED
1 passed in 98.36s (1:38)
```

- Real Slack trigger posted as jleechan to #ai-slack-test
- Real ai_orch dispatch, real tmux session, real git commit
- DM + thread reply both confirmed

---

## Proved

- MCP gateway HTTP path alive: POST /v1/chat/completions returns valid chat.completion
- Full dispatch roundtrip via gateway trigger: ai_orch spawns → commits → reconciler detects → DM lands
- Slack loopback (jleechan trigger → DM + thread): confirmed in 98s

## Not Proved

- Gateway test was first run of test_mcp_gateway_dispatch_roundtrip ever; first run failed on 30s DM poll timeout (DM WAS posted but poll window too tight). Second run with 60s window: PASS.
- No thread reply from gateway path (slack_trigger_ts=None by design)

## Fixes validated

- PATH /usr/sbin:/sbin in startup-check.sh: not directly tested in these E2E runs but confirmed in test_openclaw_configs.py (all 32 tests pass)
- sed metacharacter escaping: installer not re-run in this session (existing install valid)
- AttributeError guard in test_mcp_dispatch_roundtrip.py: fixed, test passes
