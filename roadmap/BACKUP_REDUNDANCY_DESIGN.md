# Backup Redundancy Design

Bead: ORCH-dvd
Status: implemented

## Problem

The openclaw backup system had several reliability gaps:

1. **Single-scheduler, all at :00** — launchd, openclaw-cron, and system cron all fire at `0 */4 * * *`, causing lock contention. The second and third runners skip silently via flock, so two of three schedulers effectively do nothing.
2. **Wrong target repo** — the openclaw-cron job invoked `~/.openclaw/workspace/openclaw/scripts/run-openclaw-backup.sh`, placing backups inside the workspace copy instead of `project_jleechanclaw/jleechanclaw`.
3. **Python shutil copy** — slow full copy every run; no incremental logic; no `--delete` cleanup.
4. **No `latest/` pointer** — consumers must enumerate timestamped dirs to find the newest backup.
5. **No watchdog** — silent failure if all three schedulers are down; no alert until someone checks manually.
6. **Wrong consolidation target** — `sync_openclaw_full_redacted.sh` clones `jleechanorg/openclaw` (upstream) instead of `jleechanorg/jleechanclaw` (personal backup repo).

---

## Solution

### 1. rsync + post-redaction replacing shutil

`backup-openclaw-full.sh` now uses rsync for the initial mirror step:

```bash
rsync -a --delete \
  --exclude='.openclaw-backups' --exclude='.git' --exclude='.DS_Store' \
  "$SRC_DIR/" "$SNAPSHOT_DIR/"
```

Python runs afterward as a pure post-redaction pass — no more shutil.copy2.
Benefits: incremental transfer (only changed files), `--delete` keeps snapshot clean, faster for large agent session histories.

### 2. `latest/` symlink

After every successful `git commit`, the script updates a relative symlink:

```bash
cd "$SNAP_BASE" && ln -sfn "$SNAPSHOT_TS" latest
```

Consumers can always read `.openclaw-backups/latest/` without scanning timestamps.

### 3. Fix wrong target repo

`openclaw-config/cron/jobs.json` backup job now runs:
```
/Users/jleechan/project_jleechanclaw/jleechanclaw/scripts/run-openclaw-backup.sh
```

`openclaw/scripts/sync_openclaw_full_redacted.sh` now clones `jleechanorg/jleechanclaw`.

### 4. Triple-scheduler staggering

All three schedulers run the same `run-openclaw-backup.sh` but at different offsets. flock prevents overlap within a single host.

| Scheduler | Offset | Mechanism |
|-----------|--------|-----------|
| launchd | :00 (approx, from service load) | `StartInterval: 14400` unchanged |
| openclaw-cron | :20 | `cron expr: "20 */4 * * *"` in jobs.json |
| system cron | :40 | `40 */4 * * *` in crontab |

No two schedulers fire at the same wall-clock minute. Even with clock skew, a 20-minute gap is sufficient.

### 5. `backup-watchdog.sh`

Separate hourly script at `scripts/backup-watchdog.sh`. Installed by `install-openclaw-backup-jobs.sh` as `0 * * * *` cron.

Logic:
- Find newest snapshot under `.openclaw-backups/` (follows `latest/` symlink or scans dirs)
- Compute age in seconds
- If age > 6h (21600s): fire Slack webhook + send email alert
- Exit 0 always (watchdog must not break other crons)

Alert channels (both attempted, both best-effort):
- Slack: `SLACK_BACKUP_WEBHOOK` env var (incoming webhook URL)
- Email: same `EMAIL_USER` / `EMAIL_PASS` / `BACKUP_EMAIL` vars as `run-openclaw-backup.sh`

### 6. One-time consolidation

`scripts/consolidate-workspace-snapshots.sh` — run once to rsync existing snapshots from the workspace copy into the jleechanclaw repo.

Source: `~/.openclaw/workspace/openclaw/.openclaw-backups/`
Destination: `<repo>/.openclaw-backups/`

Uses `rsync -a --ignore-existing` so it never overwrites newer snapshots.

---

## Files Changed

| File | Change |
|------|--------|
| `scripts/backup-openclaw-full.sh` | rsync + post-redaction + latest/ symlink |
| `scripts/run-openclaw-backup.sh` | unchanged (email/lock wrapper) |
| `scripts/install-openclaw-backup-jobs.sh` | system cron → :40, add watchdog hourly cron |
| `openclaw-config/cron/jobs.json` | fix path + schedule → :20 |
| `openclaw/scripts/sync_openclaw_full_redacted.sh` | fix repo `openclaw` → `jleechanclaw` |
| `scripts/backup-watchdog.sh` | new — hourly watchdog |
| `scripts/consolidate-workspace-snapshots.sh` | new — one-time consolidation |
