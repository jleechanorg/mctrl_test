#!/usr/bin/env bash
# Install OpenClaw LaunchAgents from this repo
# Usage: ./scripts/install-launchagents.sh [--mc-token <token>] [--gateway-token <token>]
#
# Installs:
#   - ai.openclaw.gateway             (openclaw gateway, port 18789, via openclaw CLI)
#   - ai.openclaw.startup-check       (startup verification on login)
#   - ai.openclaw.mission-control     (MC backend, port 9010)
#   - ai.openclaw.mission-control-frontend (MC frontend, port 3000)
#
# The MC token is read from ~/.openclaw/openclaw.json if not passed explicitly.
# The gateway token is preserved from the currently installed gateway LaunchAgent
# or may be passed explicitly. This avoids reinstalling the gateway with a stale
# checked-in plist.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_DIR="$REPO_DIR/openclaw-config"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"
OPENCLAW_HOME="$HOME/.openclaw"
ENV_FILE="$REPO_DIR/.env"

is_valid_mc_token() {
  local token="${1:-}"
  [[ -n "$token" ]] && [[ ${#token} -ge 50 ]] && [[ "$token" != "your-local-auth-token-here" ]]
}

read_env_value() {
  local key="$1"
  if [[ -f "$ENV_FILE" ]]; then
    python3 - "$ENV_FILE" "$key" <<'PY'
import pathlib, sys
env_path = pathlib.Path(sys.argv[1])
key = sys.argv[2]
for line in env_path.read_text().splitlines():
    if line.startswith(f"{key}="):
        val = line.split("=", 1)[1]
        # Strip surrounding single or double quotes
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
            val = val[1:-1]
        print(val)
        break
PY
  fi
}

# --- resolve MC token ---
MC_TOKEN="${MC_TOKEN:-${LOCAL_AUTH_TOKEN:-}}"
GATEWAY_TOKEN="${OPENCLAW_GATEWAY_TOKEN:-}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --mc-token) MC_TOKEN="$2"; shift 2 ;;
    --gateway-token) GATEWAY_TOKEN="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if ! is_valid_mc_token "$MC_TOKEN" && [[ -f "$LAUNCHD_DIR/ai.openclaw.mission-control.plist" ]]; then
  MC_TOKEN=$(plutil -extract EnvironmentVariables.LOCAL_AUTH_TOKEN raw \
    -o - "$LAUNCHD_DIR/ai.openclaw.mission-control.plist" 2>/dev/null || true)
fi

if ! is_valid_mc_token "$MC_TOKEN"; then
  MC_TOKEN="$(read_env_value LOCAL_AUTH_TOKEN)"
fi

if ! is_valid_mc_token "$MC_TOKEN"; then
  MC_TOKEN="$(read_env_value MISSION_CONTROL_TOKEN)"
fi

if ! is_valid_mc_token "$MC_TOKEN"; then
  MC_TOKEN=$(python3 - <<'PY'
import json, pathlib
p = pathlib.Path.home()/'.openclaw'/'openclaw.json'
try:
    data = json.loads(p.read_text())
except Exception:
    print("")
else:
    print(data.get('env', {}).get('MISSION_CONTROL_TOKEN', ''))
PY
)
fi

if ! is_valid_mc_token "$MC_TOKEN"; then
  MC_TOKEN=$(python3 - <<'PY'
import secrets
print(secrets.token_hex(32))
PY
)
  echo "Generated new local Mission Control token for launchd services."
fi

echo "MC token: ${MC_TOKEN:0:8}... (${#MC_TOKEN} chars)"

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
  sed \
    -e "s|PLACEHOLDER_MC_TOKEN|$(_esc_sed "$MC_TOKEN")|g" \
    -e "s|@HOME@|$(_esc_sed "$HOME")|g" \
    "$src" > "$dst"

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
install_plist "$CONFIG_DIR/ai.openclaw.mission-control.plist"
install_plist "$CONFIG_DIR/ai.openclaw.mission-control-frontend.plist"
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
echo "  startup check: ~/.openclaw/logs/startup-check.log"
echo "  MC backend:  /tmp/mc-backend.log"
echo "  MC frontend: /tmp/mc-frontend.log"
