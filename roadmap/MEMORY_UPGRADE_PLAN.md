# Memory Upgrade Plan

**Goal:** Augment OpenClaw's memory with Mem0 as a structured, queryable layer alongside
the existing file-based system, then power Zoe-style context injection at agent dispatch time.

**Status:** Planning — 2026-03-09
**Epic:** ORCH-s0v (Replace Me)
**Related:** ORCH-s0v.1 (Mem0), ORCH-s0v.2 (daily cron), ORCH-fc9 / ORCH-fc9.1 (context injection)

---

## Current State (as of 2026-03-09)

| Layer | What it does | Quality |
|-------|-------------|---------|
| `memoryFlush` (built-in) | Appends notes to `MEMORY.md` before compaction | Poor — raw session log, not synthesized |
| `extraPaths` RAG | Static file indexing, hybrid 0.7 vector / 0.3 text | OK — passive retrieval, no extraction |
| `claude-mem` plugin | Per-tool observation capture, session summaries | Good for session recall; requires `MAX_CONCURRENT_AGENTS≥15` |
| `build_memory.py` | Weekly LLM synthesis via haiku → `memory/YYYY-WNN.md` | Good — durable semantic memory |

**Key gap:** No structured extraction/deduplication. Memory grows as append-only files.
No graph relationships. No Zoe-style context injection at dispatch time.

---

## Phase 1 — Daily build_memory.py launchd job (ORCH-s0v.2)

### What

Convert `scripts/build_memory.py` from manual-only to a daily scheduled job with failure alerting.

### Design

**LaunchAgent plist:** `~/Library/LaunchAgents/ai.jleechanclaw.build-memory.plist`
- Schedule: `03:00` America/Los_Angeles daily (low-traffic window)
- Run: `python scripts/build_memory.py --days 1` from jleechanclaw repo root

**Wrapper script:** `scripts/run_build_memory.sh`
```
Run build_memory.py --days 1
Capture exit code + stderr
If exit code != 0:
  - POST Slack DM to U09GH5BR3QU via $SLACK_USER_TOKEN
  - Send email via mailx (if configured)
  - Log full stderr to ~/.openclaw/logs/build-memory-YYYY-MM-DD.log
```

**Alert message format:**
```
⚠️ build_memory.py FAILED — 2026-03-09
Exit code: 1
Error: <first 500 chars of stderr>
Log: ~/.openclaw/logs/build-memory-2026-03-09.log
```

**Success:** Writes `~/.openclaw/memory/YYYY-WNN.md`, updates SOUL.md Learned Patterns,
updates workspace/MEMORY.md Project Status. Runs `openclaw memory index` to re-embed.

### Why daily not weekly

`--days 1` is cheap (1-2 haiku synthesis calls). Keeping memory current daily means
OpenClaw always has recent context without needing a full weekly batch.

---

## Phase 2 — Mem0 as structured memory layer (ORCH-s0v.1)

### What

Augment `memoryFlush` — keep the MEMORY.md append (session notes, human-readable audit trail)
AND add Mem0 writes for durable structured knowledge (decisions, entity relationships, patterns).
Two writes, not a replacement.

Mem0 gives: semantic deduplication, entity relationship graph, +26% recall accuracy.

### Architecture

```
OpenClaw session ends / compaction triggers
  → memoryFlush prompt fires (AUGMENTED):
     1. Append session notes to MEMORY.md (keep existing behavior)
     2. Call Mem0 add() for each durable insight (decisions, patterns, project status)

OpenClaw session starts / agent reasoning
  → memory_search → queries extraPaths RAG (MEMORY.md + weekly files)  [existing]
  → memory_search → queries Mem0 graph+vector store  [new, same tool name]
```

Note: OpenClaw already has `memory_search` and `memory_get` in its `alsoAllow` tool list.
When Mem0 MCP replaces the RAG backend, no openclaw.json change is needed.

### Components

1. **Mem0 MCP server** — runs locally, `pip install mem0ai`, exposes `memory_add`, `memory_search`, `memory_delete` as MCP tools

2. **Updated memoryFlush prompt** in `openclaw.json`:
   ```
   Pre-compaction: call memory_add for each durable insight (decisions, preferences,
   project status, patterns). Use entity names as subjects. Do NOT append to MEMORY.md.
   If nothing to store, reply NO_REPLY.
   ```

3. **extraPaths** — keep as-is initially. MEMORY.md + weekly files stay in RAG.
   Over time, as Mem0 accumulates structured memories, weekly files can be retired
   from extraPaths (Mem0 will have equivalent knowledge in queryable form).

4. **Migration** — one-time import: parse existing `MEMORY.md` + weekly files into Mem0
   via `scripts/migrate_to_mem0.py` (future task).

### Open questions

- Self-hosted Mem0 (local vector store, sqlite) vs Mem0 cloud API?
  → Prefer local for privacy (no tokens/secrets in cloud memory)
- Mem0 MCP server auth — needs API key or local-only binding
- Graph memory for entity relationships (Jeffrey ↔ project ↔ decision) — enabled or skip v1?

---

## Phase 3 — Context injection at dispatch (ORCH-fc9.1)

### What

Update `openclaw-config/skills/dispatch-task/SKILL.md` so OpenClaw reasons about
relevant context before constructing the agent prompt. The Zoe pattern.

### Design (LLM-decides, not scripted)

Current dispatch skill (simplified):
```
1. Create bead
2. Call dispatch_task.py with task text
3. Report session ID
```

Updated dispatch skill:
```
1. Create bead
2. Query memory: memory_search("<task description> <affected repo>")
3. Review results — select what's actually relevant (LLM judges)
4. Construct enriched prompt:
   - Task: <original task>
   - Context: <selected memory items, ≤2KB>
   - Known pitfalls: <any relevant past failures>
   - Current project status: <repo status from memory>
5. Call dispatch_task.py with enriched prompt
6. On success: memory_add the prompt pattern that worked
```

### Why LLM-decides matters

A scripted version would always inject the same files (MEMORY.md + SOUL.md).
OpenClaw's inference can distinguish: "this is a UI task → inject worldarchitect.ai UI
patterns" vs "this is a cron task → inject PR automation patterns". The script can't.

### Measurable improvement (L2 → L3 autonomy)

- L1: executes tasks with approval (current)
- **L2: decides with full context (Phase 3 target)**
- L3: proactively finds work (future — Sentry scans, PR monitoring, meeting notes)

---

## Failure Alerting Design (Phase 1 detail)

```
scripts/run_build_memory.sh
├── runs: python scripts/build_memory.py --days 1
├── on failure:
│   ├── Slack DM: curl to slack.com/api/chat.postMessage
│   │   token: $SLACK_USER_TOKEN (from ~/.profile)
│   │   channel: U09GH5BR3QU (jleechan DM)
│   └── email: echo "..." | mailx -s "build_memory FAILED" jleechan@...
└── always: tee to ~/.openclaw/logs/build-memory-$(date +%F).log
```

Log rotation: keep last 30 days (launchd doesn't do this automatically — add a
`find ~/.openclaw/logs -name 'build-memory-*.log' -mtime +30 -delete` to the wrapper).

---

## Bead Summary

| ID | Title | Status |
|----|-------|--------|
| ORCH-s0v | Replace Me epic | in_progress |
| ORCH-s0v.1 | Mem0 integration | open |
| ORCH-s0v.2 | Daily launchd + failure alerts | open |
| ORCH-fc9 | Zoe context injection (parent) | open |
| ORCH-fc9.1 | Dispatch skill update with Mem0 query | open |

**Closed (done):** ORCH-7ag, ORCH-8av, ORCH-9su, ORCH-sx4, ORCH-245

---

## Sequencing

```
Phase 1 (ORCH-s0v.2) — no dependencies, can start now
    ↓
Phase 2 (ORCH-s0v.1) — requires: Mem0 MCP running locally
    ↓
Phase 3 (ORCH-fc9.1) — requires: Mem0 MCP as memory_search tool in OpenClaw
```

Phase 1 is the quick win — 1 shell script + 1 plist. Do it first.
Phase 2 is the structural upgrade. Phase 3 is what closes the Zoe gap.
