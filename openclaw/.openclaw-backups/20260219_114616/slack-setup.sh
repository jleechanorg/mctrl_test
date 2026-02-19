#!/bin/bash
# Slack Setup Script for OpenClaw
# Run this after getting your Bot Token from Slack

echo "🦞 OpenClaw Slack Integration Setup"
echo "===================================="
echo ""

# Check if tokens are provided
if [ -z "$1" ]; then
    echo "❌ Error: Bot token required"
    echo ""
    echo "Usage: $0 <bot-token> [app-token]"
    echo ""
    echo "Example:"
    echo "  $0 [REDACTED]"
    echo "  $0 [REDACTED] xapp-your-app-token-here"
    echo ""
    echo "To get your tokens:"
    echo "1. Go to https://api.slack.com/apps/A0AESRKA7L3"
    echo "2. Click 'OAuth & Permissions'"
    echo "3. Copy the 'Bot User OAuth Token' (xoxb-...)"
    echo "4. (Optional) Enable Socket Mode and copy App Token (xapp-...)"
    exit 1
fi

[REDACTED]
[REDACTED]

echo "📝 Configuration:"
echo "  App ID: A0AESRKA7L3"
echo "  Client ID: 9541820692839.10502869347683"
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

if [ $? -eq 0 ]; then
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
    echo "❌ Failed to add Slack channel"
    echo "Check the error above and try again"
    exit 1
fi
