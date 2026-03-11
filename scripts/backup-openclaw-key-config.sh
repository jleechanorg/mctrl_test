#!/usr/bin/env bash
set -euo pipefail

# Backup key OpenClaw config/docs from ~/.openclaw into repo openclaw-config/
# This is intentionally curated (not a full mirror).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC_DIR="${HOME}/.openclaw"
DEST_DIR="$REPO_ROOT/openclaw-config"

if [ ! -d "$SRC_DIR" ]; then
  echo "Source not found: $SRC_DIR" >&2
  exit 1
fi

mkdir -p "$DEST_DIR"
mkdir -p "$DEST_DIR/agents/main/agent"
mkdir -p "$DEST_DIR/agents/monitor/agent"
mkdir -p "$DEST_DIR/workspaces/monitor/.openclaw"
mkdir -p "$DEST_DIR/launchd"

copy_if_exists() {
  local src="$1"
  local dst="$2"
  if [ -e "$src" ]; then
    mkdir -p "$(dirname "$dst")"
    # Dereference source symlinks so backups contain concrete file contents.
    cp -fL "$src" "$dst"
    echo "copied: ${src#$SRC_DIR/}"
  else
    echo "skip:   ${src#$SRC_DIR/} (missing)"
  fi
}

# Core config + docs
for f in \
  openclaw.json \
  AUTO_START_GUIDE.md BACKUP_AND_RESTORE.md HEARTBEAT.md IDENTITY.md \
  SLACK_SETUP_GUIDE.md SOUL.md TOOLS.md USER.md security-policy.md update-check.json \
  health-check.sh monitor-agent.sh startup-check.sh enable-auto-backup.sh \
  run-scheduled-job.sh set-slack-env.sh slack-setup.sh \
  ai.openclaw.gateway.plist ai.openclaw.health-check.plist ai.openclaw.monitor-agent.plist
  do
  copy_if_exists "$SRC_DIR/$f" "$DEST_DIR/$f"
done

# Keep launchd plists grouped too
for f in ai.openclaw.gateway.plist ai.openclaw.health-check.plist ai.openclaw.monitor-agent.plist; do
  copy_if_exists "$SRC_DIR/../Library/LaunchAgents/$f" "$DEST_DIR/launchd/$f"
done

# Agent metadata/state indexes (no heavy session logs)
copy_if_exists "$SRC_DIR/agents/main/agent/models.json" "$DEST_DIR/agents/main/agent/models.json"
copy_if_exists "$SRC_DIR/agents/main/agent/auth-profiles.json" "$DEST_DIR/agents/main/agent/auth-profiles.json"
copy_if_exists "$SRC_DIR/agents/monitor/agent/models.json" "$DEST_DIR/agents/monitor/agent/models.json"
copy_if_exists "$SRC_DIR/agents/monitor/agent/auth-profiles.json" "$DEST_DIR/agents/monitor/agent/auth-profiles.json"

# Dedicated monitor workspace docs/state
for f in AGENTS.md SOUL.md TOOLS.md IDENTITY.md USER.md HEARTBEAT.md BOOTSTRAP.md; do
  copy_if_exists "$SRC_DIR/workspace-monitor/$f" "$DEST_DIR/workspaces/monitor/$f"
done
copy_if_exists "$SRC_DIR/workspace-monitor/.openclaw/workspace-state.json" "$DEST_DIR/workspaces/monitor/.openclaw/workspace-state.json"

# Do not keep accidental VCS internals from workspace snapshots
rm -rf "$DEST_DIR/workspaces/monitor/.git" 2>/dev/null || true

# Store redacted auth profile snapshots for repo tracking.
if command -v jq >/dev/null 2>&1; then
  for agent in main monitor; do
    raw="$DEST_DIR/agents/$agent/agent/auth-profiles.json"
    redacted="$DEST_DIR/agents/$agent/agent/auth-profiles.redacted.json"
    if [ -f "$raw" ]; then
      jq '{
            version: (.version // null),
            lastGood: (.lastGood // null),
            profiles: ((.profiles // {})
              | with_entries(.value = {
                  provider: (.value.provider // null),
                  mode: (.value.mode // null),
                  hasApiKey: (.value.apiKey? != null),
                  hasAccessToken: (.value.accessToken? != null),
                  hasRefreshToken: (.value.refreshToken? != null)
                })),
            usageStatsKeys: ((.usageStats // {}) | keys)
          }' "$raw" > "$redacted" || true
      echo "redacted: agents/$agent/agent/auth-profiles.redacted.json"
    fi
  done
fi

echo "Done. Backup refreshed in $DEST_DIR"
