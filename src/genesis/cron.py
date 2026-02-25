"""Genesis cron — cron job definition builder for OpenClaw."""

from __future__ import annotations

from typing import Optional


def build_curation_job(
    *,
    cron_expr: str = "0 22 * * 0",
) -> dict:
    """Build the MEMORY.md curation cron job definition.

    Args:
        cron_expr: Cron expression (default: Sunday 10PM PST).
    """
    return {
        "id": "genesis-memory-curation",
        "name": "Genesis MEMORY.md curation",
        "enabled": True,
        "schedule": {
            "kind": "cron",
            "expr": cron_expr,
            "tz": "America/Los_Angeles",
        },
        "sessionTarget": "isolated",
        "wakeMode": "now",
        "payload": {
            "kind": "agentTurn",
            "message": (
                "Review daily memory files (memory/*.md) from the last 7 days. "
                "Extract important decisions, patterns, project status updates, "
                "and lessons learned. Update MEMORY.md with curated durable knowledge. "
                "Don't duplicate existing entries. Keep MEMORY.md concise and focused "
                "on facts that help future sessions start warm."
            ),
        },
        "delivery": {
            "mode": "none",
            "channel": "last",
        },
    }


def build_all_jobs() -> list[dict]:
    """Build all Genesis cron job definitions."""
    return [build_curation_job()]


def validate_cron_job(job: dict) -> bool:
    """Validate a cron job definition matches the OpenClaw format.

    Returns True if valid, False otherwise.
    """
    required_keys = {"id", "schedule", "payload"}
    if not all(k in job for k in required_keys):
        return False

    schedule = job.get("schedule", {})
    if not isinstance(schedule, dict):
        return False
    if schedule.get("kind") not in ("cron", "interval"):
        return False

    payload = job.get("payload", {})
    if not isinstance(payload, dict):
        return False

    return True
