#!/bin/bash
# Periodic proactive monitoring agent for OpenClaw

set -u

LOG_FILE="$HOME/.openclaw/logs/monitor-agent.log"
LOG_DIR="$(dirname "$LOG_FILE")"
LOCK_DIR="$HOME/.openclaw/locks/monitor-agent.lock"
LOCK_PID_FILE="$LOCK_DIR/pid"
LOCK_STALE_SECONDS="${OPENCLAW_MONITOR_LOCK_STALE_SECONDS:-7200}"
AGENT_TIMEOUT_SECONDS="${OPENCLAW_MONITOR_AGENT_TIMEOUT_SECONDS:-300}"

export PATH="$HOME/.nvm/versions/node/current/bin:$HOME/.nvm/versions/node/v22.22.0/bin:$HOME/Library/pnpm:$HOME/.bun/bin:$HOME/.local/bin:$HOME/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

OPENCLAW_BIN="$(command -v openclaw || true)"
ALERT_SLACK_TARGET="${OPENCLAW_MONITOR_SLACK_TARGET:-}"

ts() {
  date '+%Y-%m-%d %H:%M:%S'
}

log() {
  mkdir -p "$LOG_DIR" 2>/dev/null || true
  printf '[%s] %s\n' "$(ts)" "$*" >> "$LOG_FILE"
}

append_report() {
  mkdir -p "$LOG_DIR" 2>/dev/null || true
  printf '%s\n' "$REPORT" >> "$LOG_FILE"
}

if [ -z "$OPENCLAW_BIN" ]; then
  log "openclaw CLI not found"
  exit 1
fi

mkdir -p "$(dirname "$LOCK_DIR")" 2>/dev/null || true

lock_mtime_epoch() {
  if stat -f %m "$LOCK_DIR" >/dev/null 2>&1; then
    stat -f %m "$LOCK_DIR"
  else
    stat -c %Y "$LOCK_DIR" 2>/dev/null || echo 0
  fi
}

acquire_lock() {
  if mkdir "$LOCK_DIR" 2>/dev/null; then
    echo "$$" > "$LOCK_PID_FILE"
    return 0
  fi

  local pid=""
  if [ -f "$LOCK_PID_FILE" ]; then
    pid="$(cat "$LOCK_PID_FILE" 2>/dev/null || true)"
  fi

  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    log "Another monitor-agent run is active (pid=$pid); skipping."
    return 1
  fi

  local now age
  now="$(date +%s)"
  age=$(( now - $(lock_mtime_epoch) ))
  if [ "$age" -lt "$LOCK_STALE_SECONDS" ]; then
    log "Lock exists without live pid but is recent (${age}s < ${LOCK_STALE_SECONDS}s); skipping."
    return 1
  fi

  log "Removing stale lock (age=${age}s, pid='${pid:-unknown}')."
  rm -rf "$LOCK_DIR" 2>/dev/null || true
  if mkdir "$LOCK_DIR" 2>/dev/null; then
    echo "$$" > "$LOCK_PID_FILE"
    return 0
  fi

  log "Failed to acquire lock after stale cleanup; skipping."
  return 1
}

if ! acquire_lock; then
  exit 0
fi
trap 'rm -f "$LOCK_PID_FILE" 2>/dev/null || true; rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

PROMPT="You are the OpenClaw monitoring agent.
PRIMARY OBJECTIVE: report ONLY live, currently-active issues.

Hard rules (must follow):
1) Check live gateway now via http://127.0.0.1:18789/health and report exact result.
2) Check current launchd state now for ai.openclaw.gateway and ai.openclaw.health-check.
3) Log analysis must be limited to very recent lines only (last 120 seconds). Do NOT treat older lines as active incidents.
4) Past context may be included only under a separate 'Historical context' section and must not be labeled as current problems.
5) Only mark STATUS=PROBLEM if the issue is reproducible now or present in the recent (<=120s) window.

Output format (strict):
STATUS=GOOD or STATUS=PROBLEM
ACTIVE EVIDENCE:
- ...
ACTIVE PROBLEMS:
- ... (or 'none')
HISTORICAL CONTEXT:
- ... (optional)"

run_monitor_agent() {
  if command -v gtimeout >/dev/null 2>&1; then
    gtimeout "${AGENT_TIMEOUT_SECONDS}s" "$OPENCLAW_BIN" agent --agent monitor --message "$PROMPT" 2>&1
    return $?
  fi
  if command -v timeout >/dev/null 2>&1; then
    timeout "${AGENT_TIMEOUT_SECONDS}s" "$OPENCLAW_BIN" agent --agent monitor --message "$PROMPT" 2>&1
    return $?
  fi
  perl -e 'alarm shift; exec @ARGV' "$AGENT_TIMEOUT_SECONDS" "$OPENCLAW_BIN" agent --agent monitor --message "$PROMPT" 2>&1
}

REPORT="$(run_monitor_agent)"
AGENT_RC=$?

if [ "$AGENT_RC" -eq 124 ] || [ "$AGENT_RC" -eq 142 ]; then
  log "Monitoring agent timed out after ${AGENT_TIMEOUT_SECONDS}s (suppressed Slack)."
  append_report
  exit 124
fi

if [ "$AGENT_RC" -ne 0 ]; then
  log "Monitoring agent run failed (suppressed Slack). rc=${AGENT_RC}"
  append_report
  exit "$AGENT_RC"
fi

if grep -q "STATUS=PROBLEM" <<<"$REPORT"; then
  if [ -z "$ALERT_SLACK_TARGET" ]; then
    log "STATUS=PROBLEM but OPENCLAW_MONITOR_SLACK_TARGET is unset; Slack delivery skipped."
    append_report
    exit 0
  fi
  mkdir -p "$LOG_DIR" 2>/dev/null || true
  if "$OPENCLAW_BIN" message send --channel slack --target "$ALERT_SLACK_TARGET" --message "$REPORT" >> "$LOG_FILE" 2>&1; then
    log "Monitoring agent reported STATUS=PROBLEM and delivered to Slack target ${ALERT_SLACK_TARGET}."
  else
    log "Monitoring agent reported STATUS=PROBLEM but Slack delivery failed."
    exit 1
  fi
else
  log "Monitoring agent reported non-PROBLEM status; Slack delivery suppressed."
  append_report
fi

exit 0
