# OpenClaw Key Backup Scope

This repo stores a curated backup of **key** files from `~/.openclaw`.

## Included
- Core config/docs: `openclaw.json`, key `*.md`, health/monitor scripts.
- LaunchAgent plists under `openclaw-config/launchd/`.
- Agent metadata for `main` and `monitor` (`models.json`).
- Dedicated monitor workspace docs/state under `openclaw-config/workspaces/monitor/`.
- Redacted auth profile summaries:
  - `openclaw-config/agents/main/agent/auth-profiles.redacted.json`
  - `openclaw-config/agents/monitor/agent/auth-profiles.redacted.json`

## Excluded
- Secret-bearing credentials and raw auth profile tokens.
- Large/high-churn runtime artifacts (session logs/indexes, lock files, databases).
- Node module trees and transient build output.

## Refresh Command
Run:

```bash
./scripts/backup-openclaw-key-config.sh
```

This pulls current live files from `~/.openclaw` into `openclaw-config/`.
