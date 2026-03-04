#!/usr/bin/env bash
# Install OpenClaw LaunchAgents from this repo
# Usage: ./scripts/install-launchagents.sh [--mc-token <token>]
#
# Installs:
#   - ai.openclaw.gateway             (openclaw gateway, port 18789)
#   - ai.openclaw.mission-control     (MC backend, port 9010)
#   - ai.openclaw.mission-control-frontend (MC frontend, port 3000)
#   - ai.openclaw.thread-ack-watcher  (Slack missed-mention thread ack backfill)
#
# The MC token is read from ~/.openclaw/openclaw.json if not passed explicitly.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_DIR="$REPO_DIR/openclaw-config"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"

# --- resolve MC token ---
MC_TOKEN="${MC_TOKEN:-}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --mc-token) MC_TOKEN="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if [[ -z "$MC_TOKEN" ]]; then
  MC_TOKEN=$(python3 -c "
import json, sys
try:
    with open('$HOME/.openclaw/openclaw.json') as f:
        cfg = json.load(f)
    print(cfg['env']['MISSION_CONTROL_TOKEN'])
except Exception as e:
    sys.exit(f'Cannot read MC token from ~/.openclaw/openclaw.json: {e}')
")
fi

echo "MC token: ${MC_TOKEN:0:8}... (${#MC_TOKEN} chars)"

# --- install each plist ---
install_plist() {
  local src="$1"
  local label
  label=$(basename "$src" .plist)
  local dst="$LAUNCHD_DIR/$label.plist"

  # unload if already loaded (ignore errors)
  launchctl unload "$dst" 2>/dev/null || true

  # substitute placeholder token if present
  sed "s/PLACEHOLDER_MC_TOKEN/$MC_TOKEN/g" "$src" > "$dst"

  launchctl load "$dst"
  echo "  ✓ $label loaded"
}

echo "Installing LaunchAgents..."
install_plist "$CONFIG_DIR/ai.openclaw.gateway.plist"
install_plist "$CONFIG_DIR/ai.openclaw.mission-control.plist"
install_plist "$CONFIG_DIR/ai.openclaw.mission-control-frontend.plist"
install_plist "$CONFIG_DIR/ai.openclaw.thread-ack-watcher.plist"

echo ""
echo "Verifying..."
sleep 3
for port in 18789 9010 3000; do
  if lsof -i ":$port" 2>/dev/null | grep -q LISTEN; then
    echo "  ✓ port $port listening"
  else
    echo "  ✗ port $port NOT listening — check logs"
  fi
done

echo ""
echo "Log locations:"
echo "  gateway:  ~/.openclaw/logs/gateway.log"
echo "  MC backend:  /tmp/mc-backend.log"
echo "  MC frontend: /tmp/mc-frontend.log"
echo "  thread ack watcher: ~/.openclaw/logs/thread-ack-watcher.log"
