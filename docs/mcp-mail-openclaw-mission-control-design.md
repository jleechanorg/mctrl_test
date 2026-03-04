# OpenClaw Mission Control Autonomous Delivery Pipeline Design

> **Canonical design doc.** Supersedes PR #29 (`design/pr-lifecycle-task-workflow`).
> Operational content from PR #29 (polling protocol, CodeRabbit interaction, CI/review loop,
> GitHub trigger workflow) has been consolidated here.

## Goal (North Star)
Enable Jeffrey to hand off a software task once and reliably receive a high-confidence, review-cleared PR for final human merge judgment, with deterministic orchestration from task intake through CI and review resolution.

## Non-Goals
- Building the full Mission Control UI redesign in this phase.
- Deep terminal substrate/UX design is split to dedicated PR #33: https://github.com/jleechanorg/jleechanclaw/pull/33
- Replacing `ai_orch` execution/runtime internals.
- Replacing GitHub as source of truth for PR/CI/review state.
- Defining provider-specific prompt templates in this doc.
- Auto-merging without explicit Jeffrey approval.

## Tenets
1. One north-star outcome per task: merge-ready PR, not partial progress.
2. Human judgment is mandatory at merge time.
3. Planning is explicit and optionally gated by Jeffrey approval.
4. Execution is TDD-first: failing test, fix, green test.
5. `ai_orch` + tmux remains the execution engine.
6. Mission Control is the operator surface, not the code executor.
7. MCP Mail is the default inter-agent communication bus.
8. Deterministic state transitions over ad-hoc branching.
9. Fail closed on ambiguity (agent routing, approvals, or status uncertainty).
10. Retry with context, not blind reruns.
11. Review feedback is treated as work items until resolved or explicitly waived.
12. Default agent policy is stable; overrides must be explicit.

## Terminology
- OpenClaw: runtime/orchestration environment for jleechanclaw.
- Mission Control: task/approval/status UI and control plane.
- MCP Mail: inter-agent messaging transport.
- `ai_orch`: agent execution backend (spawn, tmux lifecycle, CLI invocation).

## End-to-End Lifecycle

### 1) Task Intake
Inputs:
- Jeffrey-issued task in Mission Control or OpenClaw channel.
- Optional constraints: target repo, deadline, risk level, required reviewers.

System actions:
- Create canonical `task_id` and correlation IDs.
- Validate repo ownership and execution prerequisites.
- Classify scope: docs-only, code-change, risky/production-impact.

Exit criteria:
- Task enters `INTAKE_COMPLETE` with complete metadata.

### 2) Plan and Design Gate
System actions:
- Orchestrator produces a concrete plan:
  - problem statement
  - affected files/systems
  - test plan (unit/integration/e2e as applicable)
  - risk and rollback notes
- Mission Control presents plan for optional approval gate.

Gate behavior:
- If Jeffrey requested or policy requires approval: block execution until explicit `APPROVED`.
- If no gate required: auto-transition to execution.

Exit criteria:
- `PLAN_APPROVED` or `PLAN_AUTO_APPROVED`.

### 3) TDD Execution
System actions:
- Spawn implementation agents via `ai_orch` in isolated worktree/branch.
- Enforce TDD loop:
  - create/identify failing test
  - implement minimal fix/change
  - run targeted tests until green
  - refactor safely while preserving green tests
- Publish progress and blocker events via MCP Mail to Mission Control timeline.

Exit criteria:
- Code and tests are locally green for scoped changes.
- Branch is ready for PR creation.

### 4) PR Creation
System actions:
- Open PR with structured summary:
  - problem
  - approach
  - test evidence
  - known limitations
- Link PR to `task_id`.
- Set status to `PR_OPEN`.

Exit criteria:
- PR exists and required checks are discovered.

### 5) CI and Review Resolution Loop

System actions:
- Monitor GitHub checks and review threads continuously.
- On CI failure:
  - create remediation subtask
  - run fix cycle (TDD where applicable)
  - push updates and re-run checks
- On human/bot review comment:
  - classify (required vs informational)
  - assign to implementation/review agent
  - patch and respond with evidence

#### Polling Protocol

| Check | Command / Query | Pass condition |
|-------|----------------|----------------|
| CI status | `gh pr checks --repo {repo} {pr_number}` | All required checks pass (no `FAILURE` or `PENDING`) |
| Review decision | `gh pr view {pr_number} --json reviewDecision` | `reviewDecision == "APPROVED"` |
| Unresolved threads | GraphQL `pullRequest.reviewThreads(last:100)` filtered to `isResolved == false` | Count == 0 |

**Unresolved thread detection** must use the GraphQL `reviewThreads` query — not the REST `pulls/{n}/comments` endpoint, which returns all comments (including resolved/historical) and cannot distinguish thread resolution state:

```graphql
query($owner: String!, $repo: String!, $pr: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      reviewThreads(last: 100) {
        nodes {
          isResolved
          comments(first: 1) {
            nodes { body author { login } }
          }
        }
      }
    }
  }
}
```

Filter `nodes` where `isResolved == false` to get the true unresolved count.

#### Polling Configuration

| Param | Default | Description |
|-------|---------|-------------|
| `poll_interval_ms` | 300000 (5 min) | Interval between CI/review polls |
| `max_iterations` | 50 | Hard cap on poll iterations before escalation |
| `timeout_hours` | 48 | Hard timeout for entire CI/review loop |
| `backoff_factor` | 2 | Exponential backoff multiplier on transient failures |

Loop exit criteria:
- Required CI checks passing.
- Required review threads resolved (via GraphQL thread resolution, not comment count).
- No unresolved blocking comments.

### 6) CodeRabbit Handling

Policy:
- Treat CodeRabbit feedback as required review input when available.
- If CodeRabbit approves: mark `CODERABBIT_APPROVED`.
- If CodeRabbit is rate-limited/unavailable:
  - mark `CODERABBIT_RATE_LIMITED`
  - continue with human + alternate review evidence
  - enforce fallback reviewer quorum of **1 non-author human approval**
  - require explicit note in PR limitations section.

#### CodeRabbit Interaction Protocol

1. Post `@coderabbitai review` as PR comment to request review.
2. Wait for CodeRabbit response (poll via `gh pr view --json comments`).
3. If response contains approval language: mark `CODERABBIT_APPROVED`.
4. If response indicates issues: treat as review feedback, enter `REVIEW_REMEDIATION`.
5. On rate-limit response: increment `coderabbit_rate_limits` counter.
6. After 3 rate-limit hits: mark `CODERABBIT_RATE_LIMITED`, attach fallback evidence, continue.

Exit criteria:
- `CODERABBIT_APPROVED` or `CODERABBIT_RATE_LIMITED` with fallback evidence attached.

#### CodeRabbit Rate-Limit Quorum Decision

- Default quorum when CodeRabbit is unavailable: **1 non-author human approval** plus green required CI.
- Rationale:
  - Maintains momentum when CodeRabbit is rate-limited.
  - Preserves a second set of human eyes without over-constraining small fixes.
  - Keeps merge authority with Jeffrey at final merge judgment.

### 7) Human Merge Gate
System actions:
- Mission Control presents final readiness packet:
  - CI status
  - resolved comments
  - remaining risks
  - CodeRabbit status
- Jeffrey chooses merge judgment: `MERGE`, `HOLD`, or `REWORK`.

Exit criteria:
- Task is closed only after Jeffrey's explicit final judgment.

## GitHub Comment Trigger Workflow

For ad-hoc PR task creation via `@jleechanclaw` mentions in PR comments.

### Security Requirements

1. **Trusted-actor gate:** Verify `author_association` is `OWNER`, `MEMBER`, or `COLLABORATOR` before any self-hosted runner execution.
2. **PR-only trigger:** Verify `github.event.issue.pull_request` exists to prevent issue comments from creating PR tasks.
3. **Fail-fast API calls:** Use `curl --fail-with-body` (or `curl -f`) so non-2xx responses cause the step to fail instead of silently succeeding.
4. **Safe comment text handling:** Use `jq` for JSON payload construction — never pipe comment bodies through `xargs` or shell interpolation, which mangles whitespace and special characters.

### Reference Workflow

Implemented in-repo at `.github/workflows/agent-pr-fix-trigger.yml`.

```yaml
name: Agent PR Fix Trigger

on:
  issue_comment:
    types: [created]

jobs:
  trigger-agent:
    # Security: trusted-actor gate + PR-only filter
    if: |
      github.event.issue.pull_request &&
      contains(github.event.comment.body, '@jleechanclaw') &&
      contains(fromJSON('["OWNER", "MEMBER", "COLLABORATOR"]'), github.event.comment.author_association)
    runs-on: self-hosted
    steps:
      - name: Create Mission Control task
        env:
          MC_BASE_URL: ${{ vars.MISSION_CONTROL_BASE_URL }}
          MC_TOKEN: ${{ secrets.MISSION_CONTROL_TOKEN }}
          MC_BOARD_ID: ${{ vars.MISSION_CONTROL_BOARD_ID }}
          COMMENT_BODY: ${{ github.event.comment.body }}
          PR_NUMBER: ${{ github.event.issue.number }}
          REPO: ${{ github.repository }}
          COMMENT_URL: ${{ github.event.comment.html_url }}
          ACTOR: ${{ github.actor }}
        run: |
          set -euo pipefail

          # Extract instruction after mention while preserving formatting safely.
          INSTRUCTION="$(jq -rn --arg body "$COMMENT_BODY" '$body | sub("@jleechanclaw"; "") | gsub("^\\s+|\\s+$"; "")')"

          # Build payload via jq (prevents JSON injection and whitespace mangling)
          PAYLOAD=$(jq -n \
            --arg title "PR Fix: $REPO #$PR_NUMBER" \
            --arg description "$INSTRUCTION" \
            --arg board_id "$MC_BOARD_ID" \
            --arg pr_number "$PR_NUMBER" \
            --arg repo "$REPO" \
            --arg comment_url "$COMMENT_URL" \
            --arg actor "$ACTOR" \
            '{
              title: $title,
              description: $description,
              board_id: $board_id,
              metadata: {
                pr_number: ($pr_number | tonumber),
                repo: $repo,
                comment_url: $comment_url,
                actor: $actor
              }
            }')

          # Fail-fast: --fail-with-body ensures non-2xx fails the step
          curl --silent --show-error --fail-with-body -X POST "$MC_BASE_URL/api/tasks" \
            -H "Authorization: Bearer $MC_TOKEN" \
            -H "Content-Type: application/json" \
            -d "$PAYLOAD"

          echo "Task created for PR #$PR_NUMBER"
```

## Default and Override Agent Policy
Source of truth:
- Defaults live in OpenClaw configuration first (`openclaw-config/`), then are consumed by Mission Control.

Default execution policy (from OpenClaw config):
- Primary coder: `claude` CLI.
- Default model profile: `MiniMax`.
- Default review pairing: Claude + secondary reviewer (Codex or policy-configured reviewer).

Override policy:
- Override only when explicitly provided in task input or policy rules.
- Allowed override fields:
  - agent CLI (`codex`, `gemini`, etc.)
  - model profile
  - reviewer set
- All overrides must be logged in task audit metadata with reason.

## Evidence Schema (Decision)

Use a generalized evidence bundle schema derived from `.claude/skills/evidence-standards` and existing worldarchitect.ai evidence patterns.

Required bundle files:
- `run.json` (scenario outcomes and errors)
- `metadata.json` (provenance: git baseline, runtime context, timestamp)
- `evidence.md` (human-readable pass/fail summary aligned with run data)
- `methodology.md` (environment + steps + validation method)
- `README.md` (bundle manifest and attribution)
- `request_responses.jsonl` (raw execution interactions when applicable)

Required integrity and traceability rules:
- Per-file checksum sidecars (`*.sha256`) using local basenames.
- Scenario entries must include identifiers needed for log traceability.
- Claims must map to concrete artifacts (configuration evidence, trigger evidence, log evidence).

## State Model and Status Transitions

### Primary States
`NEW`
`INTAKE_COMPLETE`
`PLAN_PENDING_APPROVAL`
`PLAN_APPROVED`
`PLAN_AUTO_APPROVED`
`EXECUTING_TDD`
`PR_OPEN`
`CI_REMEDIATION`
`REVIEW_REMEDIATION`
`READY_FOR_MERGE_JUDGMENT`
`MERGED`
`HOLD`
`REWORK_REQUIRED`
`FAILED`

### Transition Rules
- `NEW -> INTAKE_COMPLETE` only after required metadata validation.
- `INTAKE_COMPLETE -> PLAN_PENDING_APPROVAL` when policy requires human approval.
- `INTAKE_COMPLETE -> PLAN_AUTO_APPROVED` when no approval gate is required.
- `PLAN_PENDING_APPROVAL -> PLAN_APPROVED` on explicit Jeffrey approval.
- `PLAN_APPROVED | PLAN_AUTO_APPROVED -> EXECUTING_TDD` when agent allocation succeeds.
- `EXECUTING_TDD -> PR_OPEN` when branch is green and PR created.
- `PR_OPEN -> CI_REMEDIATION` on any required check failure.
- `PR_OPEN -> REVIEW_REMEDIATION` on blocking review feedback.
- `CI_REMEDIATION -> PR_OPEN` after fixes pushed and checks re-queued.
- `REVIEW_REMEDIATION -> PR_OPEN` after responses posted and blockers resolved.
- `PR_OPEN -> READY_FOR_MERGE_JUDGMENT` when all gates pass.
- `READY_FOR_MERGE_JUDGMENT -> MERGED | HOLD | REWORK_REQUIRED` only by Jeffrey decision.
- Any state -> `FAILED` when retries exhausted or unrecoverable policy error.

## Failure Handling, Retries, and Escalation
Retry strategy:
- Bounded retries per failure class (default 3):
  - CI transient/tooling failure
  - merge/rebase conflict
  - flaky test diagnosis
  - review feedback remediation
- Exponential backoff for transient infrastructure/API failures.
- Preserve failure context in MCP Mail thread for each retry.

Escalation triggers:
- Retry budget exhausted.
- Conflicting reviewer directives.
- Ambiguous ownership or unsafe change surface.
- Repeated CI flake beyond threshold.

Escalation action:
- Transition to `HOLD` with explicit escalation note and next-action options for Jeffrey.

## MVP Scope vs Future Phases

### MVP (This Design Enables)
- Single-task orchestration through full lifecycle.
- Optional plan approval gate.
- TDD execution policy enforcement at workflow level.
- PR open + CI loop + review comment resolution loop.
- CodeRabbit approve/rate-limit handling.
- Final human merge judgment gate.
- GitHub comment trigger with trusted-actor gate.

### Future Phases
- Parallel subtask graph orchestration with dependency blocking.
- Rich Mission Control UI parity with Claude web-style conversation UX.
- Cost/performance policy optimizer for agent/model routing.
- Replay-based auto-debugging with historical failure fingerprints.
- Multi-repo synchronized release orchestration.
- Poll-to-webhook migration where it is implementable without operator intervention; otherwise polling remains.

## Acceptance Criteria (Definition of Done)
1. A task can move from intake to `READY_FOR_MERGE_JUDGMENT` with deterministic, auditable state transitions.
2. Plan gate supports both explicit human approval and policy-based auto-approval.
3. Execution records evidence of TDD loop (failing -> passing tests) in task timeline.
4. PR is automatically linked to task metadata and status.
5. CI failures trigger remediation loops until pass or retry exhaustion.
6. Blocking review comments are tracked to explicit resolution or documented waiver.
7. CodeRabbit state is captured as either approved or rate-limited with fallback evidence.
8. Final state cannot be `MERGED` without explicit Jeffrey merge judgment.
9. All key actions are traceable via Mission Control timeline and MCP Mail thread IDs.
10. Pipeline behavior is configurable by policy without code changes for routine routing decisions.
11. GitHub trigger workflow enforces trusted-actor gate and PR-only filter before self-hosted runner execution.
12. API calls in automation fail fast on non-2xx responses (no silent success on errors).

## Current Decisions and Limitations

Decisions locked for Batch A:
- Source-of-truth defaults: OpenClaw config where applicable.
- CodeRabbit rate-limit fallback quorum: 1 non-author human approval + green required CI.
- Evidence schema: based on `.claude/skills/evidence-standards`, generalized for Mission Control bundles.
- Trigger architecture: prefer webhooks when implementable without operator intervention; keep polling otherwise.

Current limitations:
- Full webhook replacement for CI/review loop is not yet complete in this phase.
