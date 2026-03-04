#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS="$REPO_ROOT/scripts"
RUNNER="$SCRIPTS/run-openclaw-backup.sh"
WATCHDOG="$SCRIPTS/backup-watchdog.sh"
PLIST_TEMPLATE="$SCRIPTS/openclaw-backup.plist.template"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"
PLIST_DST="$LAUNCHD_DIR/com.openclaw.backup.plist"
CRON_MARKER="# OpenClaw 4h backup for ~/.openclaw"
# Staggered at :40 — launchd fires approx :00, openclaw-cron at :20, system cron at :40.
CRON_CMD="$RUNNER"
WATCHDOG_MARKER="# OpenClaw backup watchdog (hourly)"

mkdir -p "$LAUNCHD_DIR"
mkdir -p "$HOME/Library/Logs/openclaw-backup"

if [[ ! -x "$RUNNER" ]]; then
  echo "Runner script not executable: $RUNNER" >&2
  exit 1
fi
if [[ ! -x "$WATCHDOG" ]]; then
  echo "Watchdog script not executable: $WATCHDOG" >&2
  exit 1
fi

# ---------- launchd ----------
# Generate plist with machine-specific paths from template
sed -e "s|@REPO_ROOT@|$REPO_ROOT|g" \
    -e "s|@HOME@|$HOME|g" \
  "$PLIST_TEMPLATE" > "$PLIST_DST"

BOOTSTRAP_ERR_FILE="$(mktemp)"
if ! launchctl bootstrap gui/$(id -u) "$PLIST_DST" 2>"$BOOTSTRAP_ERR_FILE"; then
  # If service already exists, unload/reload.
  if [[ -s "$BOOTSTRAP_ERR_FILE" ]]; then
    cat "$BOOTSTRAP_ERR_FILE" >&2
  fi
  launchctl bootout gui/$(id -u) "$PLIST_DST" 2>/dev/null || true
  launchctl bootstrap gui/$(id -u) "$PLIST_DST"
fi
rm -f "$BOOTSTRAP_ERR_FILE"
launchctl enable gui/$(id -u)/com.openclaw.backup
launchctl kickstart -k gui/$(id -u)/com.openclaw.backup

echo "Installed launchd job at $PLIST_DST"

# ---------- cron ----------
CRON_TMP="$(mktemp)"
crontab -l > "$CRON_TMP" 2>/dev/null || true

if ! grep -Fq "$CRON_MARKER" "$CRON_TMP"; then
  {
    echo "$CRON_MARKER"
    # :40 offset — staggered after launchd (:00) and openclaw-cron (:20)
    echo "40 */4 * * * $CRON_CMD"
  } >> "$CRON_TMP"
  crontab "$CRON_TMP"
  echo "Installed cron job: every 4 hours at :40"
elif ! grep -Fq "$CRON_CMD" "$CRON_TMP"; then
  # Marker exists but path or timing is stale; replace the cron line
  sed -i.bak "/\/4 \* \* \* \*/s|.*|40 */4 * * * $CRON_CMD|" "$CRON_TMP"
  crontab "$CRON_TMP"
  echo "Updated cron job path/timing to $CRON_CMD"
else
  echo "Cron job already present; skipping cron install."
fi

# ---------- watchdog (hourly) ----------
if ! grep -Fq "$WATCHDOG_MARKER" "$CRON_TMP"; then
  {
    echo "$WATCHDOG_MARKER"
    echo "0 * * * * $WATCHDOG"
  } >> "$CRON_TMP"
  crontab "$CRON_TMP"
  echo "Installed watchdog cron job: every hour"
elif ! grep -Fq "$WATCHDOG" "$CRON_TMP"; then
  sed -i.bak "\|$WATCHDOG_MARKER|{n; s|.*|0 * * * * $WATCHDOG|;}" "$CRON_TMP"
  crontab "$CRON_TMP"
  echo "Updated watchdog cron job path to $WATCHDOG"
else
  echo "Watchdog cron job already present; skipping."
fi

rm -f "$CRON_TMP"

echo "Done."
