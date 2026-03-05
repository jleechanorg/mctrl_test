# jleechanclaw Orchestration Design

> How jleechanclaw talks to you, spawns agents, and manages work through a unified system.

## Goal

Jeffrey talks to **jleechanclaw** (the OpenClaw agent). jleechanclaw orchestrates coding agents (Claude Code, Codex, Gemini, Cursor) and manages their full lifecycle — task planning, agent spawning, monitoring, PR delivery — with a dashboard for visibility.

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

## The Problem

Two orchestration systems with different state models:
- `ai_orch` thinks agents are alive because tmux sessions exist and `/tmp` JSON files say so
- Mission Control thinks agents are alive because gateway WebSocket sessions are connected

Running both creates split-brain state. Gemini's review called this "an architectural death sentence."

## Beads Tracker

All work items tracked via beads (`bd list`). Design doc sections reference bead IDs.

### Epic
| ID | Title | Priority | Status |
|----|-------|----------|--------|
| ORCH-3h2 | jleechanclaw + Mission Control + ai_orch Integration | P1 | open |

### Implementation Phases
| ID | Title | Priority | Depends On |
|----|-------|----------|------------|
| ORCH-x3o | Phase 1: Webhook Bridge | P1 | ORCH-3h2 |
| ORCH-0a9 | Phase 2: Heartbeat Integration | P1 | ORCH-x3o |
| ORCH-hab | Phase 3: Task Assignment from Dashboard | P2 | ORCH-0a9 |
| ORCH-7zk | Phase 4: State Unification | P3 | ORCH-hab |

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

## Design Decision: Phased Integration (Not Rewrite)

Gemini recommends nuking one system. That's the clean answer but ignores reality:
- `ai_orch` works today and has 78 releases of battle-tested agent spawning
- Mission Control provides the UI/dashboard layer we need but can't spawn tmux agents
- A full rewrite would take weeks and break working automation

**Decision: Keep ai_orch as the executor, add Mission Control as the visibility layer, and incrementally unify state.**

## Architecture

```
  ┌──────────────────────────────────────────────────────────┐
  │                      Jeffrey (human)                      │
  │              Talks via Slack / Telegram / CLI              │
  └──────────────────────────┬───────────────────────────────┘
                             │
                             ▼
  ┌──────────────────────────────────────────────────────────┐
  │                     jleechanclaw                          │
  │               (OpenClaw agent identity)                   │
  │                                                           │
  │  Holds: business context, project goals, past decisions   │
  │  Reads: SOUL.md, USER.md, MEMORY.md, extraPaths          │
  │  Decides: what to build, which agent, what context        │
  └──────────┬────────────────────────────┬──────────────────┘
             │                            │
             ▼                            ▼
  ┌─────────────────────┐    ┌──────────────────────────────┐
  │   ai_orch (executor) │    │  Mission Control (dashboard) │
  │                      │    │                              │
  │  Spawns tmux agents  │───▶│  Boards, tasks, approvals   │
  │  Manages worktrees   │    │  Agent status + timeline     │
  │  Runs CLI tools      │    │  Webhook ingestion           │
  │  Monitors output     │    │  SSE real-time updates       │
  └──────────┬───────────┘    └──────────────────────────────┘
             │
    ┌────────┼────────┐
    ▼        ▼        ▼
 Claude    Codex    Gemini
  Code               CLI
```

### Data Flow

1. Jeffrey messages jleechanclaw via Slack/Telegram
2. jleechanclaw plans the work, selects agents
3. jleechanclaw calls `ai_orch run --agent-cli claude "task prompt"`
4. ai_orch spawns tmux session + worktree, starts agent
5. ai_orch POSTs webhook to Mission Control: `{event: "agent_started", agent: "...", task: "..."}`
6. Agent works, creates PR
7. ai_orch detects completion, POSTs webhook: `{event: "task_complete", pr: 123, ci: "passed"}`
8. Mission Control updates board, task moves to "review"
9. jleechanclaw notifies Jeffrey: "PR #123 ready to merge"

## Implementation Phases

### Phase 1: Webhook Bridge (ORCH-x3o)

**Goal**: ai_orch reports events to Mission Control. Dashboard shows what's happening.

Changes to `ai_orch`:
```python
# Add to orchestrate_unified.py — fire-and-forget webhook after agent events
def _notify_mission_control(event: str, payload: dict):
    """POST event to Mission Control webhook. Best-effort, never blocks."""
    webhook_url = os.environ.get("MISSION_CONTROL_WEBHOOK_URL")
    if not webhook_url:
        return
    try:
        import urllib.request, json
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps({"event": event, **payload}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass  # Never block orchestration for dashboard
```

Events to emit:
| Event | When | Payload |
|-------|------|---------|
| `agent_started` | tmux session created | agent_name, cli, task, worktree, branch |
| `agent_failed` | agent exits non-zero or timeout | agent_name, exit_code, last_output |
| `task_complete` | PR created or task done | agent_name, pr_url, ci_status |
| `agent_killed` | manual or auto cleanup | agent_name, reason |

Mission Control setup:
1. Deploy Mission Control locally via Docker Compose
2. Create a board: "jleechanclaw Operations"
3. Create a webhook on that board
4. Set `MISSION_CONTROL_WEBHOOK_URL` in environment

**No changes to Mission Control code.** Webhooks are a built-in feature.

### Phase 2: Heartbeat Integration (ORCH-0a9)

**Goal**: Mission Control knows which agents are alive in real-time.

Add a lightweight heartbeat loop to `ai_orch` that periodically:
1. Lists running tmux sessions (`tmux list-sessions`)
2. POSTs heartbeat for each to Mission Control (`POST /agents/{id}/heartbeat`)
3. Detects dead sessions, POSTs `agent_failed` event

This runs as a background thread in `ai_orch` or as a cron job.

```python
# heartbeat_bridge.py — runs every 60s
def sync_agents_to_mission_control():
    running = SafeAgentMonitor().list_agents()
    for agent_name in running:
        mc_agent_id = lookup_or_create_mc_agent(agent_name)
        post_heartbeat(mc_agent_id)
    # Detect agents that disappeared
    for known in get_known_mc_agents():
        if known not in running:
            post_agent_event("agent_failed", known, reason="session_disappeared")
```

### Phase 3: Task Assignment from Dashboard (ORCH-hab)

**Goal**: Create tasks in Mission Control UI, jleechanclaw picks them up and dispatches.

jleechanclaw polls Mission Control for unassigned tasks:
```
GET /boards/{board_id}/tasks?status=inbox&assigned_agent_id=null
```

For each task:
1. jleechanclaw reads the task description
2. Decides which agent CLI to use (based on task content + heuristics)
3. Calls `ai_orch run --agent-cli <cli> "<task description>"`
4. Updates task in Mission Control: status → in_progress, assigned_agent_id → self

This closes the loop: humans create tasks in the dashboard, jleechanclaw executes them autonomously.

### Phase 4: State Unification (ORCH-7zk)

**Goal**: Single source of truth for agent state.

Migrate `ai_orch` state from `/tmp` JSON files to Mission Control's PostgreSQL:
- Agent registry → `POST /agents` + heartbeat
- Task pool → Mission Control tasks with dependencies
- A2A messages → Mission Control task comments or a new endpoint
- Results → stored as task attachments or comments

This is the "nuke /tmp" step Gemini recommended, but done incrementally after the bridge is proven.

## Key Design Principles

### 1. Never Block Orchestration for Dashboard

Dashboard integration is fire-and-forget. If Mission Control is down, `ai_orch` keeps working. Agents keep spawning. PRs keep shipping. The dashboard is a visibility layer, not a dependency.

### 2. ai_orch Owns Execution, Mission Control Owns Visibility

- ai_orch: spawning, worktrees, tmux, CLI invocation, output capture
- Mission Control: boards, tasks, approvals, activity log, UI

Don't put execution logic in Mission Control. Don't put UI logic in ai_orch.

### 3. jleechanclaw Is the Brain, Not Either System

Neither ai_orch nor Mission Control decides what to build. jleechanclaw (the OpenClaw agent with business context) makes all planning decisions. The systems are its hands.

### 4. Incremental, Not Big-Bang

Each phase is independently useful:
- Phase 1 alone gives you a dashboard showing what agents are doing
- Phase 2 alone gives you real-time agent health
- Phase 3 alone gives you task-driven orchestration
- Phase 4 alone cleans up the architecture

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
