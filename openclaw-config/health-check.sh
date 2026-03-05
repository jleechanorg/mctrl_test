#!/bin/bash
# OpenClaw Health Check & Auto-Recovery Script
# Purpose: Monitors OpenClaw gateway and restarts if needed

LOG_FILE="$HOME/.openclaw/logs/health-check.log"
LOG_DIR="$(dirname "$LOG_FILE")"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
OPENCLAW_BIN="$(command -v openclaw || true)"

if [ -z "$OPENCLAW_BIN" ]; then
    echo "[$TIMESTAMP] ❌ openclaw CLI not found in PATH"
    exit 1
fi

if ! mkdir -p "$LOG_DIR"; then
    echo "[$TIMESTAMP] ❌ Failed to create log directory: $LOG_DIR"
    exit 1
fi

# Function to log messages
log_message() {
    echo "[$TIMESTAMP] $1" >> "$LOG_FILE"
}

# Check if gateway is running
if ! launchctl list | grep -q "ai.openclaw.gateway"; then
    log_message "❌ Gateway not loaded in launchctl. Installing..."
    if "$OPENCLAW_BIN" gateway install >> "$LOG_FILE" 2>&1; then
        log_message "✅ Gateway installed"
        exit 0
    else
        log_message "❌ Gateway install failed"
        exit 1
    fi
fi

# Check if process is actually running
PID=$(launchctl list | grep "ai.openclaw.gateway" | awk '{print $1}')
if [ "$PID" = "-" ] || [ -z "$PID" ]; then
    log_message "⚠️  Gateway loaded but not running. Restarting..."
    if launchctl kickstart gui/$(id -u)/ai.openclaw.gateway >> "$LOG_FILE" 2>&1; then
        log_message "✅ Gateway kickstarted"
        exit 0
    else
        log_message "❌ Gateway kickstart failed"
        exit 1
    fi
fi

# Check if gateway is responding
if ! "$OPENCLAW_BIN" gateway status | grep -q "Runtime: running"; then
    log_message "⚠️  Gateway not responding. Restarting..."
    if "$OPENCLAW_BIN" gateway stop >> "$LOG_FILE" 2>&1 && sleep 2 && "$OPENCLAW_BIN" gateway install >> "$LOG_FILE" 2>&1; then
        log_message "✅ Gateway restarted"
        exit 0
    else
        log_message "❌ Gateway restart failed"
        exit 1
    fi
fi

# Check WhatsApp connection
if ! "$OPENCLAW_BIN" channels list | grep -q "WhatsApp default: linked, enabled"; then
    log_message "⚠️  WhatsApp not linked. Attempting recovery..."
    # Note: Auto-relink requires QR scan, so just log the issue
    log_message "❌ WhatsApp disconnected - manual intervention required"
    exit 1
fi

log_message "✅ All health checks passed (PID: $PID)"
exit 0
