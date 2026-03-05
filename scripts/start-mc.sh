#!/bin/bash
# Start Mission Control backend (native Postgres on port 9010)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$REPO_ROOT/.env"
DEFAULT_BOARD_ID="aa68f729-d5e0-4d44-8c99-51bcebc0b8bc"
# Postgres: brew services start postgresql@16
/opt/homebrew/bin/brew services start postgresql@16 2>/dev/null

# Ensure mission_control DB + postgres user exist
/opt/homebrew/opt/postgresql@16/bin/createdb mission_control 2>/dev/null || true
/opt/homebrew/opt/postgresql@16/bin/psql -U jleechan postgres -c "CREATE USER postgres WITH SUPERUSER PASSWORD 'postgres';" 2>/dev/null || true
/opt/homebrew/opt/postgresql@16/bin/psql -U jleechan postgres -c "GRANT ALL ON DATABASE mission_control TO postgres;" 2>/dev/null || true

LOCAL_AUTH_TOKEN_VALUE="${LOCAL_AUTH_TOKEN:-$(grep '^LOCAL_AUTH_TOKEN=' "$ENV_FILE" 2>/dev/null | cut -d= -f2-)}"
BOARD_ID_VALUE="${MISSION_CONTROL_BOARD_ID:-$(grep '^MISSION_CONTROL_BOARD_ID=' "$ENV_FILE" 2>/dev/null | cut -d= -f2-)}"
if [ -z "$BOARD_ID_VALUE" ]; then
  BOARD_ID_VALUE="$DEFAULT_BOARD_ID"
fi

# Start MC backend
pkill -f "orchestration.mc_backend_service" 2>/dev/null || true
pkill -f "uvicorn app.main" 2>/dev/null || true
sleep 1
cd ~/projects_reference/openclaw-mission-control/backend
DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/mission_control" \
  AUTH_MODE="local" \
  LOCAL_AUTH_TOKEN="$LOCAL_AUTH_TOKEN_VALUE" \
  MISSION_CONTROL_BASE_URL="http://127.0.0.1:9010" \
  MISSION_CONTROL_TOKEN="$LOCAL_AUTH_TOKEN_VALUE" \
  MISSION_CONTROL_BOARD_ID="$BOARD_ID_VALUE" \
  MISSION_CONTROL_IN_PROCESS_POLLER="${MISSION_CONTROL_IN_PROCESS_POLLER:-1}" \
  PYTHONPATH="$REPO_ROOT/src:${PYTHONPATH:-}" \
  nohup uv run --python 3.12 python -m orchestration.mc_backend_service --app app.main:app --host 0.0.0.0 --port 9010 > /tmp/mc-backend.log 2>&1 &
echo "MC backend started (port 9010)"
