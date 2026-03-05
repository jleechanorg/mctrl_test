#!/usr/bin/env bash
set -euo pipefail

# Manage a lightweight TaskPoller status reporter loop.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORTER="$SCRIPT_DIR/report_taskpoller_status.sh"
LOCK_FILE="${TASKPOLLER_STATUS_LOCK:-/tmp/taskpoller_status_loop.lock}"
PID_FILE="${TASKPOLLER_STATUS_PID:-/tmp/taskpoller_status_loop.pid}"

usage() {
  cat <<'EOF'
Usage:
  watch_taskpoller_status.sh start   # start background loop (every ${TASKPOLLER_INTERVAL_SECONDS:-300}s)
  watch_taskpoller_status.sh status  # run one pass now
  watch_taskpoller_status.sh stop    # stop loop
  watch_taskpoller_status.sh         # same as status

Env vars:
  TASKPOLLER_REPO_DIR         repo to check
  TASKPOLLER_INTERVAL_SECONDS polling interval in seconds (default 300)
  SLACK_BOT_TOKEN             Slack bot token
  SLACK_CHANNEL_ID            Slack channel ID (e.g. C123...)
  SLACK_THREAD_TS             Slack thread timestamp (for threaded replies)
  SLACK_WEBHOOK_URL           Optional webhook fallback (no thread support)
EOF
}

is_running() {
  if [[ -f "$PID_FILE" ]]; then
    local pid
    pid="$(cat "$PID_FILE")"
    if kill -0 "$pid" 2>/dev/null; then
      return 0
    fi
  fi
  return 1
}

start_loop() {
  if is_running; then
    echo "TaskPoller status watcher already running (pid: $(cat "$PID_FILE"))"
    exit 1
  fi

  local interval
  interval="${TASKPOLLER_INTERVAL_SECONDS:-300}"
  echo "Starting TaskPoller status loop (every ${interval}s)."
  echo "Set TASKPOLLER_REPO_DIR, SLACK_BOT_TOKEN, SLACK_CHANNEL_ID, and SLACK_THREAD_TS to enable thread posts."

  ( TASKPOLLER_LOOP_MODE=1 TASKPOLLER_INTERVAL_SECONDS="$interval" "$REPORTER" ) > /tmp/taskpoller_status_loop.log 2>&1 &
  echo $! > "$PID_FILE"
  echo "Started background loop with pid $(cat "$PID_FILE")."
}

stop_loop() {
  if ! is_running; then
    echo "Taskpoller status watcher not running."
    return
  fi
  local pid
  pid="$(cat "$PID_FILE")"
  kill "$pid" 2>/dev/null || true
  rm -f "$PID_FILE"
  echo "Stopped watcher (pid $pid)."
}

run_once() {
  TASKPOLLER_LOOP_MODE=0 "$REPORTER"
}

action="${1:-status}"
case "$action" in
  start)
    start_loop
    ;;
  stop)
    stop_loop
    ;;
  status)
    run_once
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    echo "Unknown action: $action"
    usage
    exit 1
    ;;
esac
