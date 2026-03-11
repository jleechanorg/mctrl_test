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

detect_local_timezone() {
  local target
  target="$(readlink /etc/localtime 2>/dev/null || true)"
  if [[ "$target" == *"/zoneinfo/"* ]]; then
    echo "${target##*/zoneinfo/}"
    return 0
  fi
  echo "${TZ:-unknown}"
}

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
    --mc-token)
      if [[ $# -lt 2 || -z "$2" || "$2" == --* ]]; then
        echo "Error: --mc-token requires a non-empty value" >&2
        exit 1
      fi
      MC_TOKEN="$2"
      shift 2
      ;;
    --gateway-token)
      if [[ $# -lt 2 || -z "$2" || "$2" == --* ]]; then
        echo "Error: --gateway-token requires a non-empty value" >&2
        exit 1
      fi
      GATEWAY_TOKEN="$2"
      shift 2
      ;;
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
  install -m 755 "$CONFIG_DIR/run-scheduled-job.sh" "$OPENCLAW_HOME/run-scheduled-job.sh"
  mkdir -p "$OPENCLAW_HOME/logs/scheduled-jobs"
  echo "  ✓ startup-check.sh installed"
  echo "  ✓ run-scheduled-job.sh installed"
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
  # openclaw gateway install doesn't add token to launchd env vars - fix that
  PLIST="$LAUNCHD_DIR/ai.openclaw.gateway.plist"
  if [[ -f "$PLIST" ]]; then
    # Ensure EnvironmentVariables exists, then set token idempotently.
    if ! /usr/libexec/PlistBuddy -c "Print :EnvironmentVariables" "$PLIST" >/dev/null 2>&1; then
      /usr/libexec/PlistBuddy -c "Add :EnvironmentVariables dict" "$PLIST"
    fi
    if ! plutil -replace EnvironmentVariables.OPENCLAW_GATEWAY_TOKEN -string "$GATEWAY_TOKEN" "$PLIST" 2>/dev/null; then
      plutil -insert EnvironmentVariables.OPENCLAW_GATEWAY_TOKEN -string "$GATEWAY_TOKEN" "$PLIST"
    fi
    # Restart to pick up new env var
    launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
    launchctl bootstrap "gui/$(id -u)" "$PLIST"
  fi
  echo "  ✓ ai.openclaw.gateway installed via openclaw gateway install"
else
  echo "  ✗ Could not determine gateway token; refusing to reinstall ai.openclaw.gateway"
  exit 1
fi
install_startup_check_script
install_plist "$CONFIG_DIR/ai.openclaw.startup-check.plist"
SCHEDULE_INSTALLER="$REPO_DIR/scripts/install-openclaw-scheduled-jobs.sh"
if [[ -x "$SCHEDULE_INSTALLER" ]]; then
  LOCAL_TZ="$(detect_local_timezone)"
  if [[ "$LOCAL_TZ" != "America/Los_Angeles" && "${OPENCLAW_ALLOW_NON_PT_SCHEDULE:-0}" != "1" ]]; then
    echo "  • skipping scheduled job migration: local timezone '$LOCAL_TZ' differs from America/Los_Angeles"
    echo "    set OPENCLAW_ALLOW_NON_PT_SCHEDULE=1 to override"
  else
    "$SCHEDULE_INSTALLER"
  fi
else
  echo "  • skipping scheduled job migration (installer not found: $SCHEDULE_INSTALLER)"
fi
MC_BACKEND_PLIST="$CONFIG_DIR/ai.openclaw.mission-control.plist"
MC_FRONTEND_PLIST="$CONFIG_DIR/ai.openclaw.mission-control-frontend.plist"
if [[ -f "$MC_BACKEND_PLIST" ]]; then
  install_plist "$MC_BACKEND_PLIST"
else
  echo "  • skipping ai.openclaw.mission-control (plist not found in openclaw-config/)"
fi
if [[ -f "$MC_FRONTEND_PLIST" ]]; then
  install_plist "$MC_FRONTEND_PLIST"
else
  echo "  • skipping ai.openclaw.mission-control-frontend (plist not found in openclaw-config/)"
fi
echo ""
echo "Verifying..."
sleep 3
PORTS=(18789)
[[ -f "$MC_BACKEND_PLIST" ]] && PORTS+=(9010)
[[ -f "$MC_FRONTEND_PLIST" ]] && PORTS+=(3000)
for port in "${PORTS[@]}"; do
  if lsof -i ":$port" 2>/dev/null | grep -q LISTEN; then
    echo "  ✓ port $port listening"
  else
    echo "  ✗ port $port NOT listening — check logs"
  fi
done

echo ""
echo "Verifying launchd labels..."
EXPECTED_LABELS=("ai.openclaw.gateway" "ai.openclaw.startup-check")
for plist in "$CONFIG_DIR"/ai.openclaw.schedule.*.plist; do
  [[ -f "$plist" ]] || continue
  EXPECTED_LABELS+=("$(basename "$plist" .plist)")
done
[[ -f "$MC_BACKEND_PLIST" ]] && EXPECTED_LABELS+=("ai.openclaw.mission-control")
[[ -f "$MC_FRONTEND_PLIST" ]] && EXPECTED_LABELS+=("ai.openclaw.mission-control-frontend")

for label in "${EXPECTED_LABELS[@]}"; do
  if launchctl print "gui/$(id -u)/$label" >/dev/null 2>&1; then
    echo "  ✓ $label registered"
  else
    echo "  ✗ $label NOT registered"
  fi
done

echo ""
echo "Log locations:"
echo "  gateway:  ~/.openclaw/logs/gateway.log"
echo "  startup check: ~/.openclaw/logs/startup-check.log"
echo "  MC backend:  /tmp/mc-backend.log"
echo "  MC frontend: /tmp/mc-frontend.log"
