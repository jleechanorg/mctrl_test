#!/bin/bash
# OpenClaw Startup Verification
# Purpose: Runs after login to verify OpenClaw is running and send confirmation

LOG_FILE="$HOME/.openclaw/logs/startup-check.log"
LOG_DIR="$(dirname "$LOG_FILE")"
OPENCLAW_BIN="$(command -v openclaw || true)"
TARGET="${OPENCLAW_WHATSAPP_TARGET:-}"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Ensure openclaw CLI exists
if [ -z "$OPENCLAW_BIN" ]; then
    echo "[$TIMESTAMP] ❌ openclaw CLI not found in PATH" >&2
    exit 1
fi

# Ensure log directory exists
if ! mkdir -p "$LOG_DIR"; then
    echo "[$TIMESTAMP] ❌ Failed to create log directory: $LOG_DIR" >&2
    exit 1
fi

if [ -z "$TARGET" ]; then
    echo "[$TIMESTAMP] ❌ OPENCLAW_WHATSAPP_TARGET is not set. Set it before enabling startup confirmation." >> "$LOG_FILE"
    exit 1
fi

# Wait for network to be available (max 30 seconds)
for i in {1..30}; do
    if ping -c 1 8.8.8.8 &> /dev/null; then
        break
    fi
    sleep 1
done

# Wait for OpenClaw to start (max 30 seconds)
for i in {1..30}; do
    if launchctl list | grep -q "ai.openclaw.gateway"; then
        PID=$(launchctl list | grep "ai.openclaw.gateway" | awk '{print $1}')
        if [ "$PID" != "-" ] && [ -n "$PID" ]; then
            echo "[$TIMESTAMP] ✅ OpenClaw started successfully (PID: $PID)" >> "$LOG_FILE"

            # Wait a bit more for WhatsApp to connect
            sleep 10

            # Send startup confirmation via WhatsApp
            if "$OPENCLAW_BIN" channels list | grep -q "WhatsApp default: linked, enabled"; then
                if "$OPENCLAW_BIN" message send --target "$TARGET" \
                    --message "🚀 OpenClaw auto-started successfully (PID: $PID) ✅" \
                    --channel whatsapp >> "$LOG_FILE" 2>&1; then
                    echo "[$TIMESTAMP] ✅ Startup confirmation sent via WhatsApp" >> "$LOG_FILE"
                else
                    echo "[$TIMESTAMP] ❌ Failed to send startup confirmation via WhatsApp" >> "$LOG_FILE"
                    exit 1
                fi
            else
                echo "[$TIMESTAMP] ⚠️  WhatsApp not ready yet" >> "$LOG_FILE"
            fi

            exit 0
        fi
    fi
    sleep 1
done

echo "[$TIMESTAMP] ❌ OpenClaw failed to start within 30 seconds" >> "$LOG_FILE"
exit 1
