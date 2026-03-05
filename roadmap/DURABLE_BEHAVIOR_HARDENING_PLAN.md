# Durable Behavior Hardening Plan

Status: Draft for OpenClaw execution planning
Owner: jleechanclaw orchestration
Last Updated: 2026-03-03

## Goal

Make OpenClaw behavior deterministic across repeated user requests.

This plan intentionally avoids one-off fixes and focuses on systemic controls:
- explicit repo routing
- strict workflow/API contracts
- branch-scope hygiene
- supervised async processing
- fail-closed policy checks

## Bead Program

Epic:
- `ORCH-qli` — Harden OpenClaw + Mission Control PR automation reliability

Child beads:
- `ORCH-qli.1` (P0): Fix PR trigger workflow contract (PR-only + board endpoint + safe JSON payload)
- `ORCH-qli.2` (P1): Prevent branch contamination in automation-created PRs
- `ORCH-qli.3` (P1): Deterministic repo-routing allowlist for cross-repo operations
- `ORCH-qli.4` (P1): Bring Task Poller under launchd supervision with backlog SLO alerts
- `ORCH-qli.5` (P2): Harden PR auto-`@coderabbit` cron to avoid false-ready and spam
- `ORCH-qli.6` (P1): CI guardrails for workflow endpoint/payload safety

Dependency highlights:
- `ORCH-qli.1` blocks `ORCH-qli.3`
- `ORCH-qli.1` and `ORCH-qli.2` block `ORCH-qli.6`

## Execution Sequence

### Phase 1 — Contract correctness first
1. Execute `ORCH-qli.1`
2. Validate with live dry-run in each target repo (`jleechanclaw`, `worldai_claw`, `worldarchitect.ai`)
3. Confirm Mission Control task creation uses board endpoint only

Exit criteria:
- No workflow uses `/api/tasks`
- `issue_comment` workflows are PR-scoped only
- payload generation is safe for quotes/newlines

### Phase 2 — Routing and branch hygiene
1. Execute `ORCH-qli.2`
2. Execute `ORCH-qli.3`
3. Add explicit preflight output in automation logs: resolved repo, branch base, scope diff

Exit criteria:
- no unintended cross-repo fanout
- no mixed-scope PR diffs
- PR creation fails closed on ambiguity

### Phase 3 — Runtime reliability
1. Execute `ORCH-qli.4`
2. Add backlog telemetry and alerts (inbox count + oldest age)

Exit criteria:
- task poller always supervised
- inbox drain SLO measurable and enforced

### Phase 4 — Noise reduction and policy lock-in
1. Execute `ORCH-qli.5`
2. Execute `ORCH-qli.6`

Exit criteria:
- no duplicate/spammy review comments
- CI blocks unsafe workflow patterns before merge

## Required Technical Standards

### A) Repo mutation safety
All `gh` mutations must include `--repo owner/repo`.
No implicit default repo writes.

### B) Mission Control API contract
Use only board-scoped task endpoints:
- `POST /api/v1/boards/{board_id}/tasks`
- `PATCH /api/v1/boards/{board_id}/tasks/{task_id}`

### C) Workflow payload safety
No raw JSON interpolation from untrusted text.
Use `jq -n` (or equivalent safe serializer).

### D) Branch scope isolation
PR branch must start from target repo base branch.
Fail if changed files exceed declared task scope.

### E) Async execution reliability
Long-running work must be queued and supervised.
No silent inbox accumulation.

## Validation Matrix

For each phase, run:
1. Unit tests for changed modules
2. Policy/contract checks (including negative cases)
3. One live smoke in each affected repo/workflow path
4. Evidence capture:
   - command used
   - status code/output
   - resulting PR/task URL

## What “Done” Looks Like

`ORCH-qli` is complete only when:
- no known wrong-repo PR fanout path remains
- no known invalid MC endpoint path remains
- automation fails closed on ambiguous routing/scope
- task poller is supervised and backlog SLOs visible
- CI policy checks prevent regression on these classes

## OpenClaw Operator Prompt (Copy/Paste)

Use this when asking OpenClaw to execute the plan:

"Execute roadmap/DURABLE_BEHAVIOR_HARDENING_PLAN.md using bead sequence ORCH-qli.1 -> ORCH-qli.2/3 -> ORCH-qli.4 -> ORCH-qli.5/6.\
Work phase-by-phase, fail closed on policy violations, and attach evidence (commands, statuses, URLs) for each acceptance criterion before moving to next phase."
