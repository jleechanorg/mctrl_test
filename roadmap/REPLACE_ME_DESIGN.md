# Replace Me: Autonomous Agent Memory & Identity Design

**Goal:** OpenClaw should be able to operate as Jeffrey's autonomous replacement — not just execute tasks on request, but make decisions, maintain context, communicate, and operate proactively with the full depth of Jeffrey's working knowledge.

**Status:** In Progress (implementation in PR-72)
**Date:** 2026-03-08
**Related:** SOUL.md, TOOLS.md, MEMORY.md, MVP_OPENCLAW_AIORCH_MULTI_AGENT.md

---

## Problem Statement

Today OpenClaw has:
- **SOUL.md** — static identity/behavior rules (manually curated)
- **MEMORY.md** — accumulated context (manually updated, drifts)
- **TOOLS.md** — operational reference (manually maintained)
- **RAG** — hybrid vector+FTS search over workspace files

What's missing:
- **Historical depth** — a year of decisions, incidents, and patterns trapped in git/Slack/PR history, not in memory
- **Pattern extraction** — behavioral preferences inferred from history, not manually described
- **Forward capture** — no automatic recording of what happens day-to-day
- **Proactive autonomy** — OpenClaw reacts but doesn't initiate

The memory files are snapshots, not a living system.

---

## Autonomy Levels

The "replace me" goal is a spectrum, not a binary:

| Level | Capability | Status |
|-------|-----------|--------|
| **L0** | Answer questions about Jeffrey's work | Partial (RAG + MEMORY.md) |
| **L1** | Execute tasks Jeffrey would execute, with approval | Mostly working (dispatch_task, mctrl) |
| **L2** | Make decisions Jeffrey would make, report after | Not started |
| **L3** | Initiate actions Jeffrey would initiate proactively | Fragments (PR automation cron) |
| **L4** | Represent Jeffrey in interactions (Slack, PR reviews) | Not started |

Each level requires progressively deeper memory and judgment.

---

## Architecture

### Data Sources

| Source | Contains | Contributes To |
|--------|----------|---------------|
| **Git history** (3 repos, 1 year) | What was built, when, code patterns | Weekly memory files |
| **PR descriptions + reviews** | Quality bar, review patterns, decision rationale | Pattern extraction → SOUL.md |
| **Slack history** | Communication style, escalation patterns, tone | Communication rules → SOUL.md |
| **OpenClaw session logs** | How Jeffrey phrases requests, what frustrates him | Preference learning |
| **Beads (bd)** | Task management, prioritization patterns | Project status memory |
| **Claude Code sessions** | Working patterns, tool usage, debugging approaches | Forward capture |

### Pipeline

```
Data Sources → Extraction Scripts → Memory Files → RAG Index
                                  → SOUL.md updates
                                  → Pattern database

Historical:
  git log (1yr) ──→ seed_memory.py ──→ ~/.openclaw/memory/YYYY-WNN.md
  gh pr list    ──→                 ──→ (included in weekly summaries)

Periodic:
  git log (week) ─→ extract_patterns.py ─→ SOUL.md "Learned Patterns" section
  beads list     ─→                      ─→ MEMORY.md project status

Forward:
  ghost hooks ────→ .ai-sessions/ ────→ git notes + semantic search
  claude-mem  ────→ SQLite ────────→ MCP search tools
```

### Memory File Format

Weekly memory files (`~/.openclaw/memory/YYYY-WNN.md`):

```markdown
## Week 12, 2026 (Mar 17-23)

### worldarchitect.ai
- Merged PR #5886: native PR scheduler migration (off crontab → gateway cron)
- Fixed streaming fallback: JSON narrative guard, mock mode detection
- Decision: archive bulky docs to separate repo to keep main lean

### jleechanclaw
- Built notifier retry handling + outbox transient failure retries
- Hardened launchd args and Slack polling helpers
- Key learning: gateway HUP doesn't re-embed new memory files, need explicit `openclaw memory index`

### worldai_claw
- Replaced deterministic world generators with LLM planning
- Fixed bilateral faction diplomacy + conditional world-state writes

### Patterns observed
- Preferred merge strategy: squash merge
- PR review focus: real tests over mocks, no fake code
- Communication: direct, concise, action-oriented
```

### SOUL.md Structure (Evolved)

```markdown
# SOUL.md

## Core Identity (human-curated, immutable by scripts)
[Existing SOUL.md content — who you are, how you think]

## Learned Patterns (auto-updated weekly by extract_patterns.py)
### Decision-Making
- When CI fails: investigate root cause, don't retry blindly
- When tests are missing: write real E2E tests, never mocks for integration
- When code review: focus on security, real vs fake, unnecessary complexity

### Communication Style
- Slack: direct, no pleasantries, action items first
- PR descriptions: summary bullets, before/after/why format
- Escalation: if blocked >30min, surface to user with options

### Project Priorities (auto-updated)
- worldarchitect.ai: copilot reliability, streaming stability
- jleechanclaw: mctrl supervisor hardening, memory system
- worldai_claw: LLM world generation quality

## Memory Citations — MANDATORY
[...]
```

---

## MVP Scope (Phase 1)

Three components, no new infrastructure:

### 1. `scripts/seed_memory.py` — Historical Backfill

One-time script that processes a year of git history into weekly memory files.

**Input:**
- `git log --since="1 year ago"` across worldarchitect.ai, jleechanclaw, worldai_claw
- `gh pr list --state merged --limit 500` for PR context

**Processing:**
- Group commits by week per repo
- For each week: send commit subjects + PR descriptions to Claude API (haiku for cost)
- Generate structured weekly summary markdown

**Output:**
- `~/.openclaw/memory/YYYY-WNN.md` (≈52 files for a year)
- Add `~/.openclaw/memory/` directory to extraPaths (single entry, not per-file)
- Run `openclaw memory index`

**Estimated cost:** ~52 API calls × haiku pricing ≈ negligible

- **Implementation status:** Added in `scripts/seed_memory.py` for weekly git/PR backfill plus optional SOUL audit metadata write.

### 2. `scripts/extract_patterns.py` — Weekly Pattern Extraction

Cron job that analyzes recent activity and updates SOUL.md's "Learned Patterns" section.

**Input:**
- Last 7 days of git log across repos
- Last 7 days of bead updates
- Last 7 days of PR review comments (via `gh api`)

**Processing:**
- Send aggregated activity to Claude API
- Prompt: "Given this week's activity, what patterns, preferences, or decisions should be recorded?"
- Parse structured output

**Output:**
- Updates "Learned Patterns" section of SOUL.md (preserving Core Identity)
- Updates project status in MEMORY.md

**Schedule:** OpenClaw gateway cron, weekly (Sunday midnight)

- **Implementation status:** Added in `scripts/extract_patterns.py`; wired a weekly cron job in `openclaw-config/cron/jobs.json` for one-pass pattern extraction.

### 3. Forward Capture — Install ghost

```bash
bun install -g github:notkurt/ghost#main
cd ~/projects/worldarchitect.ai && ghost enable
cd ~/project_jleechanclaw/jleechanclaw && ghost enable
cd ~/project_worldaiclaw/worldai_claw && ghost enable
```

Ghost provides:
- Automatic session → markdown recording
- Mistake ledger (prevents repeating errors)
- Decision log (captures reasoning)
- Git note attachment (links sessions to commits)
- Semantic search across past sessions

---

## Future Phases

### Phase 2: Communication & Slack Memory
- Ingest Slack history (via Slack export or API)
- Extract communication patterns: tone, formality, channel-specific behavior
- Add Slack memory files to RAG index
- Enable L4: OpenClaw posts to Slack matching Jeffrey's voice

### Phase 3: Autonomous Decision Framework
- Define decision boundaries in SOUL.md (what to decide vs what to escalate)
- Build confidence scoring: "I'm 90% sure Jeffrey would approve this PR"
- Implement gradual autonomy: start with low-risk decisions (formatting, rebasing), escalate high-risk (architecture, security)
- Track decision accuracy: did Jeffrey agree with autonomous decisions?

### Phase 4: Proactive Behavior Engine
- Beyond cron jobs: event-driven proactive actions
- "PR stalled >24h → follow up", "CI failing on main → investigate", "New dependency vulnerability → assess"
- Requires L2+ autonomy and pattern-informed judgment

### Phase 5: Multi-Persona
- Different contexts (work vs personal projects) require different behaviors
- SOUL.md variants or context-switching rules
- Channel-specific communication adapters

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **Token cost** of summarizing a year of history | Budget | Use haiku for summarization, batch by week, cache results |
| **Memory bloat** — too many files, noisy retrieval | Retrieval quality degrades | Weekly granularity (52 files/year), periodic consolidation |
| **SOUL.md drift** — auto-updates break curated rules | Identity corruption | Separate sections: immutable Core Identity vs updatable Learned Patterns |
| **Summary quality** — LLM misses nuance from commit msgs | Incomplete memory | Include PR descriptions + review comments, not just subjects |
| **Privacy/secrets** in git history | Data leak into memory | Redaction pass before writing memory files |
| **Stale patterns** — learned patterns become outdated | Wrong decisions | Timestamp patterns, decay old ones, weekly refresh |
| **Over-confidence** — acting on incomplete memory | Bad autonomous decisions | Start at L1 (approval required), measure accuracy before upgrading |

---

## Implementation Plan

| Step | What | Deliverable | Effort | Status |
|------|------|------------|--------|--------|
| 1 | Write `seed_memory.py` | Script + 52 weekly memory files | Small | ✅ Implemented |
| 2 | Add `~/.openclaw/memory/` dir to extraPaths | Config change + reindex | Tiny | ✅ Implemented |
| 3 | Write `extract_patterns.py` | Script + gateway cron job | Small | ✅ Implemented |
| 4 | Evolve SOUL.md structure | Add "Learned Patterns" section separator | Tiny | ✅ Implemented (`openclaw-config/SOUL.md`) |
| 5 | Install ghost on 3 repos | Forward session capture | Tiny | ⚪ Added runbook (`scripts/setup-genesis-ghost.sh`) |
| 6 | Validate: ask OpenClaw historical questions | E2E test of memory retrieval | Small | ⚪ Added validation runbook (`scripts/validate-genesis-memory-l0.sh`) |
| 7 | Run for 2 weeks, assess pattern quality | Iteration on extraction prompts | Ongoing |

Steps 1-5 are the MVP. Step 6 requires runbook execution to gather live E2E evidence; steps 1-5 are implemented in code/config.

---

## Success Criteria

**L0 (memory):** OpenClaw can answer "what did Jeffrey work on in week 38 of 2025?" accurately from RAG.

**L1 (execution):** OpenClaw dispatches tasks with correct context from historical memory (e.g., "fix the streaming bug like we did in PR #5849").

**L2 (judgment):** OpenClaw makes a decision Jeffrey would make, and Jeffrey agrees with it >80% of the time when reviewed.

**L3 (proactive):** OpenClaw initiates an action (follow-up, fix, notification) that Jeffrey would have initiated, without being asked.

**L4 (representation):** A collaborator interacting with OpenClaw via Slack cannot distinguish it from Jeffrey for routine interactions.

---

## References

- [ghost](https://github.com/notkurt/ghost) — session capture + git notes + semantic search
- [claude-mem](https://github.com/thedotmack/claude-mem) — persistent memory plugin for Claude Code
- [Letta Context Repositories](https://www.letta.com/blog/context-repositories) — git-backed agent memory architecture
- `roadmap/MVP_OPENCLAW_AIORCH_MULTI_AGENT.md` — existing mctrl dispatch system
- `roadmap/CONVERGENCE_ENGINE_DESIGN.md` — convergence architecture (related autonomy goals)
