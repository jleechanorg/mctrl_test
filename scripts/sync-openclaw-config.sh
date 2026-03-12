#!/usr/bin/env bash
# Sync files FROM this repo's openclaw-config/ TO live ~/.openclaw/
# Analyzes differences first and alerts on unexpected changes.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_CONFIG="$REPO_ROOT/openclaw-config"
LIVE_DIR="${HOME}/.openclaw"
BACKUP_SCRIPT="$REPO_ROOT/scripts/backup-openclaw-key-config.sh"

# Directories to sync (from repo to live)
SYNC_DIRS="${SYNC_DIRS:-skills}"

# Color codes
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "=== OpenClaw Config Sync Analyzer ==="
echo "Repo:   $REPO_CONFIG"
echo "Live:   $LIVE_DIR"
echo "Sync:   $SYNC_DIRS"
echo ""

REFRESH_BACKUP="${OPENCLAW_SYNC_REFRESH_BACKUP:-1}"
if [ "$REFRESH_BACKUP" = "1" ]; then
  echo "--- Pre-sync Backup Refresh ---"
  if [ -x "$BACKUP_SCRIPT" ]; then
    "$BACKUP_SCRIPT"
    echo ""
  else
    echo -e "  ${YELLOW}WARN:${NC} backup script not executable/missing: $BACKUP_SCRIPT"
    echo ""
  fi
else
  echo "--- Pre-sync Backup Refresh ---"
  echo "  Skipped (OPENCLAW_SYNC_REFRESH_BACKUP=$REFRESH_BACKUP)"
  echo ""
fi

# Check for skills in repo that aren't installed in live
echo "--- Skills Check ---"
if [ -d "$REPO_CONFIG/skills" ]; then
  REPO_SKILLS=$(ls -d "$REPO_CONFIG/skills"/*/ 2>/dev/null | xargs -n1 basename 2>/dev/null | sort)
  LIVE_SKILLS=$(ls -d "$LIVE_DIR/skills"/*/ 2>/dev/null | xargs -n1 basename 2>/dev/null | sort || echo "")

  echo "  Repo skills: $REPO_SKILLS"
  echo "  Live skills:  $LIVE_SKILLS"
  echo ""

  MISSING_LIVE=$(comm -23 <(echo "$REPO_SKILLS") <(echo "$LIVE_SKILLS"))
  if [ -n "$MISSING_LIVE" ]; then
    echo -e "  ${YELLOW}MISSING IN LIVE:${NC} $MISSING_LIVE"
    echo ""
  else
    echo -e "  ${GREEN}OK:${NC} all repo skills installed in live"
    echo ""
  fi
fi

# Check skills directory for diffs
echo "--- Skills Directory Diff ---"
for dir in $SYNC_DIRS; do
  REPO_SUBDIR="$REPO_CONFIG/$dir"
  LIVE_SUBDIR="$LIVE_DIR/$dir"

  if [ ! -d "$REPO_SUBDIR" ]; then
    continue
  fi

  if [ "${1:-}" = "--execute" ]; then
    mkdir -p "$LIVE_SUBDIR"
  fi

  # Find new or modified files in repo
  echo "  Checking $dir/ for new/modified files..."
  SYNC_NEEDED=0
  while IFS= read -r rel_file; do
    REPO_FILE="$REPO_SUBDIR/$rel_file"
    LIVE_FILE="$LIVE_SUBDIR/$rel_file"

    if [ ! -f "$LIVE_FILE" ]; then
      echo -e "    ${GREEN}+ NEW:${NC} $rel_file"
      SYNC_NEEDED=1
    elif ! diff -q "$REPO_FILE" "$LIVE_FILE" > /dev/null 2>&1; then
      echo -e "    ${YELLOW}~ MODIFIED:${NC} $rel_file"
      SYNC_NEEDED=1
    fi
  done < <(find "$REPO_SUBDIR" -type f \( -name "*.json" -o -name "*.md" -o -name "*.sh" -o -name "*.yaml" -o -name "*.yml" \) | sed "s|$REPO_SUBDIR/||" | sort)

  if [ "$SYNC_NEEDED" = "0" ]; then
    echo -e "    ${GREEN}(all synced)${NC}"
  fi
  echo ""
done

# Summary
echo "=== Ready ==="
echo "Run with --execute to sync:"
echo "  ./scripts/sync-openclaw-config.sh --execute"
echo ""

if [ "${1:-}" = "--execute" ]; then
  echo "Executing sync..."

  for dir in $SYNC_DIRS; do
    REPO_SUBDIR="$REPO_CONFIG/$dir"
    LIVE_SUBDIR="$LIVE_DIR/$dir"

    if [ -d "$REPO_SUBDIR" ]; then
      echo "  Syncing $dir/..."
      rsync -a --delete \
        --exclude='.git' \
        --exclude='.DS_Store' \
        "$REPO_SUBDIR/" "$LIVE_SUBDIR/"
    fi
  done

  echo ""
  echo -e "${GREEN}Sync complete.${NC}"
  echo "Reload OpenClaw: kill -HUP \$(pgrep -f openclaw-gateway)"
else
  echo "(dry run - no changes made)"
fi
