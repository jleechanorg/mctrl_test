#!/bin/bash
# OpenClaw Startup Verification
# Purpose: Runs after login to verify OpenClaw is running and send confirmation

LOG_FILE="$HOME/.openclaw/logs/startup-check.log"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

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
            if openclaw channels list | grep -q "WhatsApp default: linked, enabled"; then
                openclaw message send --target "+6502965127" \
                    --message "🚀 MacBook restarted! OpenClaw auto-started successfully (PID: $PID) ✅" \
                    --channel whatsapp >> "$LOG_FILE" 2>&1
                echo "[$TIMESTAMP] ✅ Startup confirmation sent via WhatsApp" >> "$LOG_FILE"
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
