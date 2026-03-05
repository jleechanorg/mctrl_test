#!/usr/bin/env bash
# mc-health-check.sh — verify all Mission Control services are healthy.
# Exits 0 if healthy, 1 if any check fails.
set -euo pipefail

PASS=0
FAIL=0

check() {
  local label="$1"
  local ok="$2"
  if [ "$ok" = "1" ]; then
    echo "✅ $label"
    PASS=$((PASS+1))
  else
    echo "❌ $label"
    FAIL=$((FAIL+1))
  fi
}

# --- ports ---
for port in 18789 9010 3000; do
  listening=$(lsof -i ":$port" 2>/dev/null | grep -c LISTEN || true)
  check "port :$port listening" "$([[ $listening -gt 0 ]] && echo 1 || echo 0)"
done

# --- MC health endpoint ---
mc_health=$(curl -sf http://localhost:9010/health 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(1 if d.get('ok') else 0)" 2>/dev/null || echo 0)
check "MC backend /health ok" "$mc_health"

# --- MC agents registered ---
_mc_token=$(python3 -c "import json; cfg=json.load(open('$HOME/.openclaw/openclaw.json')); print(cfg.get('env',{}).get('MISSION_CONTROL_TOKEN',''))" 2>/dev/null || echo "")
_auth_header=()
if [[ -n "${_mc_token}" ]]; then
  _auth_header=(-H "Authorization: Bearer ${_mc_token}")
fi
mc_agents=$(curl -sf http://localhost:9010/api/v1/agents \
  ${_auth_header[@]+"${_auth_header[@]}"} 2>/dev/null | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(1 if len(d.get('items',[])) > 0 else 0)" 2>/dev/null || echo 0)
check "MC agents registered (heartbeat)" "$mc_agents"

# --- task poller running ---
poller_running=$(launchctl list ai.openclaw.task-poller 2>/dev/null | grep -c "PID" || true)
check "task-poller LaunchAgent loaded" "$([[ $poller_running -gt 0 ]] && echo 1 || echo 0)"

# --- inbox tasks with no agents (zombie state) ---
inbox_count=$(curl -sf "http://localhost:9010/api/v1/tasks?status=inbox" \
  ${_auth_header[@]+"${_auth_header[@]}"} 2>/dev/null | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('items',[])))" 2>/dev/null || echo 0)
if [[ "$inbox_count" -gt 0 && "$mc_agents" == "0" ]]; then
  echo "⚠️  ZOMBIE STATE: $inbox_count inbox tasks but 0 agents registered"
  FAIL=$((FAIL+1))
elif [[ "$inbox_count" -gt 0 ]]; then
  echo "ℹ️  $inbox_count tasks in inbox"
fi

echo ""
echo "Result: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
