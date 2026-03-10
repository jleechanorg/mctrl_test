#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="$REPO_ROOT/openclaw-config"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"
LIVE_DIR="$HOME/.openclaw"
LIVE_JOBS="$LIVE_DIR/cron/jobs.json"
RUNNER_SRC="$CONFIG_DIR/run-scheduled-job.sh"
RUNNER_DST="$LIVE_DIR/run-scheduled-job.sh"
SCHEDULED_LOG_DIR="$LIVE_DIR/logs/scheduled-jobs"

MIGRATED_JOB_IDS=(
  "522e23a7-c7c1-41f2-b117-a3af05661578"
  "7424ea0d-2c8a-4a59-b58e-09b242c6c58e"
  "5192e214-2754-49d5-b567-07c7b24cb116"
  "882c6964-1deb-4b4b-936d-9edcab83fbda"
  "genesis-memory-curation-weekly"
  "genesis-pattern-extraction-weekly"
)

render_and_load_plist() {
  local src="$1"
  local label
  local dst

  label="$(basename "$src" .plist)"
  dst="$LAUNCHD_DIR/$label.plist"

  sed -e "s|@HOME@|$HOME|g" "$src" >"$dst"

  if ! launchctl bootstrap "gui/$(id -u)" "$dst" 2>/dev/null; then
    launchctl bootout "gui/$(id -u)" "$dst" 2>/dev/null || true
    launchctl bootstrap "gui/$(id -u)" "$dst"
  fi

  launchctl enable "gui/$(id -u)/$label" || true
  echo "  ✓ loaded $label"
}

printf 'Installing OpenClaw launchd scheduled jobs\n'
printf 'Repo: %s\n\n' "$REPO_ROOT"

if [[ ! -x "$RUNNER_SRC" ]]; then
  echo "Missing executable runner: $RUNNER_SRC" >&2
  exit 1
fi

mkdir -p "$LAUNCHD_DIR" "$LIVE_DIR" "$LIVE_DIR/cron" "$SCHEDULED_LOG_DIR"
install -m 755 "$RUNNER_SRC" "$RUNNER_DST"
echo "  ✓ installed runner $RUNNER_DST"

echo "Installing launchd scheduled job plists..."
for plist in "$CONFIG_DIR"/ai.openclaw.schedule.*.plist; do
  [[ -f "$plist" ]] || continue
  render_and_load_plist "$plist"
done

if [[ -f "$LIVE_JOBS" ]]; then
  backup="$LIVE_JOBS.bak.$(date +%Y%m%d-%H%M%S)"
  cp "$LIVE_JOBS" "$backup"

  jq --argjson ids "$(printf '%s\n' "${MIGRATED_JOB_IDS[@]}" | jq -R . | jq -s .)" '
    .jobs = ((.jobs // []) | map(if (.id as $id | ($ids | index($id)) != null) then .enabled = false else . end))
  ' "$LIVE_JOBS" > "$LIVE_JOBS.tmp"

  mv "$LIVE_JOBS.tmp" "$LIVE_JOBS"
  echo "  ✓ disabled migrated in-app cron jobs in $LIVE_JOBS"
  echo "  ✓ backup saved at $backup"
else
  echo "  ! live cron file missing: $LIVE_JOBS (skipped disable step)"
fi

printf '\nVerifying loaded labels...\n'
for plist in "$CONFIG_DIR"/ai.openclaw.schedule.*.plist; do
  label="$(basename "$plist" .plist)"
  if launchctl print "gui/$(id -u)/$label" >/dev/null 2>&1; then
    echo "  ✓ $label registered"
  else
    echo "  ✗ $label not registered"
  fi
done

echo
echo "Done. Scheduled OpenClaw jobs now run via launchd labels ai.openclaw.schedule.*"
