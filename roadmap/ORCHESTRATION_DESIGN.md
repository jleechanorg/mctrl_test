# jleechanclaw Orchestration Design

> How jleechanclaw talks to you, spawns agents, and manages work through a unified system.

## Goal

Jeffrey talks to **jleechanclaw** (the OpenClaw agent). jleechanclaw orchestrates coding agents (Claude Code, Codex, Gemini, Cursor) and manages their full lifecycle — task planning, agent spawning, monitoring, PR delivery — with a dashboard for visibility.

## Locked Direction (2026-03-05)

We are keeping `ai_orch` as a long-term execution component.

**Authoritative stack (current):**
1. `openclaw` / jleechanclaw = outer-ralph planning brain (LLM orchestrator)
2. `ai_orch` + `ralph-pair.sh` = deterministic execution building blocks
3. AO patterns = selectively ported into an AO-lite kernel (plugin contracts, restore metadata, lifecycle primitives)

Mission Control is optional for visibility, never an execution lifecycle authority.

## Authoritative Architecture (Current)

``` 
  Jeffrey (human)
         |
         v
  jleechanclaw / OpenClaw (outer-ralph: intent + policy + convergence decisions)
         |
         v
  deterministic tools: ai_orch + gh_integration + evidence + beads + /pair
         |
         v
  Claude Code / Codex / Gemini / Cursor runtimes
```

Single-writer rule:
- Outer ralph is the only lifecycle decision writer.
- Tooling plugins execute deterministic actions and report state.
- Optional dashboards mirror state; they do not mutate canonical lifecycle.

MVP implementation reference: `roadmap/MVP_OPENCLAW_AIORCH_MULTI_AGENT.md`.

## AO Feature-for-Feature Audit (2026-03-05)

Scope for this audit:
- `agent-orchestrator` source (`packages/core`, `packages/cli`, `packages/plugins/scm-github`, `packages/web`)
- `mctrl` source (`src/orchestration/*`)
- `worldarchitect.ai` orchestration source (`orchestration/*`)
- Local `/copilot` implementation (`~/.claude/commands/copilot.md`, `~/.claude/commands/_copilot_modules/commentfetch.py`)

Scoring rubric:
- `better` = stronger implementation than AO for the same capability
- `equal` = same capability coverage and operational quality
- `worse` = missing or materially weaker than AO

### AO Capability Matrix

| AO Capability | mctrl | worldarchitect.ai | Evidence |
|---|---|---|---|
| Plugin slot architecture + registry (runtime/agent/workspace/tracker/scm/notifier/terminal) | worse | worse | AO: `packages/core/src/types.ts`, `packages/core/src/plugin-registry.ts`; no equivalent registry in `mctrl`/`worldarchitect.ai` |
| Typed core contracts for session/runtime/agent/workspace/tracker/scm/notifier/terminal | worse | worse | AO: `packages/core/src/types.ts`; Python stacks are ad-hoc module contracts |
| Orchestrator config model (defaults, notification routing, reactions, per-project overrides) | worse | worse | AO: `packages/core/src/types.ts`; no equivalent central schema in both Python stacks |
| Interactive + auto config generation (`ao init`, repo/default-branch detection) | worse | worse | AO: `packages/cli/src/commands/init.ts` |
| Preflight checks (tmux/gh auth/ports/build) before orchestration actions | worse | worse | AO: `packages/cli/src/lib/preflight.ts`; partial CLI checks in `worldarchitect.ai` are not orchestration-wide |
| Built-in plugin loading + config-aware plugin initialization | worse | worse | AO: `packages/core/src/plugin-registry.ts` |
| Session spawn with tracker validation + tracker branch naming | worse | worse | AO: `packages/core/src/session-manager.ts` |
| Workspace lifecycle API (create/destroy/list/postCreate/restore) | worse | worse | AO: `packages/core/src/types.ts`, `packages/core/src/session-manager.ts` |
| Metadata-backed session archiving + restore from archive | worse | worse | AO: `packages/core/src/session-manager.ts`, `packages/core/src/metadata.ts` |
| Session liveness + activity enrichment during list/get | worse | worse | AO: `packages/core/src/session-manager.ts` |
| Runtime-abstracted session messaging (`send`) | worse | equal | AO: `packages/core/src/session-manager.ts`; worldai has tmux send/resume in `orchestration/runner.py` |
| Cleanup terminated/completed sessions with tracker + PR checks | worse | worse | AO: `packages/core/src/session-manager.ts` |
| Lifecycle manager state machine (15 statuses) | worse | worse | AO: `packages/core/src/types.ts`, `packages/core/src/lifecycle-manager.ts` |
| Transition-driven event model with priorities | worse | worse | AO: `packages/core/src/types.ts`, `packages/core/src/lifecycle-manager.ts` |
| Reaction engine (`send-to-agent`/`notify`/`auto-merge`) | worse | worse | AO: `packages/core/src/lifecycle-manager.ts` |
| Retry/time-based escalation rules in reactions | worse | worse | AO: `packages/core/src/lifecycle-manager.ts` |
| System-level `summary.all_complete` reaction | worse | worse | AO: `packages/core/src/lifecycle-manager.ts` |
| Detect PR by branch | equal | worse | AO: `packages/plugins/scm-github/src/index.ts`; mctrl: `src/orchestration/gh_integration.py` |
| CI checks parsing + fail-closed CI summary | equal | worse | AO: `packages/plugins/scm-github/src/index.ts`; mctrl: `src/orchestration/gh_integration.py` |
| Review decision parsing | equal | worse | AO: `packages/plugins/scm-github/src/index.ts`; mctrl: `src/orchestration/gh_integration.py` |
| Unresolved review-thread detection (GraphQL `reviewThreads.isResolved`) | equal | worse | AO: `packages/plugins/scm-github/src/index.ts`; mctrl: `src/orchestration/gh_integration.py` |
| Automated/bot comment extraction + severity inference | equal | worse | AO: `packages/plugins/scm-github/src/index.ts`; mctrl: `src/orchestration/gh_integration.py` |
| Merge readiness aggregation (CI/review/conflicts/draft/blockers) | equal | worse | AO: `packages/plugins/scm-github/src/index.ts`; mctrl: `src/orchestration/gh_integration.py` |
| PR merge + close operations | equal | worse | AO: `packages/plugins/scm-github/src/index.ts`; mctrl: `src/orchestration/gh_integration.py` |
| CLI command surface (`start/status/spawn/batch/send/session/review-check/dashboard/open`) | worse | worse | AO: `packages/cli/src/index.ts`, `packages/cli/src/commands/*` |
| Web API + dashboard mutation endpoints with validation | worse | worse | AO: `packages/web/src/app/api/*`; no equivalent in these Python repos |
| SSE event stream for near-real-time dashboard state | worse | worse | AO: `packages/web/src/app/api/events/route.ts`; worldai dashboard is terminal polling (`orchestration/dashboard.py`) |
| Priority-based multi-notifier routing | worse | worse | AO: `packages/core/src/types.ts`, notifier plugins |
| Tracker integrations (GitHub + Linear plugins) | worse | worse | AO: plugin set in `packages/core/src/plugin-registry.ts` |
| Terminal integration plugins (`iterm2`, `web`) | worse | worse | AO: plugin set in `packages/core/src/plugin-registry.ts` |
| Integration-test matrix across runtime/agent/workspace/notifier/tracker/scm combos | worse | worse | AO: `packages/integration-tests/src/*` |

### Non-AO Strengths in Current Python Stack

Capabilities where your current code is stronger than AO today (outside AO's native feature envelope):
- `worldarchitect.ai` CLI-chain fallback + runtime preflight before launch attempts (`orchestration/task_dispatcher.py`).
- `worldarchitect.ai` A2A `TaskPool` with atomic file-lock claiming and constraint validation (`orchestration/a2a_integration.py`).
- `mctrl` webhook hardening with trusted-actor gate and optional signature validation (`src/orchestration/webhook_bridge.py`).
- `mctrl` explicit `EvidencePacket` completeness model for auditable stage transitions (`src/orchestration/evidence.py`).
- Local `/copilot` workflow's per-comment accountability/coverage gating (`~/.claude/commands/copilot.md` + `_copilot_modules/commentfetch.py`).

### AO Review Handling vs `/copilot`

For PR comment-remediation depth specifically:
- AO (`ao review-check`) is intentionally thin: detect unresolved threads, send a generic fix prompt into tmux.
- `/copilot` is more advanced on per-comment accountability: severity rules, 100% coverage gates, idempotent carry-forward, explicit response typing, and CI/state rechecks.

Verdict:
- `/copilot` is better as a review-remediation workflow.
- AO is better as a generic reusable control-plane primitive.
- We still keep ORCH-edi open to preserve AO's unresolved-thread semantics inside `/copilot` classification paths.

### What This Means for Stack Direction

1. Keep AO as control plane authority (lifecycle + routing), not because Python stacks are weak, but because AO is the only codebase here that already has the full reusable control-plane envelope.
2. Keep `ai_orch` as execution substrate because worldai is strongest at deterministic tmux/worktree/CLI execution mechanics.
3. Keep `/copilot` patterns for deep review remediation logic and port only missing AO signal semantics where needed.
4. Keep TaskPoller separation on its own track (`ORCH-xnf`) so architecture decisions here are not blocked by in-process coupling drift.

## Current Systems

### System 1: jleechanorg-orchestration (PyPI, v0.1.78)

What it does well:
- Battle-tested task dispatcher and agent spawning via tmux
- CLI (`ai_orch`/`orch`) with `run`, `dispatcher`, `list`, `attach`, `kill`
- Multi-CLI support: claude, codex, gemini, cursor
- Git worktree isolation per agent
- A2A protocol for agent-to-agent messaging

Weaknesses (from Gemini's review):
- File-based state in `/tmp` — ephemeral, race-prone, lost on reboot
- tmux pane scraping for monitoring — brittle with ANSI codes
- No persistent history of what agents did across sessions

### System 2: openclaw-mission-control (dashboard)

What it does well:
- Full web UI: boards, tasks, agents, approvals, activity timeline
- FastAPI backend with proper REST API + SSE streaming
- PostgreSQL for durable state, Redis for job queues
- WebSocket RPC to OpenClaw gateway
- Agent provisioning with heartbeat/lifecycle management
- Webhook ingestion for external events

Weaknesses:
- Heavy stack (Postgres + Redis + Next.js) for a single-user setup
- Designed for gateway-native agents, not tmux-based CLI agents
- No awareness of `ai_orch` agent types or worktree isolation

### System 3: agent-orchestrator (AO control plane patterns)

What it does well:
- Lifecycle state machine and reaction loop patterns
- Plugin architecture for isolating execution adapters
- SCM/readiness primitives we can port and harden

Weaknesses for direct adoption:
- TypeScript monorepo migration cost for existing Python runtime
- Requires adaptation to our OpenClaw-driven planning workflow

## The Problem

Split-brain appears whenever more than one system writes lifecycle state for the same task/session.

Historical example:
- `ai_orch` inferred liveness from tmux and `/tmp` state
- Mission Control inferred liveness from gateway connectivity

Design rule going forward: one authoritative writer per state domain.

## Beads Tracker

All work items tracked via beads (`bd list`). Design doc sections reference bead IDs.

### Epic
| ID | Title | Priority | Status |
|----|-------|----------|--------|
| ORCH-3h2 | jleechanclaw + AO + ai_orch Integration | P1 | open |

### Implementation Phases
| ID | Title | Priority | Depends On |
|----|-------|----------|------------|
| ORCH-x3o | Phase 1: AO Execution Adapter Bridge | P1 | ORCH-3h2 |
| ORCH-0a9 | Phase 2: Heartbeat + Lease Integration | P1 | ORCH-x3o |
| ORCH-hab | Phase 3: Optional Mission Control Mirror | P2 | ORCH-0a9 |
| ORCH-7zk | Phase 4: State Durability Unification | P3 | ORCH-hab |

### Ports from agent-orchestrator
| ID | Title | Priority | Depends On |
|----|-------|----------|------------|
| ORCH-l6o | Port GitHub SCM logic → `gh_integration.py` | P1 | ORCH-3h2 |
| ORCH-y77 | Port lifecycle reaction engine → `lifecycle_reactions.py` | P1 | ORCH-l6o |
| ORCH-azl | Evaluate Claude Code PostToolUse hook pattern | P2 | — |

### Superpowers
| ID | Title | Priority | Depends On |
|----|-------|----------|------------|
| ORCH-2oy | Superpower 1: Auto-Triage GitHub Notifications | P2 | ORCH-3h2 |
| ORCH-04k | Superpower 2: Self-Improving Prompts | P2 | ORCH-3h2 |
| ORCH-6k1 | Superpower 3: Parallel Agent Swarms | P2 | ORCH-3h2 |
| ORCH-vvh | Superpower 4: Cost Dashboard | P3 | ORCH-3h2 |
| ORCH-431 | Superpower 5: Replay Failed Agents | P2 | ORCH-3h2 |
| ORCH-8z2 | Superpower 6: Cross-Repo Coordination | P2 | ORCH-3h2 |
| ORCH-7et | Superpower 7: Approval Gates for Production | P2 | ORCH-3h2 |

## Historical Plan: AO-First (Superseded)

Gemini recommends nuking one system. That's the clean answer but ignores reality:
- `ai_orch` works today and has 78 releases of battle-tested agent spawning
- AO patterns are strong for lifecycle ownership and split-brain prevention
- Mission Control provides the UI/dashboard layer we need but can't spawn tmux agents
- A full rewrite would take weeks and break working automation

This AO-first plan is retained for historical context and pattern extraction only.
It is superseded by the minimal-stack direction above and tracked reconciliation work (`ORCH-a68.1`).

## Historical Architecture (AO-First, Superseded)

``` 
  Jeffrey (human)
         |
         v
  jleechanclaw (OpenClaw brain: intent + policy)
         |
         v
  agent-orchestrator (AO control plane: lifecycle + routing)
      |                                |
      v                                v
  ai_orch (AO plugin: cmux + CLI)   Mission Control (optional read-only UI mirror)
      |
      v
  Claude Code / Codex / Gemini / Cursor runtimes
```

### Data Flow

1. Jeffrey messages jleechanclaw via Slack/Telegram
2. jleechanclaw plans the work, selects agents
3. jleechanclaw submits intent to AO
4. AO dispatches to `ai_orch` plugin (`run --backend cmux --agent-cli <cli>`)
5. ai_orch spawns session/worktree, starts agent, streams execution events back to AO
6. AO owns lifecycle transitions and readiness policy
7. Optional: AO/jleechanclaw mirrors events to Mission Control for visibility
8. jleechanclaw notifies Jeffrey: "PR #123 ready to merge"

## Implementation Phases

### Phase 1: AO Execution Adapter Bridge (ORCH-x3o)

**Goal**: AO dispatches execution through `ai_orch` with explicit event contracts.

Changes to `ai_orch`:
```python
# ai_orch adapter surface consumed by AO
def run_task(task: TaskSpec, emit: Callable[[str, dict], None]) -> RunHandle:
    # spawn session/worktree/CLI
    emit("agent_started", {...})
    # stream progress/events
    emit("task_complete", {...})  # or agent_failed / agent_killed
```

Events emitted to AO:
| Event | When | Payload |
|-------|------|---------|
| `agent_started` | session created | agent_name, cli, task, worktree, branch |
| `agent_failed` | agent exits non-zero or timeout | agent_name, exit_code, last_output |
| `task_complete` | PR created or task done | agent_name, pr_url, ci_status |
| `agent_killed` | manual or auto cleanup | agent_name, reason |

AO consumes these events and owns all lifecycle transitions.

### Phase 2: Heartbeat + Lease Integration (ORCH-0a9)

**Goal**: AO can prove liveness/ownership of every running execution session.

Add a lightweight heartbeat loop to `ai_orch` that periodically:
1. Lists active sessions (`tmux` now, `cmux` in Phase 2 runtime migration)
2. Sends heartbeat to AO for known run handles
3. Marks missing sessions as failed with reason `session_disappeared`

This runs as a background thread in `ai_orch` or as a supervised sidecar.

```python
def sync_sessions_to_ao():
    running = SafeAgentMonitor().list_agents()
    for session in running:
        ao_heartbeat(session)
    reconcile_missing_sessions(running)
```

### Phase 3: Optional Mission Control Mirror (ORCH-hab)

**Goal**: Human visibility and approvals without adding a second lifecycle authority.

Flow:
1. AO/jleechanclaw mirrors lifecycle events to Mission Control (webhook/API)
2. Mission Control displays boards/timelines/approvals
3. Any human action in Mission Control is translated to intent and routed back through AO

Mission Control never directly invokes executors or writes canonical lifecycle state.

### Phase 4: State Durability Unification (ORCH-7zk)

**Goal**: Remove `/tmp` state and keep one durable execution ledger.

Migrate `ai_orch` local ephemeral state into AO-managed persistence:
- Agent/session registry
- Task lifecycle + retry metadata
- Execution results and artifacts
- Lease ownership and handoff history

Mission Control can mirror this data for UI, but AO remains source of truth.

## Key Design Principles

### 1. Never Block Orchestration for Dashboard

Dashboard integration is fire-and-forget. If Mission Control is down, `ai_orch` keeps working. Agents keep spawning. PRs keep shipping. The dashboard is a visibility layer, not a dependency.

### 2. AO Owns Lifecycle, ai_orch Owns Execution

- AO: lifecycle state machine, retry/escalation policy, orchestration routing
- ai_orch: spawning, worktrees, cmux/tmux backend ops, CLI invocation, output capture
- Mission Control (optional): boards, tasks, approvals, activity log, UI mirror

Don't duplicate lifecycle decisions across AO and Mission Control. Don't put execution logic in UI layers.

### 3. jleechanclaw Is the Brain, Not Either System

Neither ai_orch nor Mission Control decides what to build. jleechanclaw (the OpenClaw agent with business context) makes all planning decisions. The systems are its hands.

### 4. Incremental, Not Big-Bang

Each phase is independently useful:
- Phase 1 alone gives deterministic AO -> ai_orch dispatch contracts
- Phase 2 alone gives real-time session health + ownership enforcement
- Phase 3 alone gives human visibility/approval workflows without dual-writer risk
- Phase 4 alone removes `/tmp` fragility with durable lifecycle state

## Autonomous Completion Contract

This system is considered successful only when jleechanclaw can run an autonomous repair loop from idea/design input to merge-ready output with explicit stop conditions.

### Loop Invariant

For every active task, jleechanclaw repeats:
1. plan + dispatch
2. detect PR/CI/review state
3. auto-remediate CI/review failures with updated context
4. re-check readiness gates

The loop continues until either:
- all merge-readiness gates pass, or
- escalation criteria are met and human decision is required.

### Merge-Readiness Gates (Authoritative)

A PR is `ready/mergeable` only when all of the following are true:
1. CI is green (all required GitHub Actions checks pass).
2. Relevant tests pass for the changed scope.
3. PR has no merge conflicts (GitHub mergeable state is mergeable).
4. No serious unresolved review comments remain.
5. CodeRabbit is approved or rate-limited (rate-limited is acceptable, not a blocker).

### Escalation Gates (Stop Autonomy, Request Human Input)

jleechanclaw must stop auto-iteration and request explicit human action when any of the following hold:
1. Retry limit or time-based escalation threshold is exceeded for CI/review remediation.
2. Task is stuck/needs_input/errored and cannot progress deterministically.
3. Required credentials, permissions, or external service access are missing.
4. Product-level ambiguity requires judgment (scope change, conflicting requirements, risky tradeoff).

### System Boundaries

1. OpenClaw/jleechanclaw is the planning and policy brain.
2. ai_orch/cmux is the execution substrate (spawn, isolate, run, collect outputs).
3. Mission Control is optional visibility + approvals (never authoritative for execution lifecycle).
4. Lifecycle state transitions are owned by AO; jleechanclaw is the policy brain above AO.

## Superpowers Brainstorm

Ideas beyond the core integration:

### Superpower 1: Auto-Triage GitHub Notifications (ORCH-2oy)
jleechanclaw scans GitHub notifications across all 20+ repos every morning. Failing CI, open PRs needing review, stale issues — triaged into Mission Control tasks automatically via `gh` CLI. No human scanning required.

### Superpower 2: Self-Improving Prompts (ORCH-04k)
When an agent succeeds (CI passes, PR merged), log the prompt that worked. When it fails, log what went wrong. Over time, jleechanclaw builds a prompt library: "For auth bugs, always include the middleware file paths. For UI tasks, start with Gemini design spec."

### Superpower 3: Parallel Agent Swarms (ORCH-6k1)
For large tasks, jleechanclaw decomposes into subtasks and spawns 3-5 agents simultaneously — each on its own worktree/branch. Mission Control shows the swarm as linked tasks with dependencies. Merge order enforced by task dependency blocking.

### Superpower 4: Cost Dashboard (ORCH-vvh)
Track API spend per agent per task. Mission Control custom fields store token counts. jleechanclaw learns which tasks are expensive (Codex for deep reasoning) vs cheap (Claude for git ops) and optimizes agent selection.

### Superpower 5: "Replay" Failed Agents (ORCH-431)
When an agent fails, Mission Control stores the full context (prompt, output, error). jleechanclaw can "replay" with a better prompt — injecting the failure context so the retry agent knows what went wrong. Not just retry — informed retry. Note: the lifecycle reaction engine (ORCH-y77) implements the automated version of this as a state machine with configurable retry limits.

### Superpower 6: Cross-Repo Coordination (ORCH-8z2)
A feature that spans worldarchitect.ai (backend) + ai_universe (MCP server) + ai_universe_frontend (UI). jleechanclaw creates three linked tasks in Mission Control, spawns three agents, and blocks the frontend task until backend + server are merged. Mission Control's dependency system handles the blocking.

### Superpower 7: Approval Gates for Production (ORCH-7et)
For production deployments or security-sensitive changes, Mission Control's approval workflow requires Jeffrey's explicit sign-off before the agent can proceed. jleechanclaw requests approval, Jeffrey clicks "Approve" in the dashboard, agent continues.

## Reference Repos & Credits

This design was informed by studying these open-source projects:

| Repo | URL | What We Studied |
|------|-----|-----------------|
| **agent-orchestrator** (Composio) | https://github.com/ComposioHQ/agent-orchestrator | GitHub SCM integration, lifecycle state machine, reaction engine, plugin architecture |
| **openclaw-mission-control** | https://github.com/abhi1693/openclaw-mission-control | Dashboard architecture, boards/tasks/approvals, webhook ingestion, SSE streaming |
| **openclaw** | https://github.com/openclaw/openclaw | Agent runtime, memory system, gateway, cron jobs, workspace management |

### What We're Reusing from agent-orchestrator

Composio's agent-orchestrator is a TypeScript monorepo for spawning and managing fleets of parallel AI coding agents. Its plugin-based architecture (8 swappable slots: Runtime, Agent, Workspace, Tracker, SCM, Notifier, Terminal, Lifecycle) is well-designed. We're porting select logic patterns — not adopting the framework.

**Porting to ai_orch (Python):**

#### 1. GitHub SCM Logic → `gh_integration.py` (ORCH-l6o)

The `scm-github` plugin (`packages/plugins/scm-github/src/index.ts`) has ~300 lines of `gh` CLI wrappers that solve the "after the agent creates a PR, what happens?" problem. Functions to port:

| Function | What It Does | gh Command |
|----------|-------------|------------|
| `detect_pr(branch, repo)` | Find PR by branch name (no ID tracking needed) | `gh pr list --head <branch> --json number,url,title,isDraft` |
| `get_ci_checks(pr, repo)` | Parse CI status with fail-closed logic | `gh pr checks <num> --json name,state,link` |
| `get_pending_comments(pr, repo)` | Fetch unresolved review threads, exclude bots | GraphQL via `gh api graphql -f` (injection-safe variable passing) |
| `get_reviews(pr, repo)` | Get review decisions (approved/changes_requested) | `gh pr view <num> --json reviews` |
| `get_merge_readiness(pr, repo)` | Aggregate CI + approvals + conflicts into `blockers[]` | Composition of above |

Key design choices we're preserving:
- **PR detection by branch name** — agents don't need to report PR IDs; we discover them
- **Fail-closed error handling** — CI fetch failure → report as "failing" not "none"
- **GraphQL `-f` flag** — safe variable passing prevents injection from repo names with special chars
- **Bot filtering** — hardcoded list of known bot logins (github-actions, dependabot, codecov)

#### 2. Lifecycle Reaction Engine → `lifecycle_reactions.py` (ORCH-y77)

The lifecycle manager (`packages/core/src/lifecycle-manager.ts`) runs a polling loop every 5-30s that auto-detects state transitions and triggers reactions. State machine:

```
working → pr_open → ci_failed ──(auto-retry)──→ working
                  → review_pending → changes_requested ──(auto-retry)──→ working
                  → approved → mergeable → merged

Terminal states: stuck, needs_input, errored, killed, done
```

Reaction patterns to port:
- `ci_failed` → fetch CI logs, auto-send to agent via tmux: "CI failing. Logs at [link]. Fix and push."
- `changes_requested` → fetch review comments (GraphQL), auto-send to agent
- `approved + ci_passing` → notify human "PR ready to merge" (or auto-merge if configured)
- Escalation: after N retries or duration, stop auto-fixing and alert human

This is effectively "Superpower 5: Replay Failed Agents" implemented as a state machine.

#### 3. PostToolUse Hook Pattern (ORCH-azl, evaluation)

agent-orchestrator's Claude Code plugin installs a bash hook that watches for `gh pr create` / `git checkout -b` and auto-updates session metadata — no tmux pane scraping needed. Worth evaluating as an alternative to ai_orch's current tmux output monitoring for Claude Code agents.

### What We're NOT Reusing

| Component | Why Skip |
|-----------|----------|
| Plugin architecture (8 TypeScript interfaces) | Over-engineered for our setup; we have 2 systems already |
| Flat-file metadata (key=value) | We're moving toward PostgreSQL (Phase 4), opposite direction |
| tmux runtime plugin | ai_orch's tmux management has 78 releases of battle-testing |
| Next.js web dashboard | Mission Control is more feature-rich for our needs |
| workspace-worktree plugin | ai_orch already handles worktree isolation |

### What We're Reusing from openclaw-mission-control

The full dashboard layer — boards, tasks, approvals, activity timeline, webhook ingestion, SSE streaming. Used as-is (Phase 1 webhook bridge), not forked.

### What We're Reusing from openclaw

The agent runtime itself — memory system, gateway, cron jobs, session management, workspace. jleechanclaw runs as an OpenClaw agent. See `roadmap/GENESIS_DESIGN.md` for the Genesis (OpenClaw config layer) design.

## Open Questions

1. **Mission Control deployment**: Run locally via Docker Compose, or deploy to a VPS for always-on access?
2. **Webhook payload schema**: Should we match Mission Control's native webhook format, or define our own?
3. **Agent identity mapping**: How to map tmux session names to Mission Control agent IDs? Naming convention or lookup table?
4. **Authentication**: Use Mission Control's local token auth or add a dedicated service account for ai_orch?
5. **MCP Agent Mail**: Should jleechanclaw use MCP Mail for agent communication instead of Mission Control's task comments?

## Dependencies

| Dependency | Version | Purpose |
|-----------|---------|---------|
| OpenClaw | latest | Agent runtime, gateway, persistent memory |
| agent-orchestrator | latest reference patterns | Lifecycle control-plane design + plugin model |
| jleechanorg-orchestration | 0.1.78+ | Task dispatch, agent spawning, tmux management |
| openclaw-mission-control | latest | Dashboard, boards, tasks, approvals, webhooks |
| Docker + Docker Compose | any | Mission Control deployment |
| PostgreSQL | 15+ | Mission Control state (via Docker) |
| Redis | 7+ | Mission Control job queue (via Docker) |
| Python | 3.11+ | ai_orch runtime |
| Node.js | 22+ | OpenClaw runtime |
| tmux | any | Agent session isolation |

## File Locations

| What | Where |
|------|-------|
| This design doc | `jleechanclaw/roadmap/ORCHESTRATION_DESIGN.md` |
| TDD execution roadmap | `jleechanclaw/roadmap/TDD_EXECUTION_ROADMAP.md` |
| SOUL.md (agent identity) | `~/.openclaw/SOUL.md` |
| ai_orch source | `/Users/jleechan/projects/worldarchitect.ai/orchestration/` |
| Mission Control reference | `/Users/jleechan/projects_reference/openclaw-mission-control/` |
| jleechanclaw repo | `/Users/jleechan/project_jleechanclaw/jleechanclaw/` |
| Original Genesis design | `jleechanclaw/docs/GENESIS_DESIGN.md` (historical) |
| agent-orchestrator reference | `/Users/jleechan/projects_reference/agent-orchestrator/` |
| agent-orchestrator SCM plugin | `agent-orchestrator/packages/plugins/scm-github/src/index.ts` |
| agent-orchestrator lifecycle | `agent-orchestrator/packages/core/src/lifecycle-manager.ts` |
| agent-orchestrator types | `agent-orchestrator/packages/core/src/types.ts` |

---

## Architecture Revision: Dispatch Simplification (2026-03-04)

### Decision: Eliminate the Task Poller

`task_poller.py` is an **architectural smell** — a queue consumer that only exists because MC and `ai_orch` don't talk to each other. It introduces:
- 60s polling latency, split-brain risk, false heartbeats, race conditions

**New direction (two phases):**

| Phase | Dispatch model | Executor | MC role |
|-------|---------------|----------|---------|
| **Phase 1** (now) | jleechanclaw → AO → `ai_orch` plugin | tmux + ai_orch | Optional read-only updates |
| **Phase 2** (cmux) | jleechanclaw → AO → `ai_orch --backend cmux` | ai_orch + cmux terminal backend | Optional read-only updates |

### Locked Architectural Decisions (2026-03-04)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **cmux vs tmux** | **cmux only** — not optional, not a fallback | Once cmux is stable, ai_orch uses it as the sole backend. tmux is removed. |
| **Lifecycle state authority** | **AO only** — single writer for orchestration lifecycle | ai_orch reports execution signals; OpenClaw provides policy/intent; no dual-writer ambiguity. |
| **MC authority** | **Non-authoritative** — visibility/approvals only | MC mirrors state and supports humans; it does not drive execution transitions. |
| **Stuck task policy** | **Human review required** — no auto-fail timeout | Stuck tasks surface to Jeffrey for explicit retry or cancel. System never silently fails tasks. |

### Control Plane Rules (cmux Era)

To avoid split-brain and terminal corruption once multiple systems are connected:

1. **Single writer to cmux**: only `ai_orch` mutates cmux state (`ensure_terminal`, `run_command`, `attach`, `kill`).
2. **Single writer to lifecycle state**: only AO mutates canonical task/session lifecycle.
3. **Intent path is linear**: OpenClaw/jleechanclaw submits intent to AO; AO invokes `ai_orch`; Mission Control never invokes executors directly.
4. **Per-session lease required for mutation**: every mutating action carries a lease owner (`auto:<controller>` or `human:<user>`). Writes without active lease are rejected.
5. **Human takeover is first-class**: when Jeffrey claims a panel/session lease, autonomous writes for that session are paused until explicit handback.
6. **Read paths are multi-reader**: all controllers may read session snapshots, logs, and status simultaneously.
7. **A2A remains inside ai_orch agent mesh**: agent-to-agent messaging stays available regardless of which controller initiated the parent task.

These rules let OpenClaw, AO, and optional Mission Control coordinate on the same execution substrate without dual-writer races.

### Phase 1: Gateway-Direct Dispatch (ORCH-7sy)

```
Jeffrey → jleechanclaw → AO.dispatch(task)
                       ↓
                  AO → ai_orch.run --agent-cli claude "task"
                       ↓
                  AO.update_state(DISPATCHING → IN_PROGRESS → DONE|EXECUTION_FAILED)
                       ↓
                  Optional MC mirror update
```

### Phase 2: cmux as ai_orch Backend (ORCH-zyo)

```
Jeffrey → jleechanclaw → AO.dispatch(task)
                       ↓
                  AO → ai_orch.run --backend cmux --agent-cli claude "task"
                       ↓
                  cmux.ensure_terminal("mc:{branch}")
                  cmux.run_command(handle, "claude --print ...")
                  AO.update_state(status)
                  Optional MC mirror update
```

### Open Gaps (Beads)

| Bead | Gap |
|------|-----|
| ORCH-7sy | Gateway-direct dispatch (eliminates task_poller) |
| ORCH-zyo | cmux as ai_orch backend (Phase 2) — depends on ORCH-7sy |
| ORCH-k9n | Reconciliation loop: surfaces stuck tasks to human review |
| ORCH-qxw | DISPATCHING atomic state (race condition fix) |
| ORCH-8w8 | EXECUTION_FAILED state + error propagation |
| ORCH-5gc | Enforce autonomous completion readiness gates (CI/tests/conflicts/review/CodeRabbit) |
| ORCH-36u | Implement escalation gate policy for autonomous loop |
| ORCH-jvd | Add integration tests for Autonomous Completion Contract |
| ORCH-dkj | cmux single-writer gateway in ai_orch (all mutating commands brokered) |
| ORCH-z1i | Per-session lease model (auto owner vs human owner) for cmux mutations |
| ORCH-9l4 | Human takeover/handoff protocol (pause automation on claimed panel) |
| ORCH-xrf | Branch contamination prevention (ORCH-qli.2) |
| ORCH-jym | Repo-routing allowlist for cross-repo ops (ORCH-qli.3) |
| ORCH-afl | CodeRabbit cron hardening (ORCH-qli.5) |
| ORCH-cvg | Convergence orchestration gateway foundation |
| ORCH-dep | ai_orch plugin hardening under AO control plane (depends on ORCH-cvg) |
| ORCH-cil | Convergence Intelligence Layer (depends on ORCH-cvg) |
| ORCH-7rw | Event-sourced Convergence Twin (depends on ORCH-5gc, ORCH-36u, ORCH-z1i) |
| ORCH-nrl | Nested Ralph Loops (outer + inner) (depends on ORCH-cvg, ORCH-cil) |
| ORCH-rce | Python reaction engine fallback (depends on ORCH-7sy) |
| ORCH-ams | Auto-mode selection + environment config (depends on ORCH-cvg, ORCH-rce) |
| ORCH-xnf | Split TaskPoller into separate service; remove in-process coupling |
| ORCH-edi | Port AO unresolved review-thread semantics into `/copilot` classification |
| ORCH-zpf | Complete AO feature-by-feature parity audit vs `mctrl` + `worldarchitect.ai` |
