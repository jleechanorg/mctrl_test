# jleechanclaw

Tools, scripts, and configuration for **jleechanclaw** — an autonomous orchestrator agent that replaces Jeffrey as the day-to-day operator across all jleechanorg projects.

## What This Is

This repo is the support layer for an OpenClaw agent named **jleechanclaw**. The agent manages fleets of coding agents (Claude Code, Codex, Gemini, Cursor), monitors their work, handles PR lifecycle, and only escalates when human judgment is truly needed.

Inspired by the [Zoe pattern](https://x.com/eRvissun) — a one-person dev team where the orchestrator holds all business context and delegates specialized coding work to a fleet of agents.

### The Two-Tier Principle

Context windows are zero-sum. Fill it with code and there's no room for business context.

**jleechanclaw** (orchestrator) holds business context: project goals, roadmaps, past decisions, what worked, what failed. Coding agents hold code context: files, tests, types. Each agent is loaded with exactly what it needs.

## Architecture

```
                    ┌─────────────────────┐
                    │     jleechanclaw     │
                    │   (orchestrator)     │
                    │  Business context    │
                    │  Task planning       │
                    │  Agent management    │
                    │  PR lifecycle        │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
     ┌────────▼──────┐ ┌──────▼───────┐ ┌──────▼───────┐
     │  Claude Code  │ │    Codex     │ │   Gemini     │
     │  (frontend,   │ │  (backend,   │ │  (design,    │
     │   git ops,    │ │   complex    │ │   UI specs,  │
     │   fast iter)  │ │   reasoning) │ │   creative)  │
     └───────────────┘ └──────────────┘ └──────────────┘
```

## How jleechanclaw Operates

1. **Receives work** — from Jeffrey via Slack, from GitHub notifications, from scanning failing CI
2. **Plans tasks** — breaks work into focused pieces, selects the right agent for each
3. **Spawns agents** — via `ai_orch run` with precise prompts containing full business context
4. **Monitors progress** — CI status, PR reviews, agent health, launchd schedulers
5. **Handles failures** — diagnoses why an agent failed, writes a better prompt, retries (max 3)
6. **Delivers results** — notifies Jeffrey when PRs are ready to merge
7. **Learns** — logs what worked, what didn't, refines future prompts

## Dependencies

### Core

| Dependency | What It Does | Install |
|-----------|--------------|---------|
| [OpenClaw](https://github.com/openclaw/openclaw) | Agent runtime — persistent memory, channels, gateway | `pnpm install` in openclaw repo |
| [jleechanorg-orchestration](https://pypi.org/project/jleechanorg-orchestration/) | Task dispatch, agent spawning, tmux management | `pip install jleechanorg-orchestration` |
| [jleechanorg-automation](https://pypi.org/project/jleechanorg-automation/) | PR monitor, comment-validation, codex-update, fixpr | `pip install jleechanorg-automation` |

### Agent CLIs

| CLI | Use Case |
|-----|----------|
| `claude` | Frontend, git ops, fast iteration |
| `codex` | Backend, complex reasoning, workhorse |
| `gemini` | Design, UI specs, creative generation |
| `cursor-agent` | IDE-integrated tasks |

### Coordination and Monitoring

| Tool | Purpose |
|------|---------|
| [MCP Agent Mail](https://github.com/jleechanorg/mcp_mail) | Cross-agent messaging ("Gmail for coding agents") |
| [Beads](https://github.com/nickarls/beads) | Memory/context management for coding sessions |

### Infrastructure

| Requirement | Version |
|-------------|---------|
| Node.js | 22+ |
| Python | 3.11+ |
| tmux | any |
| git + gh | any |

## What's In This Repo

### `openclaw-config/` — Live OpenClaw configuration

Tracked baseline for `~/.openclaw/`. Changes here should be synced to `~/.openclaw/` for runtime pickup.

| File/Dir | Purpose |
|----------|---------|
| `SOUL.md` | jleechanclaw personality, goals, and decision-making rules |
| `TOOLS.md` | Tool allow/deny list and usage policy |
| `USER.md` | User context (Jeffrey's preferences, communication style) |
| `IDENTITY.md` | Agent identity definition |
| `openclaw.json` | Runtime config (gateway port, auth, memory, compaction) |
| `cron/jobs.json` | Payload catalog for scheduled jobs. Launchd labels under `ai.openclaw.schedule.*` execute these payloads via `~/.openclaw/run-scheduled-job.sh`. |
| `ai.openclaw.gateway.plist` | launchd plist for the gateway service |
| `AUTO_START_GUIDE.md` | How to set up all launchd services from scratch |
| `BACKUP_AND_RESTORE.md` | Backup and restore runbook |
| `SLACK_SETUP_GUIDE.md` | Slack app and token setup |
| `HEARTBEAT.md` | Heartbeat / health-check protocol |
| `security-policy.md` | Tool execution security policy |
| `skills/` | Custom openclaw skills (agent-browser, moltbook) |
| `agents/` | Per-agent config and session state |
| `canvas/`, `completions/`, `extensions/` | OpenClaw runtime dirs |

### `src/` — Python source

| Module | Purpose |
|--------|---------|
| `src/genesis/config.py` | Config generation utilities |
| `src/genesis/cron.py` | Cron job spec generation |
| `src/genesis/memory.py` | Memory entry generation |
| `src/genesis/writer.py` | File writer for generated config |
| `src/orchestration/backup_redaction.py` | Secret redaction for backups |
| `src/orchestration/evidence.py` | Evidence collection for CI/review |
| `src/orchestration/gh_integration.py` | GitHub API integration |
| `src/tests/` | pytest suite for the above |

### `scripts/` — Shell utilities

| Script | Purpose |
|--------|---------|
| `backup-openclaw-full.sh` | Full recursive backup of `~/.openclaw/` with secret redaction |
| `run-openclaw-backup.sh` | Backup runner with locking and failure alerts |
| `dropbox-openclaw-backup.sh` | Dropbox-targeted backup |
| `install-openclaw-backup-jobs.sh` | Install launchd plist for scheduled backups |
| `check-openclaw-cron-guardrail.sh` | CI guardrail: launchd-only scheduling for repo-managed OpenClaw jobs |
| `setup-openclaw-full.sh` | Full first-time OpenClaw setup |
| `install-launchagents.sh` | Install all openclaw launchd plists from `openclaw-config/` |
| `claude_start.sh` | Start Claude Code agent session |
| `push.sh` | Safe push with branch verification |
| `sync_branch.sh` | Sync branch with upstream |
| `resolve_conflicts.sh` | Semi-automated conflict resolution |
| `create_snapshot.sh` | Create workspace snapshot |
| `consolidate-workspace-snapshots.sh` | Merge workspace snapshots |
| `peekaboo-preflight.sh` | Preflight checks for Peekaboo UI automation |
| `run_lint.sh` | Lint the Python source |
| `run_tests_with_coverage.sh` | Run tests with coverage report |
| `codebase_loc.sh` / `loc.sh` | Lines-of-code counters |
| `setup_email.sh` | Email notification setup |
| `setup-github-runner.sh` | Self-hosted GitHub Actions runner setup |

### Root-level scripts

| Script | Purpose |
|--------|---------|
| `health-check.sh` | Gateway and agent health checks |
| `create_worktree.sh` | Create isolated git worktrees for parallel agent work |
| `blank-to-pr.sh` | Scaffold a branch through to PR |
| `bootstrap-openclaw-config.sh` | Bootstrap fresh OpenClaw configuration |
| `enable-auto-backup.sh` | Enable automated backup scheduling |
| `integrate.sh` | Integration tooling |

### `docs/` — Design docs

| File | Purpose |
|------|---------|
| `GENESIS_DESIGN.md` | Original design doc (historical) |
| `openclaw-backup-jobs.md` | Backup job documentation |
| `orchestration-system-justification.md` | Why the Python orchestration layer exists |
| `user_preferences_learnings.md` | Learned user preferences log |

### `roadmap/` — Planning docs

| File | Purpose |
|------|---------|
| `GENESIS_DESIGN.md` | Renamed jleechanclaw design (canonical) |
| `ORCHESTRATION_DESIGN.md` | Orchestration system design |
| `NATURAL_LANGUAGE_DISPATCH.md` | Why config > code for scheduling |
| `DURABLE_BEHAVIOR_HARDENING_PLAN.md` | Plan for making behavior deterministic |
| `ORCHESTRATION_EVIDENCE_STANDARDS.md` | Evidence standards for orchestration claims |
| `OUTCOME_LEDGER_DESIGN.md` | Outcome tracking design |
| `PEEKABOO_ANTIGRAVITY_UI_AUTOMATION.md` | UI automation design |
| `TDD_EXECUTION_ROADMAP.md` | TDD execution plan |
| `BACKUP_REDUNDANCY_DESIGN.md` | Backup redundancy design |

### `discord-eng-bot/`

Standalone OpenClaw agent config for a Discord engineering bot — separate `openclaw.json` and `SOUL.md` for a Discord-channel-native agent persona.

## PR Automation System

Automated PR jobs (comment-validation, fixpr, fix-comment, codex-update) are driven by `jleechanorg-pr-monitor`.

These jobs currently run through the **openclaw gateway's built-in cron scheduler**. Repo-managed schedules in this repository use launchd; PR automation remains an external live configuration under `~/.openclaw/cron/jobs.json`.

| What | Where |
|------|-------|
| Job definitions (live, macOS) | `~/.openclaw/cron/jobs.json` — **not** in `openclaw-config/cron/` (that tracks Slack/backup jobs only) |
| Binary | `/opt/homebrew/bin/jleechanorg-pr-monitor` |
| Package | `pip install jleechanorg-automation` |
| Source library | `~/projects/worldarchitect.ai/automation/` |
| Executor | `ai.openclaw.gateway` launchd service (cron built into gateway process) |
| Logs | `~/Library/Logs/worldarchitect-automation/` |

Active scheduled PR jobs (as of 2026-03-07):

| Job | Schedule | Command |
|-----|----------|---------|
| `pr-monitor` | `0 */2 * * *` | `jleechanorg-pr-monitor --max-prs 10` |
| `comment-validation` | `*/30 * * * *` | `jleechanorg-pr-monitor --comment-validation` |
| `fixpr` | `*/30 * * * *` | `jleechanorg-pr-monitor --fixpr --cli-agent minimax` |
| `fix-comment` | `45 * * * *` | `jleechanorg-pr-monitor --fix-comment --cli-agent minimax` |
| `codex-api` | `30 * * * *` | `jleechanorg-pr-monitor --codex-api --codex-apply-and-push` |

```bash
# Inspect live jobs
cat ~/.openclaw/cron/jobs.json | python3 -m json.tool

# Add/change a PR automation job: edit ~/.openclaw/cron/jobs.json directly
```

## Launchd Scheduled Jobs (repo-managed)

Repo-managed recurring jobs run via launchd labels `ai.openclaw.schedule.*`.
Payload text remains tracked in `openclaw-config/cron/jobs.json` and is executed by `~/.openclaw/run-scheduled-job.sh`.

| Job | Schedule | Purpose |
|-----|----------|---------|
| `Daily Slack Check-in 9AM` | `0 9 * * *` PT | Morning summary to Slack |
| `Daily Slack Check-in 12PM` | `0 12 * * *` PT | Midday summary |
| `Daily Slack Check-in 6PM` | `0 18 * * *` PT | Evening summary |
| `OpenClaw backup` | `20 */4 * * *` | Backup `~/.openclaw/` every 4h |
| `Genesis memory curation` | `0 22 * * 0` PT | Weekly memory curation |

## Quick Start

### Gateway health check

```bash
./health-check.sh

# Or directly
curl -sS http://127.0.0.1:18789/health
```

### Spawn an agent

```bash
pip install jleechanorg-orchestration

ai_orch run --agent-cli claude "Fix flaky integration tests and open PR"
ai_orch run --agent-cli codex "Refactor auth middleware"
```

### Backup

```bash
./scripts/backup-openclaw-full.sh
./scripts/install-openclaw-backup-jobs.sh  # set up scheduled backups
```

### Install launchd services

```bash
./scripts/install-launchagents.sh  # installs all plists from openclaw-config/
./scripts/install-openclaw-scheduled-jobs.sh  # installs and migrates scheduled jobs
```

## Agent Selection Guide

| Task Type | Agent | Why |
|-----------|-------|-----|
| Backend logic, complex bugs, multi-file refactors | Codex | Deep reasoning, low false-positive rate |
| Frontend, git operations, fast iteration | Claude Code | Fast, broad context |
| UI design, specs, creative | Gemini | Design sensibility |
| IDE-integrated tasks | Cursor | Tight IDE integration |

## Projects Managed

| Repo | Description |
|------|-------------|
| [worldarchitect.ai](https://github.com/jleechanorg/worldarchitect.ai) | AI RPG — primary project |
| [codex_fork](https://github.com/jleechanorg/codex_fork) | Fork of Codex open source CLI |
| [beads](https://github.com/jleechanorg/beads) | Memory upgrade for coding agents |
| [ai_universe](https://github.com/jleechanorg/ai_universe) | MCP Backend Server (Firebase + Cerebras) |
| [ai_universe_frontend](https://github.com/jleechanorg/ai_universe_frontend) | Multi-model AI consultation platform |
| [mcp_mail](https://github.com/jleechanorg/mcp_mail) | Agent-to-agent mail coordination |
| [worldai_claw](https://github.com/jleechanorg/worldai_claw) | AI RPG powered by OpenClaw |
| [claude-commands](https://github.com/jleechanorg/claude-commands) | Claude command collection |

## License

Private — personal workspace and tools for jleechan's OpenClaw setup.

E2E recovery check: README updated via automated test.
