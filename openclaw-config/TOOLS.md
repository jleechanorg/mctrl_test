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
- Run from a git worktree path for the relevant repo (never the primary checkout)
- After dispatching, tell the user: agent is running in tmux, attach with `ai_orch attach <session>`
- Do NOT wait for the agent to finish before responding — it runs async
- Before any PR operation, resolve repo from URL or explicit `<owner>/<repo>` and pass `--repo <owner>/<repo>` explicitly
- Never create/edit/merge PRs with implicit default repo context

### Worktree Guardrails (Mandatory)

- Coding tasks are blocked unless executed from a git worktree.
- Pre-check before `ai_orch run`:
  - `git rev-parse --git-dir | grep -q '.git/worktrees/'`
  - If that command fails, stop and create/use a linked worktree first.
- If no worktree exists, create one first and dispatch inside that path.

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

## CLI aliases

- `aiorch` is shorthand for the `ai_orch` binary.

Add whatever helps you do your job. This is your cheat sheet.
