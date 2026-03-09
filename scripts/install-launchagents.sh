#!/usr/bin/env bash
# Install OpenClaw LaunchAgents from this repo
# Usage: ./scripts/install-launchagents.sh [--gateway-token <token>]
#
# Installs:
#   - ai.openclaw.gateway             (openclaw gateway, port 18789, via openclaw CLI)
#   - ai.openclaw.startup-check       (startup verification on login)
# The gateway token is preserved from the currently installed gateway LaunchAgent
# or may be passed explicitly. This avoids reinstalling the gateway with a stale
# checked-in plist.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_DIR="$REPO_DIR/openclaw-config"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"
OPENCLAW_HOME="$HOME/.openclaw"
GATEWAY_TOKEN="${OPENCLAW_GATEWAY_TOKEN:-}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --gateway-token) GATEWAY_TOKEN="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

# --- preserve existing gateway token if available ---
if [[ -z "$GATEWAY_TOKEN" && -f "$LAUNCHD_DIR/ai.openclaw.gateway.plist" ]]; then
  GATEWAY_TOKEN=$(plutil -extract EnvironmentVariables.OPENCLAW_GATEWAY_TOKEN raw \
    -o - "$LAUNCHD_DIR/ai.openclaw.gateway.plist" 2>/dev/null || true)
fi

# --- install startup helper + plists ---
install_startup_check_script() {
  install -d "$OPENCLAW_HOME"
  mkdir -p "$OPENCLAW_HOME/logs"
  install -m 755 "$CONFIG_DIR/startup-check.sh" "$OPENCLAW_HOME/startup-check.sh"
  echo "  ✓ startup-check.sh installed"
}

_esc_sed() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/&/\\&/g; s/|/\\|/g'; }

install_plist() {
  local src="$1"
  local label
  label=$(basename "$src" .plist)
  local dst="$LAUNCHD_DIR/$label.plist"

  mkdir -p "$LAUNCHD_DIR"
  sed -e "s|@HOME@|$(_esc_sed "$HOME")|g" "$src" > "$dst"

  if ! launchctl bootstrap "gui/$(id -u)" "$dst" 2>/dev/null; then
    launchctl bootout "gui/$(id -u)" "$dst" 2>/dev/null || true
    launchctl bootstrap "gui/$(id -u)" "$dst"
  fi
  echo "  ✓ $label loaded"
}

echo "Installing LaunchAgents..."
if [[ -n "$GATEWAY_TOKEN" && ${#GATEWAY_TOKEN} -ge 20 ]]; then
  openclaw gateway install --force --port 18789 --token "$GATEWAY_TOKEN" >/dev/null
  echo "  ✓ ai.openclaw.gateway installed via openclaw gateway install"
else
  echo "  ✗ Could not determine gateway token; refusing to reinstall ai.openclaw.gateway"
  exit 1
fi
install_startup_check_script
install_plist "$CONFIG_DIR/ai.openclaw.startup-check.plist"
echo ""
echo "Verifying..."
sleep 3
for port in 18789; do
  if lsof -i ":$port" 2>/dev/null | grep -q LISTEN; then
    echo "  ✓ port $port listening"
  else
    echo "  ✗ port $port NOT listening — check logs"
  fi
done

echo ""
echo "Log locations:"
echo "  gateway:  ~/.openclaw/logs/gateway.log"
echo "  startup check: ~/.openclaw/logs/startup-check.log"
