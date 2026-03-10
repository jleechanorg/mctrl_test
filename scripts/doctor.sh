#!/usr/bin/env bash

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_CONFIG="$REPO_ROOT/openclaw-config"
LIVE_OPENCLAW="$HOME/.openclaw"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"
GATEWAY_LABEL="ai.openclaw.gateway"
GATEWAY_PLIST="$LAUNCHD_DIR/$GATEWAY_LABEL.plist"
SCHEDULED_LABELS=(
  "ai.openclaw.schedule.daily-checkin-9am"
  "ai.openclaw.schedule.daily-checkin-12pm"
  "ai.openclaw.schedule.daily-checkin-6pm"
  "ai.openclaw.schedule.backup-4h20"
  "ai.openclaw.schedule.genesis-memory-curation-weekly"
  "ai.openclaw.schedule.genesis-pattern-extraction-weekly"
)
MIGRATED_JOB_IDS=(
  "522e23a7-c7c1-41f2-b117-a3af05661578"
  "7424ea0d-2c8a-4a59-b58e-09b242c6c58e"
  "5192e214-2754-49d5-b567-07c7b24cb116"
  "882c6964-1deb-4b4b-936d-9edcab83fbda"
  "genesis-memory-curation-weekly"
  "genesis-pattern-extraction-weekly"
)

PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0

pass() {
  printf '[PASS] %s\n' "$1"
  PASS_COUNT=$((PASS_COUNT + 1))
}

warn() {
  printf '[WARN] %s\n' "$1"
  WARN_COUNT=$((WARN_COUNT + 1))
}

fail() {
  printf '[FAIL] %s\n' "$1"
  FAIL_COUNT=$((FAIL_COUNT + 1))
}

require_file() {
  local path="$1"
  local label="$2"
  if [[ -f "$path" ]]; then
    pass "$label present: $path"
  else
    fail "$label missing: $path"
  fi
}

require_dir() {
  local path="$1"
  local label="$2"
  if [[ -d "$path" ]]; then
    pass "$label present: $path"
  else
    fail "$label missing: $path"
  fi
}

require_cmd() {
  local cmd="$1"
  if command -v "$cmd" >/dev/null 2>&1; then
    pass "command available: $cmd"
  else
    fail "command missing: $cmd"
  fi
}

json_valid() {
  local file="$1"
  jq empty "$file" >/dev/null 2>&1
}

cmp_text() {
  local left="$1"
  local right="$2"
  [[ "$left" == "$right" ]]
}

printf 'OpenClaw Repo Doctor\n'
printf 'Repo: %s\n' "$REPO_ROOT"
printf 'Home: %s\n\n' "$HOME"

if [[ "$(uname -s)" == "Darwin" ]]; then
  pass 'running on macOS'
else
  warn 'non-macOS host; launchd checks may be invalid'
fi

require_cmd jq
require_cmd curl
require_cmd launchctl
require_cmd plutil
require_cmd openclaw
printf '\n'

require_dir "$REPO_CONFIG" 'repo config directory'
require_file "$REPO_CONFIG/openclaw.json" 'repo openclaw config'
require_file "$REPO_CONFIG/cron/jobs.json" 'repo cron jobs'
require_file "$REPO_CONFIG/ai.openclaw.gateway.plist" 'repo gateway plist'
require_file "$REPO_CONFIG/startup-check.sh" 'repo startup check script'
require_file "$REPO_CONFIG/run-scheduled-job.sh" 'repo scheduled job runner'
for label in "${SCHEDULED_LABELS[@]}"; do
  require_file "$REPO_CONFIG/$label.plist" "repo launchd schedule plist ($label)"
done
require_file "$REPO_ROOT/scripts/sync-openclaw-config.sh" 'sync script'
printf '\n'

require_dir "$LIVE_OPENCLAW" 'live ~/.openclaw'
require_file "$LIVE_OPENCLAW/openclaw.json" 'live openclaw config'
require_file "$LIVE_OPENCLAW/cron/jobs.json" 'live cron jobs'
require_dir "$LIVE_OPENCLAW/logs" 'live logs dir'
require_file "$LIVE_OPENCLAW/run-scheduled-job.sh" 'live scheduled job runner'
require_file "$GATEWAY_PLIST" 'live launchd gateway plist'
for label in "${SCHEDULED_LABELS[@]}"; do
  require_file "$LAUNCHD_DIR/$label.plist" "live launchd schedule plist ($label)"
done
printf '\n'

if [[ -f "$REPO_CONFIG/openclaw.json" ]] && json_valid "$REPO_CONFIG/openclaw.json"; then
  pass 'repo openclaw.json is valid JSON'
else
  fail 'repo openclaw.json is invalid JSON'
fi

if [[ -f "$LIVE_OPENCLAW/openclaw.json" ]] && json_valid "$LIVE_OPENCLAW/openclaw.json"; then
  pass 'live openclaw.json is valid JSON'
else
  fail 'live openclaw.json is invalid JSON'
fi

if [[ -f "$LIVE_OPENCLAW/openclaw.json" ]]; then
  live_token=$(jq -r '.gateway.auth.token // empty' "$LIVE_OPENCLAW/openclaw.json" 2>/dev/null || true)
  if [[ -n "$live_token" && "$live_token" != "null" && "$live_token" != "\${OPENCLAW_GATEWAY_TOKEN}" ]]; then
    pass 'live gateway auth token is set in ~/.openclaw/openclaw.json'
  else
    fail 'live gateway auth token missing/placeholder in ~/.openclaw/openclaw.json'
  fi
fi

if [[ -f "$REPO_CONFIG/openclaw.json" && -f "$LIVE_OPENCLAW/openclaw.json" ]]; then
  repo_norm=$(jq -c '{gateway:{port:.gateway.port,mode:.gateway.mode,bind:.gateway.bind,auth_mode:.gateway.auth.mode,tailscale_mode:.gateway.tailscale.mode,tailscale_reset:.gateway.tailscale.resetOnExit,chat_completions:.gateway.http.endpoints.chatCompletions.enabled},env:{OPENCLAW_RAW_STREAM:.env.OPENCLAW_RAW_STREAM,OPENCLAW_RAW_STREAM_PATH:.env.OPENCLAW_RAW_STREAM_PATH,GOOGLE_CLOUD_PROJECT:.env.GOOGLE_CLOUD_PROJECT}}' "$REPO_CONFIG/openclaw.json" 2>/dev/null || true)
  live_norm=$(jq -c '{gateway:{port:.gateway.port,mode:.gateway.mode,bind:.gateway.bind,auth_mode:.gateway.auth.mode,tailscale_mode:.gateway.tailscale.mode,tailscale_reset:.gateway.tailscale.resetOnExit,chat_completions:.gateway.http.endpoints.chatCompletions.enabled},env:{OPENCLAW_RAW_STREAM:.env.OPENCLAW_RAW_STREAM,OPENCLAW_RAW_STREAM_PATH:.env.OPENCLAW_RAW_STREAM_PATH,GOOGLE_CLOUD_PROJECT:.env.GOOGLE_CLOUD_PROJECT}}' "$LIVE_OPENCLAW/openclaw.json" 2>/dev/null || true)
  if cmp_text "$repo_norm" "$live_norm"; then
    pass 'repo/live normalized gateway config is in sync'
  else
    fail 'repo/live normalized gateway config drift detected'
  fi
fi

printf '\n'
if [[ -f "$LIVE_OPENCLAW/cron/jobs.json" ]] && json_valid "$LIVE_OPENCLAW/cron/jobs.json"; then
  still_enabled=()
  for job_id in "${MIGRATED_JOB_IDS[@]}"; do
    if jq -e --arg id "$job_id" 'any(.jobs[]?; .id == $id and (.enabled == true))' "$LIVE_OPENCLAW/cron/jobs.json" >/dev/null 2>&1; then
      still_enabled+=("$job_id")
    fi
  done

  if [[ ${#still_enabled[@]} -eq 0 ]]; then
    pass 'migrated OpenClaw cron jobs are disabled in ~/.openclaw/cron/jobs.json'
  else
    fail "migrated cron job IDs are still enabled in ~/.openclaw/cron/jobs.json: ${still_enabled[*]}"
  fi
else
  fail 'could not validate live cron jobs JSON'
fi

printf '\n'
if [[ -f "$GATEWAY_PLIST" ]]; then
  if plutil -lint "$GATEWAY_PLIST" >/dev/null 2>&1; then
    pass 'gateway launchd plist is valid'
  else
    fail 'gateway launchd plist failed plutil -lint'
  fi

  plist_port=$(plutil -extract EnvironmentVariables.OPENCLAW_GATEWAY_PORT raw -o - "$GATEWAY_PLIST" 2>/dev/null || true)
  live_port=$(jq -r '.gateway.port // empty' "$LIVE_OPENCLAW/openclaw.json" 2>/dev/null || true)
  if [[ -n "$plist_port" && -n "$live_port" && "$plist_port" == "$live_port" ]]; then
    pass "gateway port matches between plist and live config ($live_port)"
  else
    fail "gateway port mismatch (plist=$plist_port, live=$live_port)"
  fi

  plist_token=''
  if plist_token=$(plutil -extract EnvironmentVariables.OPENCLAW_GATEWAY_TOKEN raw -o - "$GATEWAY_PLIST" 2>/dev/null); then
    :
  fi
  if [[ -n "$plist_token" ]] && [[ "$plist_token" != *'Could not extract value'* ]]; then
    pass 'gateway token present in launchd EnvironmentVariables'
  else
    warn 'gateway token missing in launchd EnvironmentVariables (may still work via openclaw.json token)'
  fi
fi

printf '\n'
if [[ -x "$REPO_ROOT/scripts/sync-openclaw-config.sh" ]]; then
  sync_output="$($REPO_ROOT/scripts/sync-openclaw-config.sh 2>&1)"
  if grep -Eq 'MISSING IN LIVE|\+ NEW:|~ MODIFIED:' <<<"$sync_output"; then
    fail 'sync-openclaw-config dry run found unsynced files'
  else
    pass 'sync-openclaw-config dry run reports no drift for managed dirs'
  fi
else
  fail 'scripts/sync-openclaw-config.sh is not executable'
fi

printf '\n'
if launchctl print "gui/$(id -u)/$GATEWAY_LABEL" >/tmp/mctrl-doctor-launchctl.txt 2>&1; then
  pass 'launchd job is registered'
  if grep -q 'state = running' /tmp/mctrl-doctor-launchctl.txt; then
    pass 'launchd job state is running'
  else
    fail 'launchd job is not in running state'
  fi
else
  fail 'launchctl print failed for ai.openclaw.gateway'
fi

for label in "${SCHEDULED_LABELS[@]}"; do
  if launchctl print "gui/$(id -u)/$label" >/tmp/mctrl-doctor-launchctl-"$label".txt 2>&1; then
    pass "launchd schedule is registered: $label"
  else
    fail "launchd schedule is not registered: $label"
  fi
done

runtime_port=$(jq -r '.gateway.port // 18789' "$LIVE_OPENCLAW/openclaw.json" 2>/dev/null)
if lsof -nP -iTCP:"$runtime_port" -sTCP:LISTEN >/tmp/mctrl-doctor-lsof.txt 2>&1; then
  pass "a process is listening on gateway port $runtime_port"
else
  fail "no process listening on gateway port $runtime_port"
fi

health_body_file="/tmp/mctrl-doctor-health.json"
health_code=$(curl -sS --max-time 5 -o "$health_body_file" -w '%{http_code}' "http://127.0.0.1:${runtime_port}/health" 2>/tmp/mctrl-doctor-curl.err || true)
if [[ "$health_code" == "200" ]]; then
  pass 'HTTP /health endpoint returned 200'
  if jq empty "$health_body_file" >/dev/null 2>&1; then
    pass '/health response body is valid JSON'
  else
    warn '/health response body is not JSON'
  fi
else
  fail "HTTP /health endpoint failed (code=$health_code)"
  if [[ -s /tmp/mctrl-doctor-curl.err ]]; then
    warn "curl error: $(< /tmp/mctrl-doctor-curl.err)"
  fi
fi

status_output="$(openclaw gateway status 2>&1 || true)"
if grep -q 'Runtime: running' <<<"$status_output"; then
  pass 'openclaw gateway status reports runtime running'
else
  fail 'openclaw gateway status does not report runtime running'
fi
if grep -q 'RPC probe: failed' <<<"$status_output"; then
  fail 'openclaw gateway status reports RPC probe failure'
fi
if grep -q 'Service config issue:' <<<"$status_output"; then
  warn 'openclaw gateway status reports service config issue(s)'
fi

health_cli_output="$(openclaw gateway health 2>&1 || true)"
if grep -q '^Error:' <<<"$health_cli_output"; then
  fail 'openclaw gateway health reported an error'
  if grep -q 'gateway token mismatch' <<<"$health_cli_output"; then
    fail 'gateway token mismatch detected (gateway.remote.token should match gateway.auth.token)'
  fi
else
  pass 'openclaw gateway health completed without leading Error line'
fi

printf '\nSummary: %s pass, %s warn, %s fail\n' "$PASS_COUNT" "$WARN_COUNT" "$FAIL_COUNT"

if [[ "$FAIL_COUNT" -gt 0 ]]; then
  exit 1
fi

exit 0
