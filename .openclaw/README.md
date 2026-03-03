# .openclaw Layout Contract

This directory exists to make the boundary explicit between:

- **Synced OpenClaw config** (what maps to `~/.openclaw`) and
- **Repo-only custom artifacts** (what should stay in git only).

## Source of Truth

- `openclaw-config/` is the canonical, redacted, repo-safe mirror of `~/.openclaw`.
- `~/.openclaw` is the live runtime state on this machine.

## Sync Rules

1. Keep `openclaw-config/openclaw.json` structurally aligned with `~/.openclaw/openclaw.json`.
2. Never commit live secrets from `~/.openclaw` (tokens, auth files, credentials).
3. Use placeholders/env vars in `openclaw-config/` (for example `${DISCORD_BOT_TOKEN}`).
4. Keep custom, non-synced project notes/scripts outside `openclaw-config/`.

## Current Channel Baseline

The repo baseline currently tracks the main profile as:

- `channels.discord.enabled = false`
- `plugins.entries.discord.enabled = false`
- `channels.slack.enabled = true`
- `plugins.entries.slack.enabled = true`

Discord bot runtime is isolated in a separate local profile:

- `~/.openclaw-consensus` (Discord enabled, dedicated SOUL/tool policy)
- Repo backup for that profile lives in `discord-eng-bot/`:
  - `discord-eng-bot/openclaw.json` (redacted profile config)
  - `discord-eng-bot/SOUL.md` (prompt backup)
