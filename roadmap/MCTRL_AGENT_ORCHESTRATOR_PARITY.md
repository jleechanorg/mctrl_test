# Mctrl Agent-Orchestrator Parity Design

## Goal

Bring `mctrl` up to near-feature parity with the parts of `agent-orchestrator` that matter operationally:

- detect PR state from GitHub without relying on stored PR ids
- react automatically to CI failures and review comments
- keep retry, escalation, and catch-up state so missed webhooks do not strand work
- route remediation back through the existing `dispatch_task -> ai_orch` path
- give operators status and replay controls for the lifecycle loop

This does **not** mean porting the whole upstream product. We want the orchestration behavior, not the plugin framework, dashboard, or Mission Control split-brain.

## Scope

### In Scope

- richer GitHub SCM inspection in `src/orchestration/gh_integration.py`
- lifecycle state machine and reaction engine in `src/orchestration/lifecycle_reactions.py`
- persistent run ledger for lifecycle decisions, retries, replay, and catch-up
- real-time ingress from GitHub webhooks and periodic catch-up polling
- deterministic dispatch lanes for:
  - `comment-validation`
  - `fix-comment`
  - `fixpr`
- operator-visible status and manual replay
- real end-to-end proof against `jleechanorg/mctrl_test`

### Out of Scope

- agent-orchestrator's TypeScript plugin architecture
- dashboard/UI parity
- Mission Control integration or mirrored authority
- replacing `ai_orch`, `dispatch_task`, `supervisor`, or `reconciliation`
- introducing a second execution engine

## Why This Direction

`mctrl` already has the execution substrate:

- task dispatch through [`src/orchestration/dispatch_task.py`](/Users/jleechan/project_jleechanclaw/mctrl/src/orchestration/dispatch_task.py)
- canonical session tracking in [`src/orchestration/session_registry.py`](/Users/jleechan/project_jleechanclaw/mctrl/src/orchestration/session_registry.py)
- completion classification in [`src/orchestration/reconciliation.py`](/Users/jleechan/project_jleechanclaw/mctrl/src/orchestration/reconciliation.py)
- GitHub routing primitives in [`src/orchestration/pr_lifecycle.py`](/Users/jleechan/project_jleechanclaw/mctrl/src/orchestration/pr_lifecycle.py)
- webhook normalization in [`src/orchestration/webhook_bridge.py`](/Users/jleechan/project_jleechanclaw/mctrl/src/orchestration/webhook_bridge.py)

What is missing is the control loop that sits above those pieces and keeps PR work moving after the first PR is opened.

## Reference Behavior To Port

From `~/projects_reference/agent-orchestrator` and the earlier `jleechanclaw` lifecycle reference:

- PR discovery by branch name instead of explicit PR id storage
- state machine:
  - `working -> pr_open -> ci_failed -> working`
  - `working -> pr_open -> review_pending -> changes_requested -> working`
  - `working -> pr_open -> approved -> mergeable -> merged`
- reaction engine with retry caps and escalation
- catch-up polling so missed webhooks still produce actions
- manual replay when an operator wants to re-run a lifecycle action

## Architectural Decisions

### 1. Single Execution Path

Every automated follow-up runs through the same path:

`GitHub signal -> lifecycle engine -> dispatch_task -> ai_orch -> supervisor/reconciliation`

There is no special-purpose PR fixer process. If `mctrl` can create the first PR, it must also be able to fix CI and review feedback through the same mechanism.

### 2. Canonical State Lives In Mctrl

`mctrl` owns lifecycle state. GitHub is an observed external system, and `ai_orch` is the executor. No other component writes authoritative lifecycle transitions.

### 3. Webhooks Are Best-Effort, Catch-Up Is Mandatory

Webhook delivery is not enough. The lifecycle engine must periodically inspect open PRs and recover missed reactions using the same idempotency keys as real-time events.

### 4. Fail Closed On Missing SCM Facts

If CI status, review state, or mergeability cannot be fetched, the engine must not assume green. It should record the failure, keep the lifecycle item actionable, and retry or escalate.

### 5. Real Tests Only For Lifecycle E2E

Anything under `testing_*` must exercise the real external path:

- real GitHub repo: `jleechanorg/mctrl_test`
- real PR creation
- real CI or review-triggered follow-up dispatch
- real Slack/OpenClaw-visible evidence

## Component Design

### SCM Snapshot Layer

Extend [`src/orchestration/gh_integration.py`](/Users/jleechan/project_jleechanclaw/mctrl/src/orchestration/gh_integration.py) into the full lifecycle snapshot provider.

Required surface:

- `detect_pr(branch, repo)`
- `get_pr_state(pr)`
- `get_ci_checks(pr)`
- `get_review_threads(pr)` or equivalent unresolved-comment view
- `get_reviews(pr)`
- `get_merge_readiness(pr)`
- helper to fetch CI failure details for agent prompts

Design constraints:

- branch-based PR lookup remains canonical
- GraphQL stays variable-driven and injection-safe
- bot reviews/comments are filtered deterministically
- errors are typed enough for retry vs escalation decisions

### Lifecycle Ledger

Add a persistent lifecycle ledger under `src/orchestration/` that records:

- PR identity: repo, branch, PR number, head SHA
- lane: `comment-validation`, `fix-comment`, `fixpr`
- last observed SCM snapshot
- last dispatched reaction
- attempt counters
- timestamps for first/last action
- terminal or escalated outcomes

This ledger is the source for:

- duplicate suppression
- catch-up classification
- replay eligibility
- status output

JSONL is acceptable as the first storage format because it matches the rest of `mctrl`, but the schema must be explicit enough to migrate later.

### Lifecycle Reaction Engine

Implement [`src/orchestration/lifecycle_reactions.py`](/Users/jleechan/project_jleechanclaw/mctrl/src/orchestration/lifecycle_reactions.py) as the state machine + policy layer.

Minimum states:

- `working`
- `pr_open`
- `ci_failed`
- `review_pending`
- `changes_requested`
- `approved`
- `mergeable`
- `merged`
- `needs_input`
- `stuck`
- `errored`

Minimum reactions:

- `ci_failed`
  - collect failing checks/log pointers
  - dispatch `fixpr`
- `changes_requested`
  - collect unresolved human review feedback
  - dispatch `fix-comment`
- `approved_and_green`
  - notify human that PR is merge-ready
- `needs_input` or retry exhaustion
  - alert human instead of looping forever

### Ingress And Catch-Up

Two independent entry points feed the same engine:

- real-time webhook ingress via [`src/orchestration/webhook_bridge.py`](/Users/jleechan/project_jleechanclaw/mctrl/src/orchestration/webhook_bridge.py)
- periodic catch-up poller over open PRs and recently active branches

Catch-up requirements:

- same idempotency keys as webhook-triggered runs
- freshness window to suppress duplicate work
- recovery of failed or missed lifecycle actions
- operator-visible reason when catch-up decides to skip

### Dispatch Contract

Lifecycle reactions must compile into normal `dispatch_task` requests, not ad hoc shell commands.

Each lane must supply:

- bead id
- target repo root
- branch or worktree selection
- GitHub context payload
- explicit task prompt for the agent CLI
- Slack trigger metadata when available

The remediation prompt should carry only actionable context:

- failing checks and URLs for `fixpr`
- unresolved human comments and review summary for `fix-comment`
- no speculative prose about what might be wrong

### Operator Surface

Operators need enough control to trust the loop:

- status view showing PR, lane, current state, attempts, last action
- manual replay by PR/lane
- escalation reason when automation stopped
- direct links to PR/checks/review artifacts

This can start as CLI/status output. It does not require a dashboard.

## Parity Map

| Agent-Orchestrator Capability | Mctrl Equivalent |
|---|---|
| SCM GitHub plugin | `gh_integration.py` expanded to full PR snapshot surface |
| Lifecycle manager | `lifecycle_reactions.py` |
| Lifecycle poller | catch-up worker plus webhook-triggered checks |
| Retry/escalation rules | lifecycle config + ledger counters |
| Session restore/replay | manual replay command using recorded lane context |
| PR-open / CI / review reactions | `dispatch_task` lanes `comment-validation`, `fix-comment`, `fixpr` |

## Phased Implementation

### Phase 1: SCM And Ledger

- finish GitHub snapshot helpers
- define ledger schema and persistence helpers
- wire idempotency and duplicate suppression to the ledger

### Phase 2: Reaction Engine

- implement lifecycle state transitions
- compile SCM snapshots into lifecycle states
- dispatch `fixpr` and `fix-comment`
- add retry and escalation policy

### Phase 3: Catch-Up And Replay

- periodic poller for missed work
- manual replay command
- operator-readable status summaries

### Phase 4: Real E2E Proof

- `testing_mcp` path that opens a real PR in `mctrl_test`
- induce or observe a real follow-up event
- prove auto-fix dispatch after PR creation
- persist PR, Slack, and lifecycle ledger evidence

## Risks

- GitHub API rate limits or partial outages can look like state transitions if not handled carefully
- review-comment aggregation can spam agents if unresolved threads are not deduplicated
- CI auto-fix loops can become noisy without retry caps and escalation
- lane prompts can drift if they are generated ad hoc instead of from a stable contract

## Non-Negotiable Acceptance Criteria

- `mctrl` can create a PR and later auto-dispatch `fixpr` for a real CI failure on that PR
- `mctrl` can detect human review feedback and auto-dispatch `fix-comment`
- a missed webhook is recovered by catch-up without duplicate dispatch
- retry exhaustion escalates to Jeffrey instead of looping forever
- all lifecycle E2E proof uses real GitHub and real Slack/OpenClaw evidence

## Proposed Bead Shape

- epic: agent-orchestrator parity control plane
- task: expand GitHub SCM inspection
- task: add lifecycle ledger
- task: implement lifecycle reaction engine
- task: add catch-up poller and replay
- task: wire reaction lanes through dispatch
- task: prove the full loop with real `mctrl_test` PRs
