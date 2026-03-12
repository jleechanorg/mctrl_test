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

# Redact secrets and machine-specific values in committed backup config files.
python3 - <<'PY'
import json
import re
from pathlib import Path

dest = Path("openclaw-config")
cfg_path = dest / "openclaw.json"
if cfg_path.exists():
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    # Normalize mem0 history DB path to portable HOME placeholder.
    try:
        cfg["plugins"]["entries"]["openclaw-mem0"]["config"]["oss"]["historyDbPath"] = "${HOME}/.openclaw/mem0-history.db"
    except Exception:
        pass
    try:
        cfg["plugins"]["config"]["openclaw-mem0"]["config"]["oss"]["historyDbPath"] = "${HOME}/.openclaw/mem0-history.db"
    except Exception:
        pass

    # Keep regression-guarded tool allowlist entries present even if live
    # config drifted (for Slack MCP + second-opinion integrations).
    tools = cfg.setdefault("tools", {})
    also_allow = tools.setdefault("alsoAllow", [])
    required_tools = [
        "second-opinion-tool_agent_second_opinion",
        "second-opinion-tool_rate_limit_status",
        "second-opinion-tool_health-check",
        "slack-mcp_channels_list",
        "slack-mcp_conversations_add_message",
        "slack-mcp_conversations_history",
        "slack-mcp_conversations_mark",
        "slack-mcp_conversations_replies",
        "slack-mcp_usergroups_create",
        "slack-mcp_usergroups_list",
        "slack-mcp_usergroups_me",
        "slack-mcp_usergroups_update",
        "slack-mcp_usergroups_users_update",
        "slack-mcp_users_search",
    ]
    for tool in required_tools:
        if tool not in also_allow:
            also_allow.append(tool)

    # Normalize MCP adapter placeholders and server IDs.
    servers = (
        cfg.setdefault("plugins", {})
        .setdefault("entries", {})
        .setdefault("openclaw-mcp-adapter", {})
        .setdefault("config", {})
        .setdefault("servers", [])
    )
    for server in servers:
        if server.get("name") == "mcp-agent-mail" and str(server.get("transport", "http")).lower() == "http":
            server["url"] = "${MCP_AGENT_MAIL_URL}"
            headers = server.setdefault("headers", {})
            headers["Authorization"] = "Bearer ${MCP_AGENT_MAIL_TOKEN}"
        if server.get("name") == "slack":
            server["name"] = "slack-mcp"

    def walk(node):
        if isinstance(node, dict):
            for k, v in list(node.items()):
                if isinstance(v, str):
                    if re.search(r"xoxb-[A-Za-z0-9-]+", v):
                        node[k] = "${OPENCLAW_SLACK_BOT_TOKEN}"
                    elif re.search(r"xai-[A-Za-z0-9_-]+", v):
                        node[k] = "${XAI_API_KEY}"
                else:
                    walk(v)
        elif isinstance(node, list):
            for i in node:
                walk(i)

    walk(cfg)
    cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")

for plist in (dest / "launchd").glob("*.plist"):
    text = plist.read_text(encoding="utf-8", errors="ignore")
    text = re.sub(r"xoxb-[A-Za-z0-9-]+", "${OPENCLAW_SLACK_BOT_TOKEN}", text)
    text = re.sub(r"xai-[A-Za-z0-9_-]+", "${XAI_API_KEY}", text)
    plist.write_text(text, encoding="utf-8")
PY

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
