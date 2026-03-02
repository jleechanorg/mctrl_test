# jleechanclaw

Tools, scripts, and configuration for **jleechanclaw** — an autonomous orchestrator agent that replaces Jeffrey as the day-to-day operator across all jleechanorg projects.

## What This Is

This repo is the support layer for an OpenClaw agent named **jleechanclaw**. The agent manages fleets of coding agents (Claude Code, Codex, Gemini, Cursor), monitors their work, handles PR lifecycle, and only escalates when human judgment is truly needed.

Inspired by the [Zoe pattern](https://x.com/eRvissun) — a one-person dev team where the orchestrator holds all business context and delegates specialized coding work to a fleet of agents.

### The Two-Tier Principle

Context windows are zero-sum. Fill it with code and there's no room for business context. Fill it with customer history and there's no room for the codebase.

**jleechanclaw** (orchestrator) holds business context: project goals, roadmaps, past decisions, what worked, what failed. Coding agents hold code context: files, tests, types. Each agent is loaded with exactly what it needs.

## Architecture

```
                    ┌─────────────────────┐
                    │     jleechanclaw     │
                    │   (orchestrator)     │
                    │                      │
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

## Dependencies

### Core

| Dependency | What It Does | Install |
|-----------|--------------|---------|
| [OpenClaw](https://github.com/openclaw/openclaw) | Agent runtime — persistent memory, channels, gateway, cron | `pnpm install` in openclaw repo |
| [jleechanorg-orchestration](https://pypi.org/project/jleechanorg-orchestration/) | Task dispatch, agent spawning, tmux management | `pip install jleechanorg-orchestration` |

### Agent CLIs (managed by orchestration library)

| CLI | Use Case | Docs |
|-----|----------|------|
| `claude` | Claude Code — frontend, git ops, fast iteration | [claude.ai/code](https://claude.ai/code) |
| `codex` | Codex CLI — backend, complex reasoning, workhorse | [github.com/openai/codex](https://github.com/openai/codex) |
| `gemini` | Gemini CLI — design, UI specs, creative generation | [github.com/google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) |
| `cursor-agent` | Cursor Agent — IDE-integrated tasks | [cursor.com](https://cursor.com) |

### Coordination and Monitoring

| Tool | Purpose | Location |
|------|---------|----------|
| [OpenClaw Mission Control](https://github.com/abhi1693/openclaw-mission-control) | Web dashboard for agent ops, approvals, and visibility | `/Users/jleechan/projects_reference/openclaw-mission-control` |
| [MCP Agent Mail](https://github.com/jleechanorg/mcp_mail) | Cross-agent messaging ("Gmail for coding agents") | `/Users/jleechan/projects_other/mcp_mail` |
| [Beads](https://github.com/nickarls/beads) | Memory/context management for coding sessions | `/Users/jleechan/projects_other/beads` |

### Infrastructure

| Requirement | Version |
|-------------|---------|
| Node.js | 22+ |
| Python | 3.11+ |
| tmux | any |
| git + gh | any |

## What's In This Repo

### Scripts

| Script | Purpose |
|--------|---------|
| `scripts/backup-openclaw-full.sh` | Full recursive backup of `~/.openclaw/` with secret redaction |
| `scripts/run-openclaw-backup.sh` | Backup runner with locking and failure alerts |
| `scripts/install-openclaw-backup-jobs.sh` | Install launchd plist for scheduled backups |
| `health-check.sh` | Gateway and agent health checks |
| `create_worktree.sh` | Create isolated git worktrees for parallel agent work |
| `integrate.sh` | Integration tooling |
| `blank-to-pr.sh` | Scaffold a branch through to PR |
| `bootstrap-openclaw-config.sh` | Bootstrap fresh OpenClaw configuration |
| `enable-auto-backup.sh` | Enable automated backup scheduling |

### Configuration

| Path | Purpose |
|------|---------|
| `openclaw-config/` | Baseline OpenClaw configuration templates |
| `.openclaw/` | Sync boundary contract for `openclaw-config/` vs repo-only custom artifacts |
| `.openclaw-backups/` | Timestamped snapshots of `~/.openclaw/` (redacted) |

### Documentation

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Agent instructions (loaded by Claude Code at session start) |
| `AGENTS.md` | Sub-agent definitions and behavior |
| `IDENTITY.md` | jleechanclaw identity definition |
| `GITHUB_REPOS.md` | All jleechanorg repositories with commit counts |
| `PROJECTS_BEADS.md` | Beads memory context |
| `docs/GENESIS_DESIGN.md` | Original design doc (historical — renamed to jleechanclaw) |
| `docs/openclaw-backup-jobs.md` | Backup job documentation |
| `roadmap/` | Project roadmap tracking |

## Quick Start

### 1. Orchestration CLI

```bash
# Install the orchestration library
pip install jleechanorg-orchestration

# Spawn a Claude Code agent for a task
ai_orch run --agent-cli claude "Fix flaky integration tests and open PR"

# Spawn Codex for backend work
ai_orch run --agent-cli codex "Refactor auth middleware"

# Multi-agent with fallback chain
ai_orch run --agent-cli gemini,claude "Investigate failing CI in PR #42"

# Analyze a task and create agents
ai_orch dispatcher create --agent-cli claude "Fix PR review blockers"
```

### 2. Backup

```bash
# One-time backup
./scripts/backup-openclaw-full.sh

# Install scheduled backups (launchd)
./scripts/install-openclaw-backup-jobs.sh
```

### 3. OpenClaw Gateway

```bash
# Check health
./health-check.sh

# API test
curl -sS -X POST "http://127.0.0.1:18789/v1/chat/completions" \
  -H "Authorization: Bearer $OPENCLAW_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"agent":"main","messages":[{"role":"user","content":"Hello"}]}'
```

## Agent Selection Guide

| Task Type | Agent | Why |
|-----------|-------|-----|
| Backend logic, complex bugs, multi-file refactors | Codex | Deep reasoning, thorough, low false-positive rate |
| Frontend, git operations, fast iteration | Claude Code | Faster, fewer permission issues, broad context |
| UI design, dashboard specs, creative | Gemini | Design sensibility — Gemini designs, Claude builds |
| Rapid prototyping, IDE-integrated | Cursor | Tight IDE integration |

## How jleechanclaw Operates

1. **Receives work** — from Jeffrey, from GitHub notifications, from scanning failing CI
2. **Plans tasks** — breaks work into focused pieces, selects the right agent for each
3. **Spawns agents** — via `ai_orch run` with precise prompts containing full business context
4. **Monitors progress** — CI status, PR reviews, agent health
5. **Handles failures** — diagnoses why an agent failed, writes a better prompt, retries (max 3)
6. **Delivers results** — notifies Jeffrey when PRs are ready to merge
7. **Learns** — logs what worked, what didn't, refines future prompts

## Projects Managed

| Repo | Commits | Description |
|------|---------|-------------|
| [worldarchitect.ai](https://github.com/jleechanorg/worldarchitect.ai) | 6,341 | AI RPG — primary project |
| [codex_fork](https://github.com/jleechanorg/codex_fork) | 2,036 | Fork of Codex open source |
| [beads](https://github.com/jleechanorg/beads) | 1,898 | Memory upgrade for coding agents |
| [ai_universe](https://github.com/jleechanorg/ai_universe) | 1,285 | MCP Backend Server (Firebase + Cerebras) |
| [ai_universe_frontend](https://github.com/jleechanorg/ai_universe_frontend) | 321 | Multi-model AI consultation platform |
| [mcp_mail](https://github.com/jleechanorg/mcp_mail) | 222 | Agent-to-agent mail coordination |
| [worldai_claw](https://github.com/jleechanorg/worldai_claw) | — | AI RPG powered by OpenClaw |
| [claude-commands](https://github.com/jleechanorg/claude-commands) | — | Claude command collection |

## Reference Repos

Cloned to `/Users/jleechan/projects_reference/` for study and integration:

- `openclaw/` — OpenClaw source
- `openclaw-mission-control/` — Agent orchestration dashboard

## License

Private — personal workspace and tools for jleechan's OpenClaw setup.
