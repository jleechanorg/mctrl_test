#!/usr/bin/env bash
# install-mc-task-poller.sh — Install the Mission Control task poller LaunchAgent.
# Reads token + board ID from ~/.openclaw/openclaw.json.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PLIST_SRC="$REPO_ROOT/openclaw-config/ai.openclaw.task-poller.plist"
PLIST_DST="$HOME/Library/LaunchAgents/ai.openclaw.task-poller.plist"

# --- resolve credentials from openclaw.json ---
read_env() {
  python3 -c "
import json, sys
try:
    with open('$HOME/.openclaw/openclaw.json') as f:
        cfg = json.load(f)
    env = cfg.get('env', {})
    key = sys.argv[1]
    val = env.get(key)
    if not val:
        sys.exit(f'ERROR: {key} not set in ~/.openclaw/openclaw.json env')
    print(val)
except Exception as e:
    sys.exit(str(e))
" "$1"
}

MC_TOKEN=$(read_env MISSION_CONTROL_TOKEN)
BOARD_ID=$(read_env MISSION_CONTROL_BOARD_ID)

echo "Board ID: ${BOARD_ID}"
echo "Token:    ${MC_TOKEN:0:8}... (${#MC_TOKEN} chars)"

# --- unload existing if present ---
launchctl unload "$PLIST_DST" 2>/dev/null || true

# --- substitute placeholders ---
sed -e "s/PLACEHOLDER_MC_TOKEN/$MC_TOKEN/g" \
    -e "s/PLACEHOLDER_BOARD_ID/$BOARD_ID/g" \
    "$PLIST_SRC" > "$PLIST_DST"

launchctl load "$PLIST_DST"
echo "✅ ai.openclaw.task-poller loaded"
echo "   Log: /tmp/mc-task-poller.log"
echo "   Err: /tmp/mc-task-poller.err.log"

sleep 3
bash "$SCRIPT_DIR/mc-health-check.sh"
