#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_ROOT="${SYMPHONY_DAEMON_RUNTIME:-/tmp/jleechanclaw/symphony_daemon}"
METADATA="$RUNTIME_ROOT/daemon_metadata.json"

if [[ ! -f "$METADATA" ]]; then
  echo "Missing metadata: $METADATA" >&2
  echo "Run scripts/setup-symphony-daemon.py first." >&2
  exit 1
fi

NODE_NAME="$(jq -r '.node_name' "$METADATA")"
COOKIE="$(jq -r '.cookie' "$METADATA")"
SYMPHONY_ELIXIR_DIR="$(jq -r '.symphony_elixir_dir' "$METADATA")"
PLUGIN_NAME="${SYMPHONY_TASK_PLUGIN:-generic_tasks}"
PLUGIN_INPUT="${SYMPHONY_TASK_PLUGIN_INPUT:-$(jq -r '.task_plugin_input' "$METADATA")}"
ISSUES_JSON="${SYMPHONY_TASK_ISSUES_JSON:-$RUNTIME_ROOT/issues.$(date +%s).json}"

SYMPHONY_TASK_PLUGIN="$PLUGIN_NAME" \
SYMPHONY_TASK_PLUGIN_INPUT="$PLUGIN_INPUT" \
SYMPHONY_TASK_ISSUES_JSON="$ISSUES_JSON" \
python3 "$ROOT_DIR/scripts/prepare-symphony-payload.py"

cd "$SYMPHONY_ELIXIR_DIR"
/opt/homebrew/bin/mise exec -- epmd -daemon || true
SYMPHONY_DAEMON_NODE="$NODE_NAME" \
SYMPHONY_DAEMON_COOKIE="$COOKIE" \
TASK_ISSUES_JSON="$ISSUES_JSON" \
/opt/homebrew/bin/mise exec -- mix run "$ROOT_DIR/scripts/enqueue-symphony-memory-issues.exs"
