# mctrl Direction: No OSS Mission Control

Status: Proposed clarified direction
Owner: jleechanclaw orchestration
Last Updated: 2026-03-08

## Decision

Do not make the OSS OpenClaw Mission Control project part of the target `mctrl`
architecture.

For this repo, the intended stack is:
- `OpenClaw` / jleechanclaw as the planning and policy layer
- `worldarchitect.ai` / `worldai_claw` as downstream product repos that request automation work
- `mctrl` as the durable orchestration and supervision layer
- `ai_orch` as the execution substrate
- `beads` as the canonical task tracker

If we want visibility later, build it around `mctrl`'s own state and evidence.
Do not depend on a separate Mission Control service for execution, lifecycle
authority, or canonical state.

## Why

OSS Mission Control adds complexity we do not need:
- extra runtime surface: FastAPI, frontend, database, queueing, deployment
- another state model that can drift from `mctrl`
- another place where lifecycle authority can accidentally creep back in
- integration work for tmux/worktree/`ai_orch` semantics that `mctrl` already owns

The main problem we are solving is trustworthy orchestration, not dashboard
breadth.

The current reliability work already points to the right center of gravity:
- `mctrl` knows the bead id, branch, worktree, session, and start SHA
- `mctrl` decides whether a task is actually reviewable
- `mctrl` emits Slack/OpenClaw notifications and preserves evidence

That is already the control plane we need.

## Target Architecture

```text
jleechan
  -> OpenClaw / jleechanclaw
  -> beads
  -> mctrl dispatch + supervisor + notifier
  -> ai_orch sessions/worktrees
  -> GitHub / Slack / MCP mail
```

Rules:
- one lifecycle authority: `mctrl`
- one execution substrate: `ai_orch`
- one task source of truth: `beads`
- no second dashboard/service may write canonical execution state
- GitHub PR lifecycle lanes like `comment-validation`, `fix-comment`, and `fixpr`
  should resolve into direct `mctrl` dispatch, not Mission Control task creation

## What This Means

Keep:
- `src/orchestration/dispatch_task.py`
- `src/orchestration/reconciliation.py`
- `src/orchestration/supervisor.py`
- `src/orchestration/session_registry.py`
- notifier + evidence paths
- direct OpenClaw -> `mctrl` -> `ai_orch` dispatch

De-emphasize or remove from forward plans:
- Mission Control as a required deployment
- Mission Control as lifecycle state authority
- Mission Control as task start authority
- Mission Control-only features that require dual writes or mirrored status logic

Acceptable future UI direction:
- a thin local/read-only `mctrl` status view
- static reports from registry/evidence artifacts
- Slack/GitHub-first operator workflow with no extra control-plane service

## Practical Consequences for the Roadmap

1. Reliability and durability work in `mctrl` stays highest priority.
2. Gateway-direct and direct dispatch paths are preferred over any Mission Control
   polling/start path.
3. New features should attach to `mctrl` state, not invent a parallel task model.
4. If a dashboard is built later, it should read `mctrl` state and remain
   non-authoritative.

## Explicit Non-Goals

These are not goals for this repo's mainline direction:
- running OSS Mission Control as mandatory infrastructure
- syncing canonical task state into a second database for normal operation
- requiring Mission Control for approvals, execution, or completion detection
- rebuilding `mctrl` around Mission Control's native abstractions

## Migration Guidance

When existing docs mention Mission Control:
- interpret them as historical context unless they explicitly say mirror-only
- prefer `mctrl` terminology over Mission Control terminology
- prefer direct dispatch/supervisor flows over dashboard-driven flows

Follow-up cleanup that should happen separately:
- mark older Mission Control-heavy roadmap docs as superseded
- trim or delete startup/runtime paths that imply Mission Control is required
- keep only the pieces that still serve `mctrl` directly

## Recommendation

Treat OSS Mission Control as out of the target architecture unless a future need
appears that `mctrl` cannot satisfy with a much smaller read-only surface.

Default answer today: we do not need OSS Mission Control.
