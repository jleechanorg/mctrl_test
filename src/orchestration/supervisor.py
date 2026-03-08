"""mctrl supervisor daemon.

Runs reconcile_registry_once on a fixed interval, watching bead/session
mappings and emitting task_finished / task_needs_human notifications when
agent sessions exit.

Usage:
    python -m orchestration.supervisor [--interval 30] [--once]

Environment (loaded from ~/.openclaw/set-slack-env.sh if not already set):
    SLACK_BOT_TOKEN or OPENCLAW_SLACK_BOT_TOKEN   — Slack bot token
    OPENCLAW_NOTIFY_AGENT                          — OpenClaw MCP agent name (optional)
"""
from __future__ import annotations

import argparse
import logging
import os
import signal
import subprocess
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("mctrl.supervisor")

REGISTRY_PATH = os.environ.get(
    "MCTRL_REGISTRY_PATH", ".tracking/bead_session_registry.jsonl"
)
OUTBOX_PATH = os.environ.get(
    "MCTRL_OUTBOX_PATH", ".messages/outbox.jsonl"
)

_running = True


def _handle_signal(sig: int, _frame: object) -> None:
    global _running
    logger.info("Signal %s received — shutting down after current tick", sig)
    _running = False


def _ensure_slack_token() -> None:
    """Load SLACK_BOT_TOKEN from set-slack-env.sh if not already set."""
    if os.environ.get("SLACK_BOT_TOKEN") or os.environ.get("OPENCLAW_SLACK_BOT_TOKEN"):
        return
    script = os.path.expanduser("~/.openclaw/set-slack-env.sh")
    if not os.path.exists(script):
        logger.warning("No SLACK_BOT_TOKEN and %s not found — Slack notifications disabled", script)
        return
    try:
        result = subprocess.run(
            ["bash", "-c", f"source {script} && env"],
            capture_output=True, text=True, timeout=5,
        )
        for line in result.stdout.splitlines():
            if line.startswith("SLACK_BOT_TOKEN="):
                os.environ["SLACK_BOT_TOKEN"] = line.split("=", 1)[1]
                logger.info("Loaded SLACK_BOT_TOKEN from set-slack-env.sh")
            elif line.startswith("OPENCLAW_SLACK_BOT_TOKEN="):
                os.environ["OPENCLAW_SLACK_BOT_TOKEN"] = line.split("=", 1)[1]
                logger.info("Loaded OPENCLAW_SLACK_BOT_TOKEN from set-slack-env.sh")
    except Exception as exc:
        logger.warning("Could not load SLACK_BOT_TOKEN: %s", exc)


def run_once() -> list[dict]:
    # Import here so PYTHONPATH is resolved at runtime
    from orchestration.reconciliation import reconcile_registry_once
    return reconcile_registry_once(
        registry_path=REGISTRY_PATH,
        outbox_path=OUTBOX_PATH,
    )


def main() -> None:
    global _running
    _running = True  # Reset in case main() is called again in the same process (e.g. tests)
    parser = argparse.ArgumentParser(description="mctrl supervisor loop")
    parser.add_argument("--interval", type=int, default=30, help="Poll interval in seconds (default: 30)")
    parser.add_argument("--once", action="store_true", help="Run once and exit (useful for cron)")
    args = parser.parse_args()

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    _ensure_slack_token()

    logger.info(
        "mctrl supervisor starting (interval=%ds, registry=%s, outbox=%s)",
        args.interval, REGISTRY_PATH, OUTBOX_PATH,
    )

    while _running:
        try:
            emitted = run_once()
            if emitted:
                logger.info("Emitted %d event(s): %s", len(emitted), [e["event"] for e in emitted])
        except Exception as exc:
            logger.error("reconcile_registry_once failed: %s", exc, exc_info=True)

        if args.once:
            break

        # Sleep in short chunks so SIGTERM is handled promptly
        deadline = time.monotonic() + args.interval
        while _running and time.monotonic() < deadline:
            time.sleep(1)

    logger.info("mctrl supervisor stopped")


if __name__ == "__main__":
    main()
