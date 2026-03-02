# Discord Engineering Q&A Bot

OpenClaw-powered Discord bot for public engineering Q&A with restricted permissions.

## Files

- `openclaw.json` - OpenClaw configuration
- `discord-app-manifest.json` - Discord app manifest (for Developer Portal)
- `README.md` - This file (setup + usage instructions)

## Security Model

This bot is designed for **public use** with strict security:

### Sandbox
- Mode: `non-main` - public sessions run in isolated Docker containers
- Workspace access: `none` - no file system access

### Tool Restrictions
- **Denied**: read, write, edit, apply_patch, exec, bash, process, browser, canvas, nodes, cron, gateway, discord, sessions_send, sessions_spawn
- **Allowed**: web_search, web_fetch, and selected `second-opinion-tool` MCP methods (`agent_second_opinion`, `rate_limit_status`, `health-check`)

### Anti-Spam
- `requireMention: true` - bot only responds when @mentioned
- `groupPolicy: allowlist` - only configured guilds are allowed
- `replyToMode: off` - no auto-reply threading behavior

### Command Handling
- `commands.native: true` - OpenClaw native command handling is enabled

## Setup

1. **Create Discord App**
   - Go to https://discord.com/developers/applications
   - Create new application
   - Go to Bot section, create bot
   - Enable Message Content Intent

2. **Get Bot Token**
   - Reset token in Bot section
   - Copy token (you'll need it for openclaw.json)

3. **Configure OpenClaw**
   - Copy `openclaw.json` to `~/.openclaw/openclaw.json` or merge
   - Set `channels.discord.token` to your bot token (or set `DISCORD_BOT_TOKEN` if using env var expansion)
   - Set your Discord server ID under `channels.discord.guilds`
   - Ensure the Discord plugin is enabled:
     ```bash
     openclaw plugins enable discord
     ```

4. **Add Bot to Server**
   - Go to OAuth2 > URL Generator
   - Scopes: `bot`, `applications.commands`
   - Permissions: `View Channels`, `Send Messages`, `Read Message History`, `Embed Links`
   - Use generated URL to invite bot

5. **Start OpenClaw**
   ```bash
   openclaw gateway run
   ```

6. **Verify Discord Is Active**
   ```bash
   openclaw channels list
   openclaw channels capabilities --channel discord
   openclaw message send --channel discord --target channel:YOUR_CHANNEL_ID --message "healthcheck" --dry-run
   ```

## Usage

Users interact with the bot by:
- @mentioning the bot in channels
- Posting in allowed Discord guilds/channels configured under `channels.discord.guilds`

The bot can:
- Answer engineering questions via web search
- Fetch documentation from URLs
- Provide helpful responses

The bot CANNOT:
- Read/write files
- Execute code
- Access other Discord features
- Access your system
