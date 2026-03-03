"""Validation tests for committed openclaw JSON configs.

Guards against regressions in security-sensitive config properties:
- discord-eng-bot/openclaw.json (public-facing Discord bot)
- openclaw-config/openclaw.json (main agent profile)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
DISCORD_CONFIG = REPO_ROOT / "discord-eng-bot" / "openclaw.json"
MAIN_CONFIG = REPO_ROOT / "openclaw-config" / "openclaw.json"

CORE_TOOLS = {"read", "write", "edit", "exec", "bash", "process"}
SECOND_OPINION_TOOLS = {
    "second-opinion-tool_agent_second_opinion",
    "second-opinion-tool_rate_limit_status",
    "second-opinion-tool_health-check",
}


@pytest.fixture(scope="module")
def discord_cfg() -> dict:
    return json.loads(DISCORD_CONFIG.read_text())


@pytest.fixture(scope="module")
def main_cfg() -> dict:
    return json.loads(MAIN_CONFIG.read_text())


# ---------------------------------------------------------------------------
# ORCH-o00: sandbox isolation must be preserved in the public Discord bot
# ---------------------------------------------------------------------------


class TestDiscordSandbox:
    def test_sandbox_mode_is_not_off(self, discord_cfg: dict):
        """Public-facing bot must run in an isolated container, not mode='off'."""
        mode = discord_cfg["agents"]["defaults"]["sandbox"]["mode"]
        assert mode != "off", (
            f"sandbox.mode is '{mode}' — should be 'non-main' to keep "
            "Discord sessions in isolated containers (ORCH-o00)"
        )

    def test_sandbox_mode_is_non_main(self, discord_cfg: dict):
        mode = discord_cfg["agents"]["defaults"]["sandbox"]["mode"]
        assert mode == "non-main", (
            f"Expected sandbox.mode='non-main', got '{mode}' (ORCH-o00)"
        )

    def test_workspace_access_is_none(self, discord_cfg: dict):
        """Filesystem access must remain disabled regardless of sandbox mode."""
        access = discord_cfg["agents"]["defaults"]["sandbox"]["workspaceAccess"]
        assert access == "none"


# ---------------------------------------------------------------------------
# ORCH-36x: main config must explicitly list core tools in alsoAllow
# ---------------------------------------------------------------------------


class TestMainCoreTools:
    def test_also_allow_includes_core_tools(self, main_cfg: dict):
        """Core tools must be explicit in alsoAllow so removal from the
        'coding' profile does not silently break the main agent."""
        also_allow = set(main_cfg["tools"].get("alsoAllow", []))
        missing = CORE_TOOLS - also_allow
        assert not missing, (
            f"alsoAllow is missing core tools: {sorted(missing)}. "
            "Do not rely solely on the 'coding' profile to provide them (ORCH-36x)"
        )

    def test_also_allow_includes_second_opinion_tools(self, main_cfg: dict):
        """Second-opinion tool IDs must still be present (regression guard)."""
        also_allow = set(main_cfg["tools"].get("alsoAllow", []))
        missing = SECOND_OPINION_TOOLS - also_allow
        assert not missing, f"alsoAllow missing second-opinion tools: {sorted(missing)}"


# ---------------------------------------------------------------------------
# ORCH-d5b: MCP adapter auth uses dynamic Firebase JWT (not a static header)
#
# Token lifecycle (auth-cli.mjs):
#   - ID token:      1 hour (TOKEN_EXPIRATION_MS = 3600000)
#   - Refresh token: months-long (Firebase Google Sign-In; stored in
#                    ~/.ai-universe/auth-token-ai-universe-b3551.json)
#   - `auth-cli.mjs token` silently exchanges refresh → new ID token when
#     needed; no re-login required for months.
#
# A static ${SECOND_OPINION_MCP_TOKEN} env var would expire after 1 hour.
# The correct fix is a per-request tokenCommand in the adapter config
# (if openclaw-mcp-adapter supports it):
#   "tokenCommand": "node ~/.claude/scripts/auth-cli.mjs token"
#
# These tests verify adapter wiring only — NOT a static Authorization header.
# ---------------------------------------------------------------------------


def _get_mcp_servers(cfg: dict) -> list[dict]:
    return (
        cfg.get("plugins", {})
        .get("entries", {})
        .get("openclaw-mcp-adapter", {})
        .get("config", {})
        .get("servers", [])
    )


class TestMcpAdapterWiring:
    def test_discord_mcp_adapter_has_authorization_header(self, discord_cfg: dict):
        """Adapter must send Authorization header — server requires Firebase JWT Bearer token."""
        servers = _get_mcp_servers(discord_cfg)
        assert servers, "No MCP adapter servers in discord config"
        for server in servers:
            headers = server.get("headers", {})
            assert "Authorization" in headers, (
                f"MCP server '{server.get('name')}' missing Authorization header. "
                "Server requires Bearer token. Set SECOND_OPINION_MCP_TOKEN=$(node "
                "~/.claude/scripts/auth-cli.mjs token) at gateway startup."
            )
            assert "${SECOND_OPINION_MCP_TOKEN}" in headers["Authorization"], (
                "Authorization must use ${SECOND_OPINION_MCP_TOKEN} env var placeholder"
            )

    def test_main_mcp_adapter_has_authorization_header(self, main_cfg: dict):
        servers = _get_mcp_servers(main_cfg)
        assert servers, "No MCP adapter servers in main config"
        for server in servers:
            headers = server.get("headers", {})
            assert "Authorization" in headers, (
                f"MCP server '{server.get('name')}' missing Authorization header (ORCH-d5b)"
            )

    def test_discord_mcp_adapter_enabled(self, discord_cfg: dict):
        adapter = (
            discord_cfg.get("plugins", {})
            .get("entries", {})
            .get("openclaw-mcp-adapter", {})
        )
        assert adapter.get("enabled") is True

    def test_main_mcp_adapter_enabled(self, main_cfg: dict):
        adapter = (
            main_cfg.get("plugins", {})
            .get("entries", {})
            .get("openclaw-mcp-adapter", {})
        )
        assert adapter.get("enabled") is True

    def test_discord_mcp_server_uses_url_env_var(self, discord_cfg: dict):
        servers = _get_mcp_servers(discord_cfg)
        assert servers, "No MCP adapter servers in discord config"
        for server in servers:
            assert "${" in server.get("url", ""), (
                f"MCP server '{server.get('name')}' URL should use an env var "
                "placeholder like '${SECOND_OPINION_MCP_URL}'"
            )

    def test_main_mcp_server_uses_url_env_var(self, main_cfg: dict):
        servers = _get_mcp_servers(main_cfg)
        assert servers, "No MCP adapter servers in main config"
        for server in servers:
            assert "${" in server.get("url", ""), (
                f"MCP server '{server.get('name')}' URL should use an env var "
                "placeholder like '${SECOND_OPINION_MCP_URL}'"
            )

    def test_discord_mcp_tool_prefix_enabled(self, discord_cfg: dict):
        prefix = (
            discord_cfg.get("plugins", {})
            .get("entries", {})
            .get("openclaw-mcp-adapter", {})
            .get("config", {})
            .get("toolPrefix")
        )
        assert prefix is True

    def test_main_mcp_tool_prefix_enabled(self, main_cfg: dict):
        prefix = (
            main_cfg.get("plugins", {})
            .get("entries", {})
            .get("openclaw-mcp-adapter", {})
            .get("config", {})
            .get("toolPrefix")
        )
        assert prefix is True
