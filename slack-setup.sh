#!/bin/bash
# Slack Setup Script for OpenClaw
# Run this after getting your Bot Token from Slack

SLACK_APP_ID="${SLACK_APP_ID:-YOUR_SLACK_APP_ID}"
SLACK_CLIENT_ID="${SLACK_CLIENT_ID:-YOUR_SLACK_CLIENT_ID}"

echo "🦞 OpenClaw Slack Integration Setup"
echo "===================================="
echo ""

# Resolve tokens from env or args
BOT_TOKEN="${SLACK_BOT_TOKEN:-$1}"
APP_TOKEN="${SLACK_APP_TOKEN:-$2}"

# Prompt for missing tokens
if [ -z "$BOT_TOKEN" ]; then
    echo "❌ Error: Bot token required"
    echo "You can provide it as:"
    echo "  - Environment variable: SLACK_BOT_TOKEN"
    echo "  - First positional argument"
    echo ""
    echo "Usage: $0 <bot-token> [app-token]"
    echo ""
    echo "Example:"
    echo "  $0 xoxb-your-bot-token-here"
    echo "  $0 xoxb-your-bot-token-here xapp-your-app-token-here"
    echo ""
    echo "To get the tokens:"
    echo "1. Go to https://api.slack.com/apps/$SLACK_APP_ID/oauth"
    echo "2. Click 'OAuth & Permissions'"
    echo "3. Copy the 'Bot User OAuth Token' (xoxb-...)"
    echo "4. (Optional) Enable Socket Mode and copy App Token (xapp-...)"
    exit 1
fi

export SLACK_BOT_TOKEN="$BOT_TOKEN"
if [ -n "$APP_TOKEN" ]; then
    export SLACK_APP_TOKEN="$APP_TOKEN"
fi

echo "📝 Configuration:"
echo "  App ID: $SLACK_APP_ID"
echo "  Client ID: $SLACK_CLIENT_ID"
echo "  Bot Token: ${BOT_TOKEN:0:12}..."
if [ -n "$APP_TOKEN" ]; then
    echo "  App Token: ${APP_TOKEN:0:12}... (Socket Mode enabled)"
fi
echo ""

# Add Slack channel
echo "🔧 Adding Slack channel to OpenClaw..."
if [ -n "$APP_TOKEN" ]; then
    # With Socket Mode (recommended)
    openclaw channels add \
        --channel slack \
        --account default \
        --bot-token "$BOT_TOKEN" \
        --app-token "$APP_TOKEN"
else
    # Without Socket Mode
    openclaw channels add \
        --channel slack \
        --account default \
        --bot-token "$BOT_TOKEN"
fi

OPENCLAW_EXIT=$?
if [ $OPENCLAW_EXIT -eq 0 ]; then
    echo ""
    echo "✅ Slack channel added successfully!"
    echo ""
    echo "Testing connection..."
    sleep 3
    openclaw channels list
    echo ""
    echo "🎉 Setup complete! You can now send messages:"
    echo "  openclaw message send --channel slack --target '@your-slack-username' --message 'Hello from OpenClaw!'"
else
    echo ""
    echo "❌ Failed to add Slack channel (exit code: $OPENCLAW_EXIT)"
    echo "Check the error above and try again"
    exit 1
fi
