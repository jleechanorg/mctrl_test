#!/usr/bin/env bash
# Run the mctrl supervisor loop.
# Called by the ai.mctrl.supervisor launchd agent.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Load Slack bot token if not already in env
if [[ -z "${SLACK_BOT_TOKEN:-}" && -z "${OPENCLAW_SLACK_BOT_TOKEN:-}" ]]; then
  if [[ -f "$HOME/.openclaw/set-slack-env.sh" ]]; then
    # shellcheck disable=SC1091
    source "$HOME/.openclaw/set-slack-env.sh" 2>/dev/null || true
  fi
fi

# Source ~/.profile to pick up user-scoped Slack/env values that are not part of
# the launchd environment, primarily SLACK_USER_TOKEN and any related shell
# exports used by local OpenClaw tooling.
if [[ -f "$HOME/.profile" ]]; then
  # shellcheck disable=SC1091
  source "$HOME/.profile" 2>/dev/null || true
fi

export PYTHONPATH="$REPO_DIR/src"
export MCTRL_REGISTRY_PATH="$REPO_DIR/.tracking/bead_session_registry.jsonl"
export MCTRL_OUTBOX_PATH="$REPO_DIR/.messages/outbox.jsonl"
# Notification defaults for jleechanclaw mctrl loopback.
export OPENCLAW_NOTIFY_AGENT="${OPENCLAW_NOTIFY_AGENT:-main}"
export OPENCLAW_NOTIFY_CHANNEL="${OPENCLAW_NOTIFY_CHANNEL:-slack}"
export OPENCLAW_NOTIFY_TARGET="${OPENCLAW_NOTIFY_TARGET:-D0AFTLEJGJU}"

cd "$REPO_DIR"
exec python3 -m orchestration.supervisor --interval "${MCTRL_SUPERVISOR_INTERVAL:-30}"
