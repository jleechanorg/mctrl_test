# Mem0 Migration TDD Implementation Plan

## Scope
Define a test-driven implementation path for migrating OpenClaw memory from built-in indexing to mem0-first behavior without losing retrieval quality or durability.

## Test Strategy
1. Red tests first
- Add failing tests for required mem0 behavior before changing runtime logic.
- Test both happy path and failure path (timeouts, partial write, read mismatch).

2. Green implementation
- Implement minimal code/config changes to pass each failing test set.
- Keep built-in memory fallback enabled until parity gates pass.

3. Refactor
- Remove duplication, tighten contracts, and document invariants.

## Test Matrix
1. Ingestion tests
- Slack history ingest writes expected records to mem0.
- Sensitive values are redacted before write.
- Duplicate Slack `ts` is idempotent (no duplicate memory entries).

2. Retrieval tests
- Fixed regression query set returns expected entities/facts from mem0.
- Retrieval quality is not worse than baseline built-in memory for target queries.

3. Dual-write consistency tests
- During migration window, built-in and mem0 stores receive equivalent durable facts.
- Drift detector catches mismatches and emits actionable report.

4. Operational tests
- Scheduled job run writes, verifies, and indexes successfully.
- Failure branch alerts and returns non-zero exit.
- Rollback switch restores built-in memory as primary read path.

## Implementation Phases (TDD)
1. Phase A: Contract harness
- Add test fixtures + regression query corpus.
- Add mockable adapter boundary for mem0 client.

2. Phase B: Write path
- Implement mem0 write adapter and redaction/idempotency.
- Pass ingestion + dual-write write-side tests.

3. Phase C: Read path
- Implement mem0-first retrieval with built-in fallback flag.
- Pass retrieval parity tests.

4. Phase D: Cutover controls
- Add runtime switch and rollback command/runbook.
- Pass operational and rollback tests.

## Exit Criteria
- Regression query suite green for 7 consecutive scheduled runs.
- No unresolved drift events in dual-write window.
- Runbook validated in dry-run and rollback drill.

## Artifacts
- Roadmap: `roadmap/MEM0_MIGRATION_PLAN.md`
- This TDD plan: `roadmap/MEM0_TDD_IMPLEMENTATION_PLAN.md`
- Bead tracking: `rev-7rr` + child implementation beads.
