#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_ROOT="${SYMPHONY_DAEMON_RUNTIME:-$HOME/Library/Application Support/jleechanclaw/symphony_daemon}"
METADATA="$RUNTIME_ROOT/daemon_metadata.json"

if [[ ! -f "$METADATA" ]]; then
  echo "Missing metadata: $METADATA" >&2
  echo "Run scripts/setup-symphony-daemon.py first." >&2
  exit 1
fi

NODE_NAME="$(jq -r '.node_name' "$METADATA")"
COOKIE="$(jq -r '.cookie' "$METADATA")"
SYMPHONY_ELIXIR_DIR="$(jq -r '.symphony_elixir_dir' "$METADATA")"
MISE_BIN="${MISE_BIN:-$(jq -r '.mise_bin // empty' "$METADATA")}"
if [[ -z "$MISE_BIN" ]]; then
  MISE_BIN="/opt/homebrew/bin/mise"
fi
if [[ ! -x "$MISE_BIN" ]]; then
  if command -v mise >/dev/null 2>&1; then
    MISE_BIN="$(command -v mise)"
  else
    echo "Missing mise binary: $MISE_BIN" >&2
    exit 1
  fi
fi

PLUGIN_NAME="${SYMPHONY_TASK_PLUGIN:-generic_tasks}"
PLUGIN_INPUT="${SYMPHONY_TASK_PLUGIN_INPUT:-$(jq -r '.task_plugin_input' "$METADATA")}"
ISSUES_JSON="${SYMPHONY_TASK_ISSUES_JSON:-$RUNTIME_ROOT/issues.$(date +%s).json}"

SYMPHONY_TASK_PLUGIN="$PLUGIN_NAME" \
SYMPHONY_TASK_PLUGIN_INPUT="$PLUGIN_INPUT" \
SYMPHONY_TASK_ISSUES_JSON="$ISSUES_JSON" \
python3 "$ROOT_DIR/scripts/prepare-symphony-payload.py"

cd "$SYMPHONY_ELIXIR_DIR"
"$MISE_BIN" exec -- epmd -daemon || true
SYMPHONY_DAEMON_NODE="$NODE_NAME" \
SYMPHONY_DAEMON_COOKIE="$COOKIE" \
TASK_ISSUES_JSON="$ISSUES_JSON" \
"$MISE_BIN" exec -- mix run "$ROOT_DIR/scripts/enqueue-symphony-memory-issues.exs"
