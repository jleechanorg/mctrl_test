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
ROLLBACK_JOBS_BACKUP=""
MIGRATION_COMMITTED=0
SYNC_SCRIPT="$REPO_ROOT/scripts/sync-openclaw-config.sh"

default_migrated_job_ids() {
  cat <<'EOF'
522e23a7-c7c1-41f2-b117-a3af05661578
7424ea0d-2c8a-4a59-b58e-09b242c6c58e
5192e214-2754-49d5-b567-07c7b24cb116
882c6964-1deb-4b4b-936d-9edcab83fbda
genesis-memory-curation-weekly
genesis-pattern-extraction-weekly
EOF
}

load_migrated_job_ids() {
  MIGRATED_JOB_IDS=()
  while IFS= read -r id; do
    [[ -n "$id" ]] && MIGRATED_JOB_IDS+=("$id")
  done < <(jq -r '.migratedLaunchdJobIds[]?' "$CONFIG_DIR/cron/jobs.json" 2>/dev/null || true)

  if [[ ${#MIGRATED_JOB_IDS[@]} -eq 0 ]]; then
    while IFS= read -r id; do
      [[ -n "$id" ]] && MIGRATED_JOB_IDS+=("$id")
    done < <(default_migrated_job_ids)
  fi
}

detect_local_timezone() {
  local target
  target="$(readlink /etc/localtime 2>/dev/null || true)"
  if [[ "$target" == *"/zoneinfo/"* ]]; then
    echo "${target##*/zoneinfo/}"
    return 0
  fi
  echo "${TZ:-unknown}"
}

rollback_on_error() {
  if [[ "$MIGRATION_COMMITTED" -eq 0 && -n "$ROLLBACK_JOBS_BACKUP" && -f "$ROLLBACK_JOBS_BACKUP" ]]; then
    cp "$ROLLBACK_JOBS_BACKUP" "$LIVE_JOBS"
    echo "  ! restored in-app cron config from backup due to migration failure: $ROLLBACK_JOBS_BACKUP" >&2
  fi
}

# Validate required tools before mutating anything (avoids half-migrated state)
if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required but not installed. Install with: brew install jq" >&2
  exit 1
fi
if ! command -v launchctl >/dev/null 2>&1; then
  echo "Error: launchctl is required (macOS only)" >&2
  exit 1
fi

# Sync repo openclaw-config to live before loading (ensures jobs.json and skills are current)
SYNC_SCRIPT="$REPO_ROOT/scripts/sync-openclaw-config.sh"
if [[ -x "$SYNC_SCRIPT" ]]; then
  "$SYNC_SCRIPT" --execute
fi

load_migrated_job_ids

LOCAL_TZ="$(detect_local_timezone)"
if [[ "$LOCAL_TZ" != "America/Los_Angeles" && "${OPENCLAW_ALLOW_NON_PT_SCHEDULE:-0}" != "1" ]]; then
  echo "Error: local timezone is '$LOCAL_TZ' but migrated schedules are defined for America/Los_Angeles." >&2
  echo "Set OPENCLAW_ALLOW_NON_PT_SCHEDULE=1 to override." >&2
  exit 1
fi
trap rollback_on_error ERR

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

if ! command -v jq >/dev/null 2>&1; then
  echo "Missing required command: jq" >&2
  exit 1
fi
if ! command -v launchctl >/dev/null 2>&1; then
  echo "Missing required command: launchctl" >&2
  exit 1
fi

if [[ ! -x "$RUNNER_SRC" ]]; then
  echo "Missing executable runner: $RUNNER_SRC" >&2
  exit 1
fi

mkdir -p "$LAUNCHD_DIR" "$LIVE_DIR" "$LIVE_DIR/cron" "$SCHEDULED_LOG_DIR"
install -m 755 "$RUNNER_SRC" "$RUNNER_DST"
echo "  ✓ installed runner $RUNNER_DST"

if [[ -f "$LIVE_JOBS" ]]; then
  backup="$LIVE_JOBS.bak.$(date +%Y%m%d-%H%M%S)"
  cp "$LIVE_JOBS" "$backup"
  ROLLBACK_JOBS_BACKUP="$backup"

  jq --argjson ids "$(printf '%s\n' "${MIGRATED_JOB_IDS[@]}" | jq -R . | jq -s .)" '
    .jobs = ((.jobs // []) | map(if (.id as $id | ($ids | index($id)) != null) then .enabled = false else . end))
  ' "$LIVE_JOBS" > "$LIVE_JOBS.tmp"

  mv "$LIVE_JOBS.tmp" "$LIVE_JOBS"
  echo "  ✓ disabled migrated in-app cron jobs in $LIVE_JOBS"
  echo "  ✓ backup saved at $backup"

  gateway_pid="$(pgrep -f 'openclaw.*gateway' | head -n1 || true)"
  if [[ -n "$gateway_pid" ]]; then
    kill -HUP "$gateway_pid" 2>/dev/null || true
    echo "  ✓ signaled gateway reload (pid=$gateway_pid)"
  else
    echo "  ! no running gateway pid found for HUP reload"
  fi
else
  echo "  ! live cron file missing: $LIVE_JOBS (skipped disable step)"
fi

echo "Installing launchd scheduled job plists..."
for plist in "$CONFIG_DIR"/ai.openclaw.schedule.*.plist; do
  [[ -f "$plist" ]] || continue
  render_and_load_plist "$plist"
done
MIGRATION_COMMITTED=1
trap - ERR

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
