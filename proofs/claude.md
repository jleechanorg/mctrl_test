---
bead_id: ORCH-d0w
cli: claude-code
note: proof file for ao spawn E2E test
---

# Claude-Code CLI Dispatch Proof

This file documents that the claude-code CLI mctrl dispatch path was exercised.

## Evidence

- **Commit SHA**: b838fad7de8fbd5e35e3cfd38c51ea0729fa3515
- **Branch**: feat/mc-3-claude-proof
- **Timestamp (UTC)**: 2026-05-02 22:27:35
- **Command**: `pytest test_hello.py -q`
- **Output**:
  ```text
  ...                                                                      [100%]
  3 passed in 0.01s
  ```

- **CLI**: claude-code
- **Dispatch**: mctrl ao spawn
- **Branch**: feat/mc-3-claude-proof
