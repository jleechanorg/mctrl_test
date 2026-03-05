#!/usr/bin/env bash
set -euo pipefail

# Report TaskPoller progress and optionally post to Slack thread/channel.

REPO_DIR=${TASKPOLLER_REPO_DIR:-/Users/jleechan/project_jleechanclaw/jleechanclaw}
INTERVAL_SECONDS=${TASKPOLLER_INTERVAL_SECONDS:-300}
LOOP_MODE=${TASKPOLLER_LOOP_MODE:-0}

SLACK_CHANNEL_ID=${SLACK_CHANNEL_ID:-}
SLACK_THREAD_TS=${SLACK_THREAD_TS:-}
OPENCLAW_MJS=${OPENCLAW_MJS:-/Users/jleechan/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw/openclaw.mjs}
DRY_RUN=${TASKPOLLER_DRY_RUN:-0}

LOG_FILE=${TASKPOLLER_STATUS_LOG:-/tmp/taskpoller_status.log}

: >"$LOG_FILE"

post_status() {
  local body="$1"

  # Slack via OpenClaw CLI (threaded reply preferred, fallback to channel send).
  if [[ -x "$OPENCLAW_MJS" && -n "$SLACK_CHANNEL_ID" ]]; then
    local args=("$OPENCLAW_MJS" "message")
    if [[ -n "$SLACK_THREAD_TS" ]]; then
      args+=("thread" "reply" "--channel" "slack" "--target" "channel:${SLACK_CHANNEL_ID}" "--reply-to" "$SLACK_THREAD_TS" "-m" "${body}")
    else
      args+=("send" "--channel" "slack" "-t" "channel:${SLACK_CHANNEL_ID}" "-m" "${body}")
    fi

    if [[ "$DRY_RUN" == "1" ]]; then
      args+=(--dry-run)
    fi

    "${args[@]}" >>"$LOG_FILE" 2>&1 || true
    return
  fi

  echo "No Slack destination configured; output stored locally only" >>"$LOG_FILE"
}

build_report() {
  {
    echo "TaskPoller Status Report: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    echo "Repo: $REPO_DIR"
    echo "Interval: ${INTERVAL_SECONDS}s"
    echo "Last commit: $(cd "$REPO_DIR" && git log -1 --oneline)"
    echo "Working tree changes:"
    cd "$REPO_DIR"
    if ! git status --short >/tmp/taskpoller_status_git.txt; then
      echo "(could not read git status)"
      return
    fi
    if [[ -s /tmp/taskpoller_status_git.txt ]]; then
      cat /tmp/taskpoller_status_git.txt
    else
      echo "clean"
    fi
    echo
      if [[ "$(git rev-parse --is-bare-repository)" == "true" ]]; then
      echo "Repository is bare."
    fi
    echo "Loop mode: $LOOP_MODE"
  }
}

run_once() {
  local report
  report="$(build_report)"
  echo "$(date -u '+%Y-%m-%d %H:%M:%S UTC')" "|" "${report//$'\n'/ }" >>"$LOG_FILE"
  post_status "$report"
}

if [[ "$LOOP_MODE" == "1" ]]; then
  while true; do
    run_once
    sleep "$INTERVAL_SECONDS"
  done
else
  run_once
fi
