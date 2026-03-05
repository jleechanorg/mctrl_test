# OpenClaw Config Audit Report
**Generated:** 2026-02-14

## Readable config files found in `~/.openclaw`
- `~/.openclaw/SOUL.md`
- `~/.openclaw/USER.md`
- `~/.openclaw/TOOLS.md`
- `~/.openclaw/IDENTITY.md`

## Notes
- This pass used a constrained execution mode; bootstrap/export was prepared via the `openclaw-rehome` scaffolding and confirmed as available.
- This audit reflects files explicitly readable in this environment.
- `AGENTS.md` was not found at `~/.openclaw/AGENTS.md`. (Workspace version is read and used instead.)
- Token scrub policy now enforced in `bootstrap-openclaw-config.sh` for common credential patterns (including Slack token formats).

## What to include in migration bundle
- `~/.openclaw` root files (especially the four above, plus any hidden JSON/YAML, TOML, and shell rc files if present).
- Workspace-level config under `~/.openclaw/workspace/`:
  - `SOUL.md`, `IDENTITY.md`, `USER.md`, `AGENTS.md`, `MEMORY.md` (optional), `HEARTBEAT.md`, `memory/*.md`, `TOOLS.md`.

## Data minimization / scrub strategy
Before publishing to a new repo:
- remove all credentials, API keys, cookies, tokens, PEMs, private keys, `.env`, `*token*`, `*secret*`, `*password*`, `*auth*`, OAuth/session artifacts.
- keep only behavior+process docs and non-sensitive defaults.
