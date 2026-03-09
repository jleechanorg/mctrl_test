#!/usr/bin/env bash
set -euo pipefail

REPOS=(
  "$HOME/projects/worldarchitect.ai"
  "$HOME/project_jleechanclaw/jleechanclaw"
  "$HOME/project_worldaiclaw/worldai_claw"
)

echo "=== Genesis Memory L0 validation (dry-run pipeline) ==="
echo
echo "[1/3] seed_memory dry-run over rolling window"
python3 scripts/seed_memory.py \
  --since "8 days ago" \
  --until now \
  --repo "${REPOS[0]}" \
  --repo "${REPOS[1]}" \
  --repo "${REPOS[2]}" \
  --dry-run

echo
echo "[2/3] extract_patterns dry-run over last 7 days"
python3 scripts/extract_patterns.py \
  --days 7 \
  --repo "${REPOS[0]}" \
  --repo "${REPOS[1]}" \
  --repo "${REPOS[2]}" \
  --dry-run

echo
echo "[3/3] OpenClaw retrieval smoke check"
if ! command -v openclaw >/dev/null; then
  echo "SKIP: openclaw CLI not installed in PATH."
  exit 0
fi

if openclaw memory search "what did Jeffrey work on in week 38 of 2025?" >/tmp/openclaw-genesis-l0-check.log 2>/tmp/openclaw-genesis-l0-check.err; then
  echo "OK: openclaw memory search executed."
  if [[ -s /tmp/openclaw-genesis-l0-check.log ]]; then
    echo "--- sample output ---"
    head -n 20 /tmp/openclaw-genesis-l0-check.log
  else
    echo "WARN: command returned no output; manual follow-up may be needed."
  fi
else
  echo "WARN: openclaw memory search command failed. Check logs:"
  cat /tmp/openclaw-genesis-l0-check.err
fi

echo
echo "Validation script complete. Use output above to confirm L0 answer quality."
