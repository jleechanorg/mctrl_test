# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## AI Coding Agents

**All coding tasks go through `ai_orch`.** Never write code yourself when asked to implement something — always delegate to an agent via `ai_orch run`.

### Agent Priority (try in order)

1. **codexs** — Codex with Spark model + high reasoning. Best for most tasks.
2. **clauded** — Claude Sonnet with full permissions. Use if codexs fails or is unavailable.
3. **codex** — Vanilla Codex. Final fallback.

### Commands

```bash
# 1st choice: codexs (Codex Spark, high reasoning effort)
CODEX_MODEL=gpt-5.3-codex-spark ai_orch run --agent-cli codex "task description"

# 2nd choice: clauded (Claude Sonnet, skip-permissions)
ai_orch run --agent-cli claude --model sonnet "task description"

# 3rd choice: codex (vanilla)
ai_orch run --agent-cli codex "task description"
```

### Rules

- Always pass the full task context in the description string (repo path, what to change, acceptance criteria)
- Run from the relevant repo directory, or include the path in the task description
- After dispatching, tell the user: agent is running in tmux, attach with `ai_orch attach <session>`
- Do NOT wait for the agent to finish before responding — it runs async
- Before any PR operation, resolve repo from URL or explicit `<owner>/<repo>` and pass `--repo <owner>/<repo>` explicitly
- Never create/edit/merge PRs with implicit default repo context

### What counts as a coding task

Everything that involves writing, modifying, or testing code: bug fixes, new features, refactors, tests, scripts. Even "small" tasks go through ai_orch — consistency matters more than overhead.

## GitHub Repo Safety Snippets

```bash
# Inspect configured remotes and pick intended target
git remote -v

# Always pin repo on gh commands
gh pr view 5833 --repo jleechanorg/worldarchitect.ai
gh pr create --repo jleechanorg/worldai_claw ...
gh pr merge 123 --repo jleechanorg/worldarchitect.ai --squash
```

Add whatever helps you do your job. This is your cheat sheet.

## mctrl — Async Dispatch & Supervisor

**mctrl** is the local async task dispatch system at `~/project_jleechanclaw/mctrl`. It is NOT Mission Control and does NOT need MC env vars.

**RULE: NEVER call `ai_orch run --async --worktree` directly for coding tasks. Always use `dispatch_task`.** Direct ai_orch bypasses the registry and supervisor — Jeffrey gets no start/done notifications.

### When to use dispatch_task

Use `dispatch_task` for any task expected to produce **>100 lines of changes**, touch multiple repos, or run >60 seconds. For tiny single-file docs fixes, direct `ai_orch` is acceptable.

### How to dispatch

```bash
dispatch_task \
  --bead-id "$BEAD_ID" \
  --task "full task description" \
  --slack-trigger-ts "$SLACK_TRIGGER_TS" \
  --agent-cli claude
```

`dispatch_task` is a command on PATH (`~/bin/dispatch_task`). It:
- Spawns `ai_orch run --async --worktree` internally
- Registers the session in the bead↔session registry
- Posts `:rocket: Task started` to Jeffrey's DM + threads under the Slack trigger

### What the supervisor does

The **supervisor daemon** (`ai.mctrl.supervisor`) polls every 30s. When the tmux session exits:
- Posts `:white_check_mark: Task done` or `:warning: Task stalled` to Jeffrey's DM + thread
- You do NOT need to poll or check manually

### Key paths

| Path | Purpose |
|------|---------|
| `~/bin/dispatch_task` | Command on PATH — use this |
| `mctrl/.tracking/bead_session_registry.jsonl` | Live bead↔session registry |
| `~/Library/Logs/mctrl/supervisor.log` | Supervisor daemon logs |

### Supervisor status

```bash
launchctl list ai.mctrl.supervisor   # check if running
tail -20 ~/Library/Logs/mctrl/supervisor.log
```
