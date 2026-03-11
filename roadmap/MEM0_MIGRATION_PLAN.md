# Mem0 Migration Plan (Future)

## Objective
Migrate from current OpenClaw built-in memory indexing to a mem0-first architecture for durable, cross-session, cross-surface memory retrieval and writes.

## Current State
- Active system: OpenClaw built-in memory (`memorySearch` + SQLite + vector/FTS hybrid).
- Slack history persistence is being handled via local ingestion into `~/.openclaw/memory/*`.
- Reliability concern: background refresh timing is not deterministic for critical workflows.

## Target State
- mem0 as primary long-term memory backend.
- OpenClaw uses mem0 tools for add/search/update/delete memory operations.
- Slack/message history ingestion writes directly to mem0 (or to canonical files + mem0 sync with strict verification).

## Track 1 (Now): Simple mem0 Setup + Extensive Validation
Goal: use the standard mem0 setup path quickly, but require strong proof that memory retrieval actually works before broader migration work.

1. Setup
- Install/enable mem0 integration with default plugin flow.
- Configure embedding provider and credentials for mem0.
- Keep built-in memory enabled as fallback during validation.

2. Ingest
- Ingest Slack history memory exports and recent session history into mem0.
- Use stable IDs for idempotency (`channel_id + ts`, `session_id + turn_id`).
- Emit source-level ingestion counts.

3. Required Test Pack
- Run 30-50 known-answer queries spanning `slack`, `session`, and mixed facts.
- Use fixed corpus: `roadmap/MEM0_50Q_QUESTIONS.md` (50 questions + expected answers).
- Verify expected fact appears in top-k results for each query.
- Add 10 negative/safety queries (facts that should not be retrieved).
- Re-run full pack twice and diff results for stability.
- Record p50/p95 retrieval latency.
- Simulate provider interruption and verify explicit failure/fallback behavior.

3a. Runtime Preflight (Required before any 50Q run)
- Verify `openclaw mem0 stats` succeeds (fails fast on native-module ABI drift).
- Verify no session lock contention on the main session file; abort run if lock timeout errors appear.
- Verify at least one provider path is healthy (no `No available auth profile` or immediate timeout loop).
- Run one smoke query through `openclaw agent` and require a parsable token answer before full batch.
- Persist preflight diagnostics with timestamps in the same `/tmp/openclaw-mem0-fastpath/<timestamp>/` bundle.

4. Pass Criteria
- >=90% correct on known-answer queries.
- 0 critical misses on high-priority personal-context questions.
- Ingested counts match source manifests within tolerance.
- No silent failure path (non-zero exit + written failure report).

5. Evidence Artifacts
- Save each run under `/tmp/openclaw-mem0-fastpath/<timestamp>/`:
- `ingest-summary.json`
- `query-results.json`
- `parity-report.json`
- `latency-report.json`
- `failures.json` (empty when green)

6. Operating Mode After Pass
- Run Track 1 in production mode.
- Schedule validation every 4 hours.
- Keep deep migration/cutover gates as follow-on work only if needed.

## Known Blockers (Observed March 11, 2026)
- `openclaw-mem0` can fail hard when `better-sqlite3` ABI is out of sync with runtime Node (`NODE_MODULE_VERSION` mismatch).
- Agent evaluation can return false failures because of session lock contention on `~/.openclaw/agents/main/sessions/*.jsonl.lock`.
- Provider cooldown/rate-limit paths can mask memory quality with `NO_ID` outcomes unless preflight checks gate the run.
- Tracking issue: `rev-x7f`.

## Migration Phases
1. Discovery and design
- Confirm mem0 deployment mode (local process vs hosted).
- Define schema/taxonomy for entities, episodes, and metadata.
- Define source-of-truth policy (mem0-only vs mem0+markdown mirror).

2. Parallel write
- Keep current built-in memory active.
- Add mem0 write path for new memory events (dual-write).
- Add reconciliation job for drift detection.

3. Read switch
- Route memory search to mem0 first.
- Keep built-in memory as fallback during burn-in.
- Add quality checks: retrieval precision/coverage against baseline queries.

4. Cutover
- Disable built-in memory as primary retrieval source.
- Keep periodic export backups to local files.
- Document rollback path and one-command recovery.

## Guardrails
- Redact secrets/PII before memory write.
- Deterministic verification after each sync run.
- Alert on failed write/retrieval checks.
- No silent fallback behavior.

## Acceptance Criteria
- mem0 returns expected results for a fixed regression query set.
- Scheduled Slack/message ingestion succeeds for 7 consecutive days.
- No data loss during dual-write and cutover windows.
- Runbook exists for rollback and disaster recovery.

## Open Questions
- Exact mem0 deployment location and credentials model.
- Cost/latency tradeoffs for embedding model selection.
- Whether to keep markdown mirror as human-auditable backup.
