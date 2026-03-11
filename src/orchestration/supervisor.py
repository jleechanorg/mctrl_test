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
from pathlib import Path
from typing import Callable

from orchestration.openclaw_notifier import default_outbox_path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("mctrl.supervisor")

REGISTRY_PATH = os.environ.get(
    "MCTRL_REGISTRY_PATH", ".tracking/bead_session_registry.jsonl"
)
REGISTRY_PATHS = os.environ.get("MCTRL_REGISTRY_PATHS", "")
OUTBOX_PATH = os.environ.get(
    "MCTRL_OUTBOX_PATH", default_outbox_path()
)
DEAD_LETTER_PATH = os.environ.get(
    "MCTRL_DEAD_LETTER_PATH", ".messages/outbox_dead_letter.jsonl"
)


def _get_int_env(name: str, default: int) -> int:
    raw = os.environ.get(name, str(default))
    try:
        return int(raw)
    except ValueError:
        logger.warning("Invalid %s value %r; falling back to %d", name, raw, default)
        return default


OUTBOX_ALERT_THRESHOLD = _get_int_env("MCTRL_OUTBOX_ALERT_THRESHOLD", 10)
OUTBOX_AGE_ALERT_SECONDS = _get_int_env("MCTRL_OUTBOX_AGE_ALERT_SECONDS", 3600)
OUTBOX_ALERT_COOLDOWN_SECONDS = _get_int_env("MCTRL_OUTBOX_ALERT_COOLDOWN_SECONDS", 3600)


ARCHIVE_AFTER_DAYS = _get_int_env("MCTRL_ARCHIVE_AFTER_DAYS", 7)

_running = True
_last_outbox_alert_at: float | None = None


def _expand_path(path: str) -> Path:
    p = Path(path).expanduser()
    if p.is_absolute():
        return p.resolve()
    return (Path.cwd() / p).resolve()


def _parse_registry_paths(raw: str) -> list[str]:
    normalized = raw.replace(";", ",").replace(":", ",")
    return [part.strip() for part in normalized.split(",") if part.strip()]


def _discover_sibling_registry_paths(
    *,
    current_registry: Path,
    outbox_path: str,
) -> list[Path]:
    # Discover sibling repo registries that share the same .messages target.
    outbox_parent = _expand_path(outbox_path).parent
    root_parent = Path.cwd().resolve().parent
    discovered: list[Path] = []
    for child in root_parent.iterdir():
        if not child.is_dir():
            continue
        candidate_registry = child / ".tracking" / "bead_session_registry.jsonl"
        if not candidate_registry.exists():
            continue
        candidate_messages = child / ".messages"
        if not candidate_messages.exists():
            continue
        try:
            if candidate_messages.resolve() != outbox_parent:
                continue
        except OSError:
            continue
        resolved_candidate = candidate_registry.resolve()
        if resolved_candidate != current_registry:
            discovered.append(resolved_candidate)
    return discovered


def _registry_paths_to_reconcile(
    *,
    registry_path: str,
    registry_paths_env: str,
    outbox_path: str,
) -> list[str]:
    primary = _expand_path(registry_path)
    resolved: list[Path] = [primary]
    if registry_paths_env.strip():
        resolved.extend(_expand_path(path) for path in _parse_registry_paths(registry_paths_env))
    elif registry_path == ".tracking/bead_session_registry.jsonl":
        resolved.extend(
            _discover_sibling_registry_paths(
                current_registry=primary,
                outbox_path=outbox_path,
            )
        )

    deduped: list[str] = []
    seen: set[str] = set()
    for path in resolved:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(key)
    return deduped


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
    from orchestration.session_registry import archive_terminal_mappings
    from orchestration.openclaw_notifier import notify_slack_outbox_alert, outbox_health_snapshot

    registry_paths = _registry_paths_to_reconcile(
        registry_path=REGISTRY_PATH,
        registry_paths_env=REGISTRY_PATHS,
        outbox_path=OUTBOX_PATH,
    )
    emitted: list[dict] = []
    for registry_path in registry_paths:
        emitted.extend(
            reconcile_registry_once(
                registry_path=registry_path,
                outbox_path=OUTBOX_PATH,
                dead_letter_path=DEAD_LETTER_PATH,
            )
        )
    snapshot = outbox_health_snapshot(
        outbox_path=OUTBOX_PATH,
        dead_letter_path=DEAD_LETTER_PATH,
    )
    maybe_alert_outbox_health(
        pending_count=int(snapshot["pending_count"]),
        dead_letter_count=int(snapshot["dead_letter_count"]),
        oldest_age_seconds=snapshot.get("oldest_age_seconds"),
        notify_fn=notify_slack_outbox_alert,
        threshold=OUTBOX_ALERT_THRESHOLD,
        age_threshold=OUTBOX_AGE_ALERT_SECONDS,
        cooldown_seconds=OUTBOX_ALERT_COOLDOWN_SECONDS,
        outbox_path=OUTBOX_PATH,
        dead_letter_path=DEAD_LETTER_PATH,
    )
    archived = 0
    for registry_path in registry_paths:
        archived += archive_terminal_mappings(
            registry_path=registry_path,
            archive_after_days=ARCHIVE_AFTER_DAYS,
        )
    if archived:
        logger.info(
            "Archived %d terminal mapping(s) across %d registry file(s)",
            archived,
            len(registry_paths),
        )
    return emitted


def maybe_alert_outbox_health(
    *,
    pending_count: int,
    dead_letter_count: int,
    oldest_age_seconds: int | None,
    notify_fn: Callable[[dict], bool],
    threshold: int,
    age_threshold: int,
    cooldown_seconds: int,
    outbox_path: str | None = None,
    dead_letter_path: str | None = None,
) -> bool:
    global _last_outbox_alert_at

    exceeds_backlog = pending_count >= max(0, threshold)
    exceeds_age = oldest_age_seconds is not None and oldest_age_seconds >= max(0, age_threshold)
    has_dead_letter = dead_letter_count > 0
    if not (exceeds_backlog or exceeds_age or has_dead_letter):
        return False

    now = time.monotonic()
    if _last_outbox_alert_at is not None and (now - _last_outbox_alert_at) < max(0, cooldown_seconds):
        return False

    payload = {
        "event": "outbox_backlog_alert",
        "pending_count": pending_count,
        "dead_letter_count": dead_letter_count,
        "oldest_age_seconds": oldest_age_seconds,
        "threshold": threshold,
        "age_threshold": age_threshold,
        "outbox_path": outbox_path or OUTBOX_PATH,
        "dead_letter_path": dead_letter_path or DEAD_LETTER_PATH,
    }
    if notify_fn(payload):
        _last_outbox_alert_at = now
        logger.warning(
            "Outbox alert fired: pending=%d dead_letter=%d oldest_age=%s",
            pending_count,
            dead_letter_count,
            oldest_age_seconds,
        )
        return True
    return False


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
        "mctrl supervisor starting (interval=%ds, registry=%s, registry_paths=%s, outbox=%s)",
        args.interval,
        REGISTRY_PATH,
        REGISTRY_PATHS or "<auto>",
        OUTBOX_PATH,
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
