# TDD Execution Roadmap for Mission Control Workflows

## Goal
Ship Mission Control + OpenClaw orchestration changes with a strict Red → Green → Refactor loop so each merge-ready PR has proof of behavior, not just design intent.

## Scope
- Task intake and planning transitions
- Execution state machine behavior
- PR readiness checks (CI, unresolved review threads, policy gates)
- Evidence packet generation and validation
- Failure/retry behavior and idempotency

## Non-Goals
- New product requirements outside PR #30 design scope
- Replacing human merge approval

## TDD Tenets
1. **Fail first**: every behavior change starts with a failing test.
2. **Small slices**: one invariant per test cluster.
3. **Deterministic evidence**: tests assert machine-readable outputs, not prose-only logs.
4. **No silent fallback**: warnings/explicit failures over hidden auto-fixes.
5. **Merge gate integrity**: no passing status unless checks and thread state are truly green.

## Phase Plan

### Phase 1 — Baseline Invariants (RED)
Create failing tests for the highest-risk invariants:
- trigger/auth guardrails
- state machine transitions
- unresolved-thread gate logic
- evidence schema minimum fields

Exit criteria:
- New tests fail on current baseline for expected reasons.

### Phase 2 — Minimal Fixes (GREEN)
Implement the smallest code changes to satisfy failing tests.

Exit criteria:
- All new tests pass.
- Existing suite still passes.

### Phase 3 — Hardening (REFACTOR)
Refactor for clarity and reuse without changing behavior:
- centralize repeated guard logic
- normalize event/evidence builders
- reduce brittle branching in lifecycle transitions

Exit criteria:
- No behavior regression (tests unchanged, still green).
- Clearer boundaries between decision, execution, and reporting.

### Phase 4 — End-to-End Confidence
Add/maintain integration tests that run full lifecycle scenarios:
- intake → planning → execution → PR updates → ready/not-ready decisions
- transient failure + retry handling
- stale/duplicate event handling

Exit criteria:
- Scenario tests pass with stable outputs.

## Required Test Layers Per Feature
1. **Unit**: policy, parsing, transition rules
2. **Integration**: lifecycle orchestration across components
3. **Contract**: schema/shape checks for evidence payloads
4. **E2E/Workflow**: realistic task-to-PR lifecycle

## PR Readiness Checklist (TDD)
- [ ] New behavior has failing tests committed before or alongside fix commits
- [ ] Tests prove both success path and expected failure path
- [ ] Evidence output includes state, checks, unresolved-thread result, and timestamps
- [ ] No bypass of human merge gate
- [ ] CI green for required checks

## Metrics
- Red→Green cycle time per change slice
- Flake rate in lifecycle tests
- % of merged PRs with evidence packet artifacts
- Regression count in post-merge workflow checks

## Immediate Backlog (apply to PR #30 follow-ups)
1. [x] Add explicit tests for unresolved-thread GraphQL gate behavior (completed 2026-03-04 in PR #30 Track A)
2. Add evidence schema validation tests for required fields
3. Add idempotency tests for duplicate webhook/polling events
4. Add transition-table tests for invalid state jumps

## Ownership
- Design source: PR #30 Mission Control workflow docs
- Execution owners: Mission Control coding agents (Claude/Codex) under jleechanclaw orchestration
- Approval: human merge decision remains mandatory
