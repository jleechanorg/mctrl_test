#!/bin/bash
# Periodic proactive monitoring agent for OpenClaw

set -u

LOG_FILE="$HOME/.openclaw/logs/monitor-agent.log"
LOG_DIR="$(dirname "$LOG_FILE")"
LOCK_DIR="$HOME/.openclaw/locks/monitor-agent.lock"

export PATH="$HOME/.nvm/versions/node/current/bin:$HOME/.nvm/versions/node/v22.22.0/bin:$HOME/Library/pnpm:$HOME/.bun/bin:$HOME/.local/bin:$HOME/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

OPENCLAW_BIN="$(command -v openclaw || true)"
ALERT_SLACK_TARGET="${OPENCLAW_MONITOR_SLACK_TARGET:-C0AJQ5M0A0Y}"

ts() {
  date '+%Y-%m-%d %H:%M:%S'
}

log() {
  mkdir -p "$LOG_DIR" 2>/dev/null || true
  printf '[%s] %s\n' "$(ts)" "$*" >> "$LOG_FILE"
}

if [ -z "$OPENCLAW_BIN" ]; then
  log "openclaw CLI not found"
  exit 1
fi

mkdir -p "$(dirname "$LOCK_DIR")" 2>/dev/null || true
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  log "Another monitor-agent run is active; skipping."
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

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

if "$OPENCLAW_BIN" agent --agent monitor --message "$PROMPT" --deliver --reply-channel slack --reply-to "$ALERT_SLACK_TARGET" >> "$LOG_FILE" 2>&1; then
  log "Monitoring agent completed and delivered to Slack target ${ALERT_SLACK_TARGET}."
else
  log "Monitoring agent run failed. Sending fallback Slack alert."
  "$OPENCLAW_BIN" message send --channel slack --target "$ALERT_SLACK_TARGET" --message ":warning: OpenClaw monitoring agent failed. Check ~/.openclaw/logs/monitor-agent.log" >> "$LOG_FILE" 2>&1 || true
  exit 1
fi

exit 0
