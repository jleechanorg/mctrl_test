---
name: dispatch-task
version: 1.0.0
description: Dispatch a bead-tracked task to an ai_orch agent session, register the mapping, and ack in Slack thread.
---

# dispatch-task

Use this skill when jleechan asks you to work on a task and you decide to dispatch it to an agent.

## When to use

- jleechan asks you to implement, fix, or investigate something that warrants spawning an agent
- You have decided the task merits a full agent run (not a quick inline answer)

## Steps

### 1. Claim or create the bead

```bash
# If bead exists:
bd update ORCH-xxx --status in_progress

# If new task:
bd create -p P1 -t task --title "short description"
# Note the ORCH-xxx ID from output
```

### 2. Ack in Slack thread

Reply to jleechan's original Slack message in the same thread:

> On it. Spawning agent for **ORCH-xxx** — will reply here when done.

Record the `ts` of jleechan's original message as `SLACK_TRIGGER_TS`.

### 3. Dispatch via mctrl

```bash
cd ~/project_jleechanclaw/mctrl

PYTHONPATH=src python -m orchestration.dispatch_task \
  --bead-id ORCH-xxx \
  --task "full task description for the agent" \
  --slack-trigger-ts "$SLACK_TRIGGER_TS" \
  --agent-cli claude
```

This will:
- Run `ai_orch run --async --worktree` to spawn a new tmux session + git worktree
- Record `start_sha` (HEAD at spawn time) for accurate commit detection
- Write the BeadSessionMapping to `.tracking/bead_session_registry.jsonl`
- The supervisor loop will watch the session and notify you when it finishes

### 4. Confirm dispatch

The command prints:
```
dispatched bead=ORCH-xxx session=ai-claude-xxxxxx worktree=/tmp/ai-orch-worktrees/...
```

Update bead notes:
```bash
bd update ORCH-xxx --append-notes "Dispatched to session ai-claude-xxxxxx. Supervisor watching."
```

## What happens next (automatic)

The mctrl supervisor loop (`ai.mctrl.supervisor` launchd agent) runs every 30s and:
1. Checks if the tmux session is still alive
2. When session ends: checks `git log start_sha..HEAD` for commits
3. Posts DM to jleechan + thread reply under the original Slack message
4. Sends MCP Agent Mail notification to OpenClaw

**You do not need to poll.** The supervisor handles completion notification.

## Notes

- `SLACK_TRIGGER_TS` is the Slack `ts` field from jleechan's message (e.g. `1772857900.668299`)
- Always use `--async --worktree` flags so each task gets an isolated git worktree
- The registry is at `.tracking/bead_session_registry.jsonl` in the mctrl repo
- If dispatch_task fails, check that `ai_orch` is on PATH and the mctrl repo is at `~/project_jleechanclaw/mctrl`
