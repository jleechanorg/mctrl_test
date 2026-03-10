"""Validation tests for committed openclaw JSON configs.

Guards against regressions in security-sensitive config properties:
- discord-eng-bot/openclaw.json (public-facing Discord bot)
- openclaw-config/openclaw.json (main agent profile)
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DISCORD_CONFIG = REPO_ROOT / "discord-eng-bot" / "openclaw.json"
MAIN_CONFIG = REPO_ROOT / "openclaw-config" / "openclaw.json"
MC_PLIST = REPO_ROOT / "openclaw-config" / "ai.openclaw.mission-control.plist"
START_MC_SCRIPT = REPO_ROOT / "scripts" / "start-mc.sh"
GATEWAY_INSTALL_SCRIPT = REPO_ROOT / "scripts" / "install-launchagents.sh"
STARTUP_CHECK_PLIST = REPO_ROOT / "openclaw-config" / "ai.openclaw.startup-check.plist"
STARTUP_CHECK_SCRIPT = REPO_ROOT / "openclaw-config" / "startup-check.sh"
MCTRL_SUPERVISOR_PLIST = REPO_ROOT / "scripts" / "mctrl-supervisor.plist.template"

CORE_TOOLS = {"read", "write", "edit", "exec", "bash", "process"}
SECOND_OPINION_TOOLS = {
    "second-opinion-tool_agent_second_opinion",
    "second-opinion-tool_rate_limit_status",
    "second-opinion-tool_health-check",
}
SLACK_MCP_TOOLS = {
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


def _server_transport(server: dict) -> str:
    return str(server.get("transport") or "http").strip().lower()


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
            if _server_transport(server) != "http":
                continue
            headers = server.get("headers", {})
            assert "Authorization" in headers, (
                f"HTTP MCP server '{server.get('name')}' missing Authorization header (ORCH-d5b)"
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
            if _server_transport(server) != "http":
                continue
            assert "${" in server.get("url", ""), (
                f"HTTP MCP server '{server.get('name')}' URL should use an env var "
                "placeholder like '${SECOND_OPINION_MCP_URL}'"
            )

    def test_main_stdio_mcp_servers_define_command(self, main_cfg: dict):
        servers = _get_mcp_servers(main_cfg)
        for server in servers:
            if _server_transport(server) != "stdio":
                continue
            command = str(server.get("command") or "").strip()
            assert command, f"MCP server '{server.get('name')}' with transport=stdio must define command"

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


class TestInstallLaunchagentsScript:
    @pytest.mark.parametrize(
        ("flag", "expected_error"),
        [
            ("--mc-token", "Error: --mc-token requires a non-empty value"),
            ("--gateway-token", "Error: --gateway-token requires a non-empty value"),
        ],
    )
    def test_missing_option_value_exits_cleanly(self, flag: str, expected_error: str):
        result = subprocess.run(
            [str(GATEWAY_INSTALL_SCRIPT), flag],
            capture_output=True,
            text=True,
            env={"HOME": str(REPO_ROOT)},
        )

        assert result.returncode != 0
        assert expected_error in result.stderr

    @pytest.mark.parametrize(
        ("flag", "expected_error"),
        [
            ("--mc-token", "Error: --mc-token requires a non-empty value"),
            ("--gateway-token", "Error: --gateway-token requires a non-empty value"),
        ],
    )
    def test_empty_option_value_exits_cleanly(self, flag: str, expected_error: str):
        result = subprocess.run(
            [str(GATEWAY_INSTALL_SCRIPT), flag, ""],
            capture_output=True,
            text=True,
            env={"HOME": str(REPO_ROOT)},
        )

        assert result.returncode != 0
        assert expected_error in result.stderr


class TestMissionControlRuntimeWiring:
    def test_mission_control_launchagent_uses_in_process_runtime(self):
        """MC launchd service should start backend+poller entrypoint, not bare uvicorn."""
        if not MC_PLIST.exists():
            pytest.skip("Mission Control launchagent plist is not present in this repository checkout")
        plist_text = MC_PLIST.read_text(encoding="utf-8")
        assert "orchestration.mc_backend_service" in plist_text
        assert "<key>MISSION_CONTROL_BASE_URL</key>" in plist_text
        assert "<key>MISSION_CONTROL_TOKEN</key>" in plist_text
        assert "<key>MISSION_CONTROL_BOARD_ID</key>" in plist_text
        assert "<key>PYTHONPATH</key>" in plist_text

    def test_start_mc_script_uses_same_runtime_entrypoint(self):
        """Manual startup path should match launchd runtime wiring."""
        if not START_MC_SCRIPT.exists():
            pytest.skip("start-mc.sh is not present in this repository checkout")
        script_text = START_MC_SCRIPT.read_text(encoding="utf-8")
        assert "orchestration.mc_backend_service" in script_text


class TestLaunchAgentInstallers:
    def test_install_launchagents_uses_gateway_cli_installer(self):
        """Gateway should be installed via the supported OpenClaw CLI service path."""
        script_text = GATEWAY_INSTALL_SCRIPT.read_text(encoding="utf-8")
        assert "openclaw gateway install --force" in script_text

    def test_install_launchagents_installs_startup_check(self):
        """Startup-check launch agent must be installed alongside the gateway."""
        script_text = GATEWAY_INSTALL_SCRIPT.read_text(encoding="utf-8")
        assert "ai.openclaw.startup-check.plist" in script_text

    def test_install_launchagents_refreshes_runtime_startup_script(self):
        """The installer must update the script the launch agent actually executes."""
        script_text = GATEWAY_INSTALL_SCRIPT.read_text(encoding="utf-8")
        assert 'install -m 755 "$CONFIG_DIR/startup-check.sh" "$OPENCLAW_HOME/startup-check.sh"' in script_text

    def test_install_launchagents_only_installs_mc_services_when_plists_exist(self):
        """Mission Control launchagents are optional and should be gated by file presence."""
        script_text = GATEWAY_INSTALL_SCRIPT.read_text(encoding="utf-8")
        assert 'if [[ -f "$MC_BACKEND_PLIST" ]]; then' in script_text
        assert 'if [[ -f "$MC_FRONTEND_PLIST" ]]; then' in script_text
        assert 'skipping ai.openclaw.mission-control' in script_text

    def test_install_launchagents_rejects_placeholder_mc_token(self):
        """Launchd installer must not stamp the checked-in placeholder token into services."""
        script_text = GATEWAY_INSTALL_SCRIPT.read_text(encoding="utf-8")
        assert "is_valid_mc_token()" in script_text
        assert "your-local-auth-token-here" in script_text
        assert "Generated new local Mission Control token for launchd services." in script_text

    def test_startup_check_plist_runs_at_load(self):
        """Startup verification should trigger automatically after login/restart."""
        plist_text = STARTUP_CHECK_PLIST.read_text(encoding="utf-8")
        assert "<string>ai.openclaw.startup-check</string>" in plist_text
        assert "<key>RunAtLoad</key>" in plist_text
        assert "<true/>" in plist_text  # RunAtLoad must be enabled, not just present

    def test_startup_check_script_resolves_openclaw_without_login_shell(self):
        """Startup-check should resolve the CLI even under launchd's minimal PATH."""
        script_text = STARTUP_CHECK_SCRIPT.read_text(encoding="utf-8")
        assert "resolve_openclaw_bin()" in script_text
        assert ".nvm/versions/node/current/bin" in script_text
        assert "/opt/homebrew/bin/openclaw" in script_text

    def test_startup_check_treats_missing_target_as_non_fatal(self):
        """Missing optional WhatsApp target should not fail the one-shot startup verifier."""
        script_text = STARTUP_CHECK_SCRIPT.read_text(encoding="utf-8")
        assert "skipping startup confirmation" in script_text
        assert "exit 0" in script_text

    def test_mctrl_supervisor_template_has_throttle_interval(self):
        """Supervisor launchd template should back off between restart attempts."""
        plist_text = MCTRL_SUPERVISOR_PLIST.read_text(encoding="utf-8")
        assert "<key>ThrottleInterval</key>" in plist_text
        assert "<integer>10</integer>" in plist_text  # ThrottleInterval must have a positive value


# ---------------------------------------------------------------------------
# ORCH-sl1: Slack DM reply must be enabled (not "off")
#
# replyToModeByChatType.direct="off" means the agent reads DMs but never
# replies. Any commit that sets direct="off" silently breaks DM responses.
# ---------------------------------------------------------------------------


class TestSlackDmReplyConfig:
    def _slack_cfg(self, main_cfg: dict) -> dict:
        return main_cfg.get("channels", {}).get("slack", {})

    def test_reply_to_mode_direct_is_not_off(self, main_cfg: dict):
        """Agent must reply to Slack DMs — direct='off' silently breaks responses."""
        slack = self._slack_cfg(main_cfg)
        by_chat_type = slack.get("replyToModeByChatType", {})
        direct = by_chat_type.get("direct")
        assert direct != "off", (
            f"replyToModeByChatType.direct='{direct}' — DMs will be silently ignored. "
            "Set to 'all' or 'thread' (ORCH-sl1)"
        )

    def test_reply_to_mode_direct_is_all(self, main_cfg: dict):
        """replyToModeByChatType.direct should be 'all' to reply to every DM."""
        slack = self._slack_cfg(main_cfg)
        direct = slack.get("replyToModeByChatType", {}).get("direct")
        assert direct == "all", (
            f"Expected replyToModeByChatType.direct='all', got '{direct}' (ORCH-sl1)"
        )

    def test_reply_to_mode_top_level_is_not_off(self, main_cfg: dict):
        """Top-level replyToMode should not be 'off' — it overrides per-type settings."""
        slack = self._slack_cfg(main_cfg)
        mode = slack.get("replyToMode")
        assert mode != "off", (
            f"replyToMode='{mode}' overrides replyToModeByChatType and silences all replies. "
            "Remove or set to 'all' (ORCH-sl1)"
        )


# ---------------------------------------------------------------------------
# ORCH-sl2: slack-mcp stdio server must be present and correctly wired
# ---------------------------------------------------------------------------


class TestSlackMcpServerConfig:
    def _get_slack_mcp_server(self, main_cfg: dict) -> dict | None:
        servers = _get_mcp_servers(main_cfg)
        return next((s for s in servers if s.get("name") == "slack-mcp"), None)

    def test_slack_mcp_server_present(self, main_cfg: dict):
        """slack-mcp server must be registered in openclaw-mcp-adapter."""
        server = self._get_slack_mcp_server(main_cfg)
        assert server is not None, (
            "No 'slack-mcp' entry in plugins.entries.openclaw-mcp-adapter.config.servers. "
            "Add stdio server entry (ORCH-sl2)"
        )

    def test_slack_mcp_uses_stdio_transport(self, main_cfg: dict):
        """slack-mcp uses a local binary — transport must be 'stdio'."""
        server = self._get_slack_mcp_server(main_cfg)
        assert server is not None, "slack-mcp server not found (ORCH-sl2)"
        assert server.get("transport") == "stdio", (
            f"slack-mcp transport='{server.get('transport')}', expected 'stdio' (ORCH-sl2)"
        )

    def test_slack_mcp_token_uses_env_var(self, main_cfg: dict):
        """Slack token must be an env var placeholder, never a hardcoded value."""
        server = self._get_slack_mcp_server(main_cfg)
        assert server is not None, "slack-mcp server not found (ORCH-sl2)"
        env = server.get("env", {})
        import re
        token = env.get("SLACK_MCP_XOXB_TOKEN", "")
        assert re.match(r"^\$\{[A-Z][A-Z0-9_]+\}$", token), (
            f"SLACK_MCP_XOXB_TOKEN='{token}' must be exactly a single env var placeholder "
            "like '${OPENCLAW_SLACK_BOT_TOKEN}' — never hardcode credentials (ORCH-sl2)"
        )

    def test_slack_mcp_add_message_tool_enabled(self, main_cfg: dict):
        """SLACK_MCP_ADD_MESSAGE_TOOL must be 'true' to enable write capability."""
        server = self._get_slack_mcp_server(main_cfg)
        assert server is not None, "slack-mcp server not found (ORCH-sl2)"
        env = server.get("env", {})
        assert env.get("SLACK_MCP_ADD_MESSAGE_TOOL") == "true", (
            "SLACK_MCP_ADD_MESSAGE_TOOL must be 'true' to allow posting messages (ORCH-sl2)"
        )


# ---------------------------------------------------------------------------
# ORCH-sl3: all slack-mcp tool IDs must be explicitly in alsoAllow
# ---------------------------------------------------------------------------


class TestSlackMcpToolsAllowed:
    def test_also_allow_includes_all_slack_mcp_tools(self, main_cfg: dict):
        """All slack-mcp tool IDs must be in alsoAllow — removal silently disables Slack access."""
        also_allow = set(main_cfg["tools"].get("alsoAllow", []))
        missing = SLACK_MCP_TOOLS - also_allow
        assert not missing, (
            f"alsoAllow missing slack-mcp tools: {sorted(missing)}. "
            "Add them back to restore Slack read/write access (ORCH-sl3)"
        )
