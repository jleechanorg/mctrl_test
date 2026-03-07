# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This repo (`jleechanorg/jleechanclaw`) is a **personal backup and workspace** for `~/.openclaw` configuration and custom orchestration tooling. It is NOT a fork of or contribution target for the upstream [openclaw/openclaw](https://github.com/openclaw/openclaw) — that repo won't accept PRs from here.

What this repo contains:
- `openclaw-config/` — personal OpenClaw config files (openclaw.json, SOUL.md, etc.)
- `src/genesis/` — Python config/memory/cron generation layer
- `src/orchestration/` — Python orchestration layer (heartbeat, lifecycle, webhook, GitHub integration)
- `src/tests/` — pytest test suite for the above
- `roadmap/` — design docs (GENESIS_DESIGN.md, ORCHESTRATION_DESIGN.md)
- Various shell scripts for backup, sync, and setup

---

## Config-First Principle

**Before writing Python code, check if the goal can be achieved by editing `openclaw-config/`.**

openclaw has rich built-in capabilities. Use them:

| Want to change | Edit this |
|---|---|
| jleechanclaw behavior / decision-making | `openclaw-config/SOUL.md` |
| Tool allow/deny list | `openclaw-config/TOOLS.md` or `openclaw.json` |
| Memory, history, compaction settings | `openclaw.json` (memorySearch, dmHistoryLimit, compaction) |
| Agent identity / user context | `openclaw-config/USER.md`, `identity/` |
| Cron / scheduled tasks | `openclaw-config/cron/` |
| New Python orchestration logic | `src/orchestration/` — **only if config cannot express it** |

New Python code in `src/` is for capabilities that genuinely don't exist in openclaw's config surface. Everything else is config. See `roadmap/NATURAL_LANGUAGE_DISPATCH.md` for the rationale.

## Durable Behavior Goal (Not Incident-Only)

Primary intent: OpenClaw should behave consistently for repeated user requests, not require one-off fixes per thread/PR.

Execution rules:
1. Treat behavior bugs as system bugs first (config/policy/workflow contract), not isolated incidents.
2. Prefer reusable guardrails in `openclaw-config/` and shared automation templates over ad-hoc local patches.
3. Enforce explicit routing and target resolution for external actions (repo, endpoint, channel) before mutation.
4. Add fail-closed checks (tests/CI/policy validators) so the same class of error cannot silently recur.
5. Validate fixes by replaying the same request style in multiple contexts.

---

## Critical Rules

| Rule | Requirement |
|------|-------------|
| **CI test failures are BLOCKERS** | ALL failing tests must be fixed before merge — no exceptions |
| **No unrelated deletions** | Never delete content from origin/main unrelated to the current task |
| No false checkmarks | Only mark items complete when 100% verified |
| No fake code | Audit existing code before writing new implementations |
| Code centralization | Search for existing utilities before writing new ones |
| PR merges | Never merge without explicit user approval |

## LLM Architecture Principles

### Core Rule: LLM Decides, Server Executes

- **LLM gets full context** — don't strip information "to optimize"
- **LLM makes decisions** — don't pre-compute what the LLM should decide
- **Server executes actions** — tools and state changes happen server-side

### Anti-Patterns (BANNED)

- Keyword-based intent detection to bypass LLM judgment
- Stripping tool definitions based on predicted need
- "Optimizations" that reduce information available to the LLM
- Disabled-by-default env-var feature flags for user-requested functionality
- Creating new env vars without clear justification (env vars for credentials/URLs only)

### Error Handling Philosophy

Warnings only — no silent fixes with fallback generation. Log warnings and let validation surface issues. Never silently fix with default content.

## Project Structure

```
src/
  genesis/          # Config/memory/cron generation (Python)
  orchestration/    # Heartbeat, lifecycle, webhook, GH integration (Python)
  tests/            # pytest suite (colocated *.test.py or tests/)
openclaw-config/    # Personal OpenClaw config files
roadmap/            # Design docs
scripts/            # Shell utilities
```

## Build, Test, and Development Commands

This repo uses **Python + pytest**, not TypeScript/pnpm.

- Run tests: `python -m pytest src/tests/ -v`
- Run tests with coverage: `python -m pytest src/tests/ --tb=short -q`
- Add src to path for imports: `PYTHONPATH=src python -m pytest src/tests/`
- pyproject.toml configures pytest root and test paths

No build step — Python source runs directly. No pnpm, no TypeScript, no Vitest.

## Coding Style

- Language: Python 3.12+
- Type hints on all function signatures
- `from __future__ import annotations` at top of files
- Dataclasses for config/data structures
- `StrEnum` for string enumerations
- Brief comments for tricky/non-obvious logic
- Keep files under ~300 LOC; split when it aids clarity or testability
- No `**kwargs` forwarding — use explicit named parameters

## File Protocols

**Default: NO NEW FILES.** Integrate into existing files first.

Before creating a new file:
1. Search for existing similar functionality
2. Try integrating into an existing module
3. Only create new file if integration is truly impossible

File placement:
- Python source → `src/genesis/` or `src/orchestration/`
- Tests → `src/tests/test_<module>.py`
- Config → `openclaw-config/`
- Scripts → `scripts/` or repo root

## Gateway (Local Machine)

The OpenClaw gateway on this machine runs as a **LaunchAgent**, not a menubar app.

```bash
# Status
openclaw gateway status

# Restart
launchctl stop gui/$UID/ai.openclaw.gateway
launchctl start gui/$UID/ai.openclaw.gateway

# Logs
tail -f /tmp/openclaw/openclaw-$(date +%F).log
# or
tail -f ~/.openclaw/logs/gateway.log

# Verify listening
lsof -i :18789 | grep LISTEN
```

Service file: `~/Library/LaunchAgents/ai.openclaw.gateway.plist`
Port: 18789 (loopback only)

## exe.dev VM ops

- Access: `ssh exe.dev` then `ssh vm-name`
- SSH flaky: use exe.dev web terminal or Shelley; keep tmux session for long ops
- Update: `sudo npm i -g openclaw@latest`
- Config: `openclaw config set ...`; ensure `gateway.mode=local`
- Discord token: store raw token only (no `DISCORD_BOT_TOKEN=` prefix)
- Restart gateway on VM:
  ```bash
  pkill -9 -f openclaw-gateway || true
  nohup openclaw gateway run --bind loopback --port 18789 --force > /tmp/openclaw-gateway.log 2>&1 &
  ```
- Verify: `openclaw channels status --probe`, `ss -ltnp | rg 18789`

## PR & Merge Protocols

- **NEVER make PRs to openclaw/openclaw** — this is a personal backup repo
- **NEVER merge without explicit user approval**
- **ALL CI checks must pass before merge** — `mergeable: "MERGEABLE"` only means no conflicts
- Always check `statusCheckRollup` for failures before declaring PR ready

### PR Description Sections (required)
- Summary (1–4 bullets)
- Changes (what changed, before → after → why)
- Testing (verification approach, evidence if applicable)
- Known Limitations

### CodeRabbit Review Protocol
After pushing fixes that address review comments authored by `coderabbitai`:
1. Post a PR comment: `@coderabbitai all good`
2. This triggers CodeRabbit to re-review and verify the fixes are resolved.

Do NOT ping CodeRabbit on a timer or without a preceding push. Only trigger after a fresh commit lands on the PR branch.

### Commit Guidelines

- Use `git add <specific files>` — never `git add -A` blindly
- Concise, action-oriented messages (e.g., `fix: remove redundant try/except in heartbeat poller`)
- Group related changes; don't bundle unrelated refactors

## Shorthand Commands

- `sync`: commit all dirty changes with a sensible Conventional Commit message, then `git pull --rebase` and `git push`

## Git Notes

- If `git branch -d/-D <branch>` is policy-blocked: `git update-ref -d refs/heads/<branch>`

## Security & Configuration

- Never commit real tokens, phone numbers, or live config values — use obviously fake placeholders
- Web provider creds: `~/.openclaw/credentials/`; rerun `openclaw login` if logged out
- Session logs: `~/.openclaw/agents/<agentId>/sessions/*.jsonl`
- Environment variables: see `~/.profile`

## Beads (Issue Tracking)

- Issue prefix: `ORCH`
- DB backend: Dolt server at `127.0.0.1:3307`
- Init if needed: `bd init -p ORCH --force`
- Commands: `bd list`, `bd create`, `bd show <id>`

## Multi-Agent Safety

- Do **not** create/apply/drop `git stash` entries unless explicitly requested
- Do **not** switch branches unless explicitly requested
- Do **not** create/remove `git worktree` checkouts unless explicitly requested
- When "push" requested: `git pull --rebase` first (never discard other agents' work)
- When "commit" requested: scope to your changes only
- When you see unrecognized files: keep going, focus on your changes only

## Troubleshooting

- Gateway/config issues: `openclaw doctor`
- Gateway not starting: check `~/.openclaw/logs/gateway.err.log`
- Import errors in Python: ensure `PYTHONPATH=src` or run pytest from repo root with pyproject.toml present
