#!/usr/bin/env bash
set -euo pipefail

ROOT="${OPENCLAW_ROOT:-$HOME/.openclaw}"
CTX="$ROOT/docs/context"
SNAP="$CTX/SYSTEM_SNAPSHOT.md"
GAPS="$CTX/DOC_GAPS.md"

mkdir -p "$CTX"

{
  echo "# System Snapshot"
  echo
  echo "Generated: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
  echo
  echo "## OpenClaw version"
  openclaw --version || true
  echo
  echo "## Gateway status"
  openclaw status || true
  echo
  echo "## Cron jobs"
  openclaw cron list --json || true
  echo
  echo "## Diagnostics flags"
  openclaw config get diagnostics.flags || true
} > "$SNAP"

missing=0
: > "$GAPS"
echo "# Documentation Gap Report" >> "$GAPS"
echo >> "$GAPS"
echo "Generated: $(date -u '+%Y-%m-%d %H:%M:%S UTC')" >> "$GAPS"
echo >> "$GAPS"

for f in PRODUCT.md WORKFLOWS.md FILE_MAP.md LEARNINGS.md PROMPTING_GUIDES.md; do
  if [[ ! -s "$CTX/$f" ]]; then
    echo "- Missing or empty: docs/context/$f" >> "$GAPS"
    missing=1
  fi
done

if [[ $missing -eq 0 ]]; then
  echo "- No required doc gaps detected." >> "$GAPS"
fi

echo "Wrote: $SNAP"
echo "Wrote: $GAPS"
