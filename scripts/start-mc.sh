#!/bin/bash
# Start Mission Control backend (native Postgres on port 9010)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Postgres: brew services start postgresql@16
/opt/homebrew/bin/brew services start postgresql@16 2>/dev/null

# Ensure mission_control DB + postgres user exist
/opt/homebrew/opt/postgresql@16/bin/createdb mission_control 2>/dev/null || true
/opt/homebrew/opt/postgresql@16/bin/psql -U jleechan postgres -c "CREATE USER postgres WITH SUPERUSER PASSWORD 'postgres';" 2>/dev/null || true
/opt/homebrew/opt/postgresql@16/bin/psql -U jleechan postgres -c "GRANT ALL ON DATABASE mission_control TO postgres;" 2>/dev/null || true

# Start MC backend
pkill -f "uvicorn app.main" 2>/dev/null; sleep 1
cd ~/projects_reference/openclaw-mission-control/backend
DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/mission_control" \
  AUTH_MODE="local" \
  LOCAL_AUTH_TOKEN="${LOCAL_AUTH_TOKEN:-$(grep '^LOCAL_AUTH_TOKEN=' "$SCRIPT_DIR/../.env" 2>/dev/null | cut -d= -f2-)}" \
  nohup uv run --python 3.12 uvicorn app.main:app --host 0.0.0.0 --port 9010 > /tmp/mc-backend.log 2>&1 &
echo "MC backend started (port 9010)"
