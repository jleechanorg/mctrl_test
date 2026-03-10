---
name: agento
version: 1.0.0
description: Delegate coding tasks to Agent-Orchestrator (AO) via the "agento" keyword.
---

# agento

Use this skill when the user's message contains the word **agento**.

## When to use

The user says "agento" to explicitly route a task through Agent-Orchestrator instead of mctrl.
Examples:
- "agento spawn worldai-claw-agento fix the login bug"
- "agento status"
- "agento send wa-abc1234 please push your changes"
- "agento fix PR 5879"

## AO CLI path

```
~/bin/ao
```

## Available projects (from agent-orchestrator.yaml)

- `worldai-pr5879` — WorldArchitect PR #5879 (jleechanorg/worldarchitect.ai, branch: tailscale_pub)

Add projects by editing `~/projects_reference/agent-orchestrator/agent-orchestrator.yaml`.

## Commands

### Spawn a new agent session

```bash
~/bin/ao spawn worldai-pr5879 <issue-number-or-PR>
```

For a freeform task (no issue number), omit the issue argument:
```bash
~/bin/ao spawn worldai-pr5879
```

### Check status of all sessions

```bash
~/bin/ao status
```

### Send a message to a running session

```bash
~/bin/ao send <session-id> "<message>"
```

### List sessions

```bash
~/bin/ao session ls
```

## Steps

1. Parse the user's intent from the message after "agento".
2. Map it to the right `ao` command above.
3. Run the command in the shell.
4. Reply immediately: "Delegated to agento — `ao spawn worldai-pr5879 <X>` started. I'll notify you when the PR is ready."
5. Do NOT wait for the spawn to complete — it runs async in tmux.

## Notes

- AO dashboard: `http://localhost:3011` (start with `~/bin/ao dashboard`)
- Config: `~/projects_reference/agent-orchestrator/agent-orchestrator.yaml`
- Sessions live in `~/.agent-orchestrator/` and `~/.worktrees/`
- Notifications: AO posts to #ai-slack-test via the agento-notifier webhook handler
