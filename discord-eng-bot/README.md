# Discord Consensus Profile Backup

This folder is the repo-safe backup for the dedicated Discord profile at `~/.openclaw-consensus`.

## Files

- `openclaw.json` - redacted Consensus profile config backup
- `SOUL.md` - Consensus system prompt backup
- `discord-app-manifest.json` - Discord app manifest template
- `README.md` - restore and usage notes

## Runtime Model

- Profile: `consensus` (`~/.openclaw-consensus`)
- Channel: Discord only
- Reply behavior: mention-gated (`requireMention: true`)
- Research behavior:
  - concise by default
  - deeper mode on `rsearch`/`research` requests
  - every answer includes a `Sources:` section

## Tool Surface

- Allowed: `web_search`, `web_fetch`, `second-opinion-tool_agent_second_opinion`, `second-opinion-tool_rate_limit_status`, `second-opinion-tool_health-check`
- Denied: filesystem, exec/process, browser/canvas, cron/gateway/session spawn/send
- Web search provider: `perplexity`

## Required Secrets / Vars

- `DISCORD_BOT_TOKEN`
- `PERPLEXITY_API_KEY`
- `OPENCLAW_GATEWAY_TOKEN` — populates both `gateway.auth.token` and `gateway.remote.token`
- `SECOND_OPINION_MCP_URL` — populates `plugins.entries.openclaw-mcp-adapter.config.servers[0].url`

## Restore Into `~/.openclaw-consensus`

1. Create directory:
   ```bash
   mkdir -p ~/.openclaw-consensus/workspace
   ```
2. Copy config:
   ```bash
   cp discord-eng-bot/openclaw.json ~/.openclaw-consensus/openclaw.json
   ```
3. Copy prompt:
   ```bash
   cp discord-eng-bot/SOUL.md ~/.openclaw-consensus/workspace/SOUL.md
   ```
4. Set real values in `~/.openclaw-consensus/openclaw.json`:
   - `channels.discord.token`
   - `channels.discord.guilds`
   - `tools.web.search.perplexity.apiKey` (or ensure env var is present for the service)
   - `gateway.auth.token` and `gateway.remote.token`
   - `plugins.entries.openclaw-mcp-adapter.config.servers[0].url`
5. Restart profile gateway:
   ```bash
   openclaw --profile consensus gateway restart
   ```
6. Ensure profile model auth exists before first reply:
   ```bash
   openclaw --profile consensus agents add openai-codex:default
   ```
   If you already authenticated in another profile, you can also copy
   `auth-profiles.json` into `~/.openclaw-consensus/agents/main/agent/`.

## Quick Validation

```bash
openclaw --profile consensus agent --channel discord --agent main --message "@Consensus research compare X vs Y" --json
```

Expected: response includes `Bottom line`, `Findings`, `Tradeoffs`, `Sources`, and `Tool audit`.
