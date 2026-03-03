# OpenClaw ~/.openclaw Backup Automation

This repository includes a recurring backup workflow for `~/.openclaw` that runs on:

- `launchd` (24/7 Apple scheduler)

Guardrail:
- Forbidden: system `crontab` edits for OpenClaw jobs.
- Required: OpenClaw gateway cron subcommands for reminders/schedules (`openclaw cron ...`).

Backups are written into this repository as redacted snapshots under:

- `.openclaw-backups/<YYYYMMDD_HHMMSS>/`

## What gets backed up

The backup script mirrors `~/.openclaw` contents and performs in-band redaction/scrubbing:

- masks common secret-bearing environment/key/token patterns in text files
- redacts obvious embedded credential strings
- skips obvious binary/log/db/ipynb/jsonl artifacts
- keeps a `REDACTION_MANIFEST.txt` per snapshot

## Files added

- `scripts/backup-openclaw-full.sh` — creates redacted snapshot and commits when changed
- `scripts/run-openclaw-backup.sh` — wrapper with timestamped logging
- `scripts/openclaw-backup.plist.template` — `launchd` job template
- `scripts/install-openclaw-backup-jobs.sh` — installs launchd schedules and removes legacy OpenClaw crontab entries

## Install recurring jobs

```bash
cd ~/.openclaw/workspace/openclaw
./scripts/install-openclaw-backup-jobs.sh
```

This creates:

- `com.openclaw.backup` launchd job at `~/Library/LaunchAgents/`

## Verify

```bash
# launchd status
launchctl print gui/$(id -u)/com.openclaw.backup
# OpenClaw reminder scheduler
openclaw cron status
openclaw cron list
# run once now
./scripts/run-openclaw-backup.sh
```

## Logs

- `~/Library/Logs/openclaw-backup/openclaw-backup.log`
- `~/Library/Logs/openclaw-backup/stdout.log`
- `~/Library/Logs/openclaw-backup/stderr.log`
