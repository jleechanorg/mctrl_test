# Genesis: Persistent Orchestration Layer for OpenClaw

## Overview

Genesis is a **configuration and content layer on top of OpenClaw** — not a new system.
After reading the OpenClaw docs and source, most of what Genesis originally proposed
already exists natively. The real work is **filling in existing files** and **tuning config**.

This doc covers: what OpenClaw already provides, what's genuinely new, and the plan.

**Repo**: `/Users/jleechan/project_jleechanclaw/jleechanclaw`
**OpenClaw workspace**: `~/.openclaw/workspace/` (a git checkout of this repo's content)
**OpenClaw config**: `~/.openclaw/openclaw.json`
**OpenClaw source (open source)**: https://github.com/openclaw/openclaw

## What OpenClaw Already Provides (that we just need to use)

### Memory System (docs: https://docs.openclaw.ai/concepts/memory)

OpenClaw uses **plain Markdown files as source of truth**. The sqlite DB at
`~/.openclaw/memory/<agentId>.sqlite` is just an auto-generated index for search.

**Workspace**: `~/.openclaw/workspace/`

| File | Purpose | Current Status |
|------|---------|----------------|
| `SOUL.md` | Agent personality ("Genesis" identity) | Filled — personality, boundaries, decision rules |
| `USER.md` | User preferences, projects, context | Filled — jleechan, projects, workflow heuristics |
| `TOOLS.md` | Local environment (MCP servers, infra) | Filled — MCP servers, commands, infrastructure |
| `MEMORY.md` | Long-term curated knowledge | **DOESN'T EXIST — needs creation** |
| `HEARTBEAT.md` | Periodic self-review tasks | Exists but empty (no tasks configured) |
| `memory/YYYY-MM-DD.md` | Daily notes (auto-loaded at session start) | Stopped Feb 14 — needs revival |

**At session startup**, OpenClaw loads: today's daily log, yesterday's daily log, SOUL.md, USER.md.

**memory_search** and **memory_get** are built-in agent tools for semantic + keyword search.

**Memory flush before compaction** auto-reminds the agent to persist important context
before the session's context window fills up — writes to `memory/YYYY-MM-DD.md` (daily logs),
NOT to MEMORY.md.

### MEMORY.md Writing: Confirmed Behavior

Per official docs (verified via /perp multi-search):

- **No auto-write config exists for MEMORY.md** — it is always agent-driven
- The agent only writes to MEMORY.md when **explicitly asked by the user**
- Memory flush before compaction writes to `memory/YYYY-MM-DD.md` only
- Docs say: "If you want something to stick, **ask the bot to write it** into memory"
- Docs say: "It helps to remind the model to store memories; it will know what to do"

**To automate MEMORY.md curation, we need a cron job** (agentTurn) that periodically
tells the agent to curate daily logs into MEMORY.md. This is the one genuinely new
automation Genesis adds.

### Configuration Options We Should Enable

In `~/.openclaw/openclaw.json` under `agents.defaults`:

```jsonc
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "enabled": true,
        // Index worldarchitect.ai and other project dirs
        "extraPaths": [
          "/Users/jleechan/projects/worldarchitect.ai/.claude/learnings.md",
          "/Users/jleechan/projects/worldarchitect.ai/CLAUDE.md"
        ],
        "query": {
          "hybrid": {
            "enabled": true,
            "vectorWeight": 0.7,
            "textWeight": 0.3,
            "temporalDecay": {
              "enabled": true,     // Prefer recent memories
              "halfLifeDays": 30   // 30-day half-life
            },
            "mmr": {
              "enabled": true,     // Diversity in results
              "lambda": 0.7
            }
          }
        },
        "experimental": {
          "sessionMemory": true    // Index session transcripts too
        }
      },
      "compaction": {
        "memoryFlush": {
          "enabled": true          // Already enabled by default
        }
      }
    }
  }
}
```

### Cron System

Already running 3x daily Slack check-ins + 4-hourly backups via `~/.openclaw/cron/jobs.json`.
Genesis cron jobs use the same native format.

## What's Genuinely New (Genesis adds)

After subtracting everything OpenClaw already does, Genesis adds only:

### 1. MCP Mail Identity

**DONE.** Registered as "Genesis" (agent #1778) on MCP Mail.
This enables cross-agent coordination — subagents can send reports to Genesis.

### 2. MEMORY.md Creation + Seed Content

The one file that doesn't exist yet. Seed with curated knowledge:

```markdown
# MEMORY.md - Long-Term Knowledge

## Architecture Decisions
- worldarchitect.ai: LLM decides, server executes (core principle)
- FastEmbed classifier for intent detection (<50ms)
- Gemini 3 code execution mode REQUIRED
- 10min/600s timeout across all layers

## Patterns That Work
- Use worktrees for parallel agent work
- CI must pass before merge, no exceptions
- memory_search for semantic recall, memory_get for direct reads
- Daily memory files for session context; MEMORY.md for durable facts
- Markdown files are source of truth; sqlite is just the index

## Key Paths
- OpenClaw workspace: ~/.openclaw/workspace/
- OpenClaw config: ~/.openclaw/openclaw.json
- jleechanclaw repo: /Users/jleechan/project_jleechanclaw/jleechanclaw
- worldarchitect.ai: /Users/jleechan/projects/worldarchitect.ai

## Current Goals
- Get first 100 users for worldarchitect.ai (AI RPG)
- Set up Genesis orchestration layer
```

### 3. MEMORY.md Curation Cron Job

The one piece that goes beyond what OpenClaw does automatically.
No config exists to auto-write MEMORY.md — a cron job is the solution.

```json
{
  "id": "genesis-memory-curation",
  "name": "Genesis MEMORY.md curation",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 22 * * 0",
    "tz": "America/Los_Angeles"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "Review daily memory files (memory/*.md) from the last 7 days. Extract important decisions, patterns, project status updates, and lessons learned. Update MEMORY.md with curated durable knowledge. Don't duplicate existing entries. Keep MEMORY.md concise and focused on facts that help future sessions start warm."
  },
  "delivery": {
    "mode": "none",
    "channel": "last"
  }
}
```

Schedule: **Sunday 10PM PST weekly**.

### 4. Active Task Registry (optional)

`~/.openclaw/workspace/tasks.md` — tracking what's in flight across projects.
No native OpenClaw equivalent.

```markdown
# Active Tasks

## worldarchitect.ai
- [ ] Get first 100 users
  - [ ] Launch landing page
  - [ ] Beta invite flow
  - [ ] Polish core game loop

## jleechanclaw (Genesis)
- [x] Register Genesis on MCP Mail
- [x] Fill in USER.md, TOOLS.md, SOUL.md
- [ ] Create MEMORY.md
- [ ] Configure memorySearch.extraPaths in openclaw.json
- [ ] Add MEMORY.md curation cron job
- [ ] Write today's daily log (restart daily notes)
```

## What Was Wrong in V1 of This Design

For honesty/learning:

1. **"Generate MEMORY.md from sqlite"** — Backwards. MEMORY.md is the source; sqlite indexes it.
2. **`genesis/handoff.md`** — Redundant with `memory/YYYY-MM-DD.md` daily logs.
3. **`genesis/projects/*.md`** — Mostly redundant with `memorySearch.extraPaths`.
4. **`scripts/memory-regen.sh`** — Not needed. Write MEMORY.md directly.
5. **`scripts/session-summarize.sh`** — Memory flush before compaction already does this.
6. **"Feed coding decisions into sqlite"** — Wrong direction. Write markdown, sqlite auto-indexes.
7. **USER.md and TOOLS.md "blank"** — They were already filled in; I read the workspace copies wrong.

## Implementation Plan

### Phase 1: Fill In What's Missing (immediate)
- [ ] Create `~/.openclaw/workspace/MEMORY.md` with seed content
- [ ] Write today's `memory/2026-02-25.md` daily log (restart daily notes)

### Phase 2: Tune Config
- [ ] Add `memorySearch.extraPaths` to `openclaw.json` for worldarchitect.ai
- [ ] Enable `temporalDecay` and `mmr` in memory search
- [ ] Enable `experimental.sessionMemory` for session transcript indexing

### Phase 3: Automation
- [ ] Add MEMORY.md curation cron job (weekly Sunday 10PM)
- [ ] Create `tasks.md` in workspace for cross-project tracking
- [ ] Define MCP Mail protocols for subagent reporting

## Comparison with External Orchestrators

| Feature | Genesis (configure OpenClaw) | Mission Control | Command Center |
|---------|------------------------------|-----------------|----------------|
| **Approach** | Fill in existing files + config | Next.js dashboard | Vanilla JS dashboard |
| **New dependencies** | None | Node.js, Next.js | None (200KB) |
| **New running processes** | None | Node server (~150MB) | Static file server |
| **Context persistence** | Native OpenClaw memory | Database-backed | SSE + localStorage |
| **Setup time** | Minutes (write markdown) | Hours (deploy app) | Minutes (serve files) |
| **Best for** | Solo dev, CLI-native | Team with visual needs | Monitoring + cost |

Genesis is the **zero-overhead option** — it doesn't add anything to run. It just uses
what OpenClaw already built, properly.

## Open Questions

1. **SOUL.md customization**: Should we add Genesis-specific identity to SOUL.md, or keep generic + put project context in MEMORY.md?
2. **extraPaths scope**: How many project files to index? Just CLAUDE.md + learnings.md, or broader?
3. **Curation frequency**: Is weekly MEMORY.md curation enough, or should it be daily?
4. **Session memory**: The experimental session transcript indexing — worth enabling?
5. **Heartbeat vs cron**: Should HEARTBEAT.md tasks supplement the cron job?
