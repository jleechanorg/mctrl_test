# tests/ — Unit and Integration Tests

This directory contains unit and integration tests that use mocks, stubs, and monkeypatching.

## How to Run

```bash
cd /Users/jleechan/project_jleechanclaw/mctrl
python -m pytest tests/ -v --tb=short
```

`pythonpath = ["src"]` is set in the root `pyproject.toml` — no manual PYTHONPATH needed.

## What Lives Here vs testing_llm/

| Here (`tests/`) | `testing_llm/` |
|---|---|
| Unit and integration tests | Real black-box verification only |
| Mocks, stubs, monkeypatching allowed | No mocks, no stubs, no injection |
| Fast (milliseconds) | Slow (real agent execution, minutes) |
| Proves isolated logic | Proves the full system works end-to-end |

## Suites

| File | What it proves |
|---|---|
| `test_mvp_loopback_e2e.py` | Registry→outbox→drain flow (mocked delivery); real Slack roundtrip |
| `test_worktree_reuse.py` | find_existing_worktree, resolve_worktree_for_branch, dispatch wiring |
| `test_reconciliation.py` | Reconciler logic: in_progress only, task_finished vs needs_human, CAS guard |
| `test_session_registry.py` | JSONL upsert, CAS update, malformed-line skipping, atomic writes |
| `test_openclaw_notifier.py` | Outbox enqueue, drain atomicity, notify_openclaw fallback |
| `test_supervisor.py` | Supervisor env parsing and startup safeguards |

## Not Proved Here

Real agent execution, real Slack delivery, real tmux sessions, real git operations.
Those are proved in `testing_llm/`.

## OpenClaw Config: Live Files vs This Repo

**The real OpenClaw config lives in `~/.openclaw/` — this repo (`openclaw-config/`) is a backup only.**

| Live (what OpenClaw reads) | Backup (this repo) |
|---|---|
| `~/.openclaw/SOUL.md` | `openclaw-config/SOUL.md` |
| `~/.openclaw/TOOLS.md` | `openclaw-config/TOOLS.md` |
| `~/.openclaw/openclaw.json` | `openclaw-config/openclaw.json` |

**After editing any `openclaw-config/` file, sync to live:**
```bash
cp openclaw-config/SOUL.md ~/.openclaw/SOUL.md
kill -HUP $(pgrep -f openclaw-gateway)  # or restart gateway
```
