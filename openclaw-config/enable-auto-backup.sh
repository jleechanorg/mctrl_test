#!/usr/bin/env bash

set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "enable-auto-backup.sh requires macOS (launchd)." >&2
  exit 1
fi

# Installs a launchd job that creates a daily backup tarball of
# ~/.openclaw and LaunchAgent config at 2:00 AM.
#
# Usage:
#   ./enable-auto-backup.sh
#
# The job calls ~/.openclaw/backup-content.sh (created lazily below).
# Guardrail: OpenClaw automation must not use system crontab.

OPENCLAW_DIR="$HOME/.openclaw"
BACKUP_DIR="$OPENCLAW_DIR/backups"
SCRIPT_PATH="$OPENCLAW_DIR/backup-content.sh"
LAUNCHAGENT="$HOME/Library/LaunchAgents/ai.openclaw.gateway.plist"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$LAUNCHD_DIR/ai.openclaw.backup.daily.plist"
LOG_DIR="$HOME/.openclaw/logs"
CRON_MARK="# OpenClaw daily backup"

mkdir -p "$BACKUP_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$LAUNCHD_DIR"

cat > "$SCRIPT_PATH" <<'EOF_SCRIPT'
#!/usr/bin/env bash
set -euo pipefail

BACKUP_DATE="$(date +%Y%m%d)"
BACKUP_DIR="$HOME/.openclaw/backups"
OPENCLAW_DIR="$HOME/.openclaw"
LAUNCHAGENT="$HOME/Library/LaunchAgents/ai.openclaw.gateway.plist"
mkdir -p "$BACKUP_DIR"

# Collect tar sources safely (ignore missing LaunchAgent plist on first-run environments)
TAR_SOURCES=("$OPENCLAW_DIR")
if [ -f "$LAUNCHAGENT" ]; then
  TAR_SOURCES+=("$LAUNCHAGENT")
fi

tar --exclude "${BACKUP_DIR#/}" \
  --exclude '*.bak' \
  -czf "$BACKUP_DIR/backup-${BACKUP_DATE}.tar.gz" \
  "${TAR_SOURCES[@]}"

# Keep 30-day retention
find "$BACKUP_DIR" -name 'backup-*.tar.gz' -type f -mtime +30 -delete || true
EOF_SCRIPT
chmod +x "$SCRIPT_PATH"

# Install/update launchd entry (daily at 2:00 AM local time)
cat > "$PLIST_PATH" <<EOF_PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>ai.openclaw.backup.daily</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$SCRIPT_PATH</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>2</integer>
    <key>Minute</key>
    <integer>0</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>$LOG_DIR/backup-content.out.log</string>
  <key>StandardErrorPath</key>
  <string>$LOG_DIR/backup-content.err.log</string>
  <key>RunAtLoad</key>
  <false/>
</dict>
</plist>
EOF_PLIST

BOOTSTRAP_ERR_FILE="$(mktemp)"
if ! launchctl bootstrap gui/$(id -u) "$PLIST_PATH" 2>"$BOOTSTRAP_ERR_FILE"; then
  if [[ -s "$BOOTSTRAP_ERR_FILE" ]]; then
    cat "$BOOTSTRAP_ERR_FILE" >&2
  fi
  launchctl bootout gui/$(id -u) "$PLIST_PATH" 2>/dev/null || true
  launchctl bootstrap gui/$(id -u) "$PLIST_PATH"
fi
rm -f "$BOOTSTRAP_ERR_FILE"
launchctl enable gui/$(id -u)/ai.openclaw.backup.daily
launchctl kickstart -k gui/$(id -u)/ai.openclaw.backup.daily

# Remove legacy OpenClaw system crontab lines if present
if command -v crontab >/dev/null 2>&1; then
  CRON_BEFORE="$(mktemp)"
  CRON_AFTER="$(mktemp)"
  crontab -l > "$CRON_BEFORE" 2>/dev/null || true
  if [[ -s "$CRON_BEFORE" ]]; then
    grep -Fv "$CRON_MARK" "$CRON_BEFORE" | grep -Fv "$SCRIPT_PATH" > "$CRON_AFTER" || true
    if ! cmp -s "$CRON_BEFORE" "$CRON_AFTER"; then
      crontab "$CRON_AFTER"
      echo "Removed legacy OpenClaw backup entries from system crontab."
    fi
  fi
  rm -f "$CRON_BEFORE" "$CRON_AFTER"
fi

echo "Installed launchd backup job: ai.openclaw.backup.daily"
echo "Schedule: daily at 02:00 local time"
echo "Backups will be written to: $BACKUP_DIR"
echo "Reminder/schedule guardrail: use 'openclaw cron ...' for OpenClaw jobs; do not use system crontab."
