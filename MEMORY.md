# MEMORY.md - Conversation Learnings (Last 4 Weeks)

## Scope
Summarizes observed user interaction patterns from conversations involving this repo over the last 4 weeks.

## 2026-02-28 - Workflow & Tooling Preferences
- Prefer direct execution-oriented responses and concrete commands over conceptual discussion.
- Frequently requests explicit validation steps and concrete outputs (`tests pass`, `deployment health`, `screenshots`, command logs).
- Strong preference for `ai_orch`/Codex workflows and clear orchestration commands.
- Requests PR/code-review workflows as a first-class process step (e.g., explicit review of PRs with model-assisted checks).
- Repeatedly requests **verification artifacts** for UI-facing changes (Playwright/browser evidence, screenshots).
- Emphasizes quick follow-ups and short iterations when work is blocked/hangs (timeouts, retries, dead loops).
- Tends to favor practical fixes with minimal scope and compatibility-safe changes.
- Explicitly asks for codex/aiaudit/automation reviews before broader rollout.
- Often wants progress tracking and explicit state tracking (checkpoints, logs, heartbeat notes, scheduler status).
- Prefers concise, direct language and action lists.

## 2026-02-28 - Safety / process constraints seen
- Uses explicit branch/PR references when assigning orchestration tasks.
- Repeatedly asks for dry-run modes when available, and for logs/iteration summaries.
- Requests that tooling attempts be resumable and status-visible (agent counts, heartbeat, loop checks).
- Prioritizes test execution and command evidence whenever changes are proposed.

## 2026-02-27 - Open questions / preferences inferred
- In ambiguity, user prefers we proceed with practical defaults and report blockers quickly.
- User accepts machine-readable evidence and concrete code/action plans over broad narratives.

