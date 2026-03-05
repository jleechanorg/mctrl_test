# Slack Setup Guide for OpenClaw

**App ID:** YOUR_SLACK_APP_ID
**Client ID:** YOUR_SLACK_CLIENT_ID
**Status:** App created, awaiting OAuth installation

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Add Scopes in Slack UI

Go to: https://api.slack.com/apps/${YOUR_SLACK_APP_ID}/oauth

Click **"Bot Token Scopes"** and add:

**Essential Scopes:**
- ✅ `chat:write` - Send messages
- ✅ `channels:read` - Read public channels
- ✅ `channels:history` - Read public channel messages
- ✅ `groups:read` - Read private channels
- ✅ `groups:history` - Read private channel messages
- ✅ `im:read` - Read DMs
- ✅ `im:history` - Read DM messages
- ✅ `im:write` - Send DMs
- ✅ `users:read` - Read user info
- ✅ `team:read` - Read workspace info
- ✅ `app_mentions:read` - Read mentions

**Recommended Scopes:**
- ✅ `reactions:read` - Read reactions
- ✅ `reactions:write` - Add reactions
- ✅ `files:read` - View files
- ✅ `files:write` - Upload files

### Step 2: Install App to Workspace

1. Scroll to top of OAuth & Permissions page
2. Click **"Install to Workspace"** (green button)
3. Click **"Allow"**
4. **COPY** the **"Bot User OAuth Token"** (starts with `xoxb-`)

### Step 3: Configure OpenClaw

Run the setup script with your bot token:

```bash
~/.openclaw/slack-setup.sh [REDACTED]
```

**With Socket Mode (recommended):**
1. Go to Socket Mode in Slack: https://api.slack.com/apps/${YOUR_SLACK_APP_ID}/socket-mode
2. Enable Socket Mode
3. Generate token with `connections:write` scope
4. Run:
```bash
~/.openclaw/slack-setup.sh [REDACTED] xapp-YOUR-APP-TOKEN
```

---

## ✅ Verification

After setup, verify with:

```bash
# Check Slack is configured
openclaw channels list

# Test message
openclaw message send --channel slack --target '@your-username' --message 'Test from OpenClaw!'
```

---

## 🔧 Manual Configuration (Alternative)

If the script doesn't work, configure manually:

```bash
openclaw channels add \
  --channel slack \
  --account default \
  --bot-token [REDACTED]
```

With Socket Mode:
```bash
openclaw channels add \
  --channel slack \
  --account default \
  --bot-token [REDACTED] \
  --app-token xapp-YOUR-APP-TOKEN
```

---

## 📋 Troubleshooting

### "Invalid token" error
- Make sure you copied the **Bot User OAuth Token** (not Client Secret)
- Token should start with `xoxb-`

### "Missing scopes" error
- Go back to OAuth & Permissions
- Add the missing scopes listed above
- **Reinstall the app** to apply new scopes

### Can't send DMs
- Make sure you added `im:write` and `im:history` scopes
- User must have DMs enabled in Slack settings

### Socket Mode issues
- Generate app-level token with `connections:write` scope
- Token should start with `xapp-`
- Socket Mode must be enabled in app settings

---

## 🎯 Next Steps After Setup

1. **Invite bot to channels:**
   - In Slack, type `/invite @openclaw` in any channel

2. **Test messaging:**
   ```bash
   # Send to channel
   openclaw message send --channel slack --target '#general' --message 'Hello!'

   # Send DM
   openclaw message send --channel slack --target '@username' --message 'Hi there!'
   ```

3. **Configure auto-start:**
   - Already configured! Slack will auto-start with WhatsApp on boot

4. **Monitor logs:**
   ```bash
   openclaw logs --follow | grep slack
   ```

---

## 🔐 Security Notes

- ✅ Bot token stored in `~/.openclaw/openclaw.json` (chmod 700)
- ✅ Tokens never logged to files
- ✅ All communication over HTTPS/WSS
- ⚠️  Never share your tokens publicly or commit to git

---

**Need help?** Check OpenClaw docs: https://docs.openclaw.ai/channels/slack
