#!/usr/bin/env bash
# Run the mctrl supervisor loop.
# Called by the ai.mctrl.supervisor launchd agent.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

_source_optional() {
  local script_path="$1"
  if [[ ! -f "$script_path" ]]; then
    return 0
  fi
  # Don't let non-critical profile/setup script errors crash launchd service startup.
  set +e
  # shellcheck disable=SC1090
  source "$script_path" >/dev/null 2>&1
  local rc=$?
  set -e
  if [[ $rc -ne 0 ]]; then
    echo "warning: sourcing $script_path returned $rc; continuing" >&2
  fi
}

# Import OPENCLAW_SLACK_BOT_TOKEN via a subshell so any `exit` in helper
# scripts cannot terminate this launchd wrapper.
_import_openclaw_slack_token() {
  if [[ -n "${OPENCLAW_SLACK_BOT_TOKEN:-}" ]]; then
    return 0
  fi
  local script_path="$HOME/.openclaw/set-slack-env.sh"
  if [[ ! -f "$script_path" ]]; then
    return 0
  fi
  local token
  token="$(bash -lc "source \"$script_path\" >/dev/null 2>&1; printf '%s' \"\${OPENCLAW_SLACK_BOT_TOKEN:-}\"" 2>/dev/null || true)"
  if [[ -n "$token" ]]; then
    export OPENCLAW_SLACK_BOT_TOKEN="$token"
  fi
}

_import_openclaw_slack_token

# Load user-scoped environment values that may be absent in launchd.
_source_optional "$HOME/.profile"

export PYTHONPATH="$REPO_DIR/src"
export MCTRL_REGISTRY_PATH="$REPO_DIR/.tracking/bead_session_registry.jsonl"
export MCTRL_OUTBOX_PATH="$REPO_DIR/.messages/outbox.jsonl"
export MCTRL_DEAD_LETTER_PATH="$REPO_DIR/.messages/outbox_dead_letter.jsonl"
# Notification defaults for jleechanclaw mctrl loopback.
export OPENCLAW_NOTIFY_AGENT="${OPENCLAW_NOTIFY_AGENT:-main}"
export OPENCLAW_NOTIFY_CHANNEL="${OPENCLAW_NOTIFY_CHANNEL:-slack}"
export OPENCLAW_NOTIFY_TARGET="${OPENCLAW_NOTIFY_TARGET:-D0AFTLEJGJU}"

cd "$REPO_DIR"
exec python3 -m orchestration.supervisor --interval "${MCTRL_SUPERVISOR_INTERVAL:-30}"
