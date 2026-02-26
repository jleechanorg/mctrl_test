"""Genesis writer — writes config files to disk for OpenClaw."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from genesis.config import build_openclaw_config
from genesis.memory import generate_seed_content
from genesis.cron import build_all_jobs


def _ensure_parent(path: str) -> None:
    """Create parent directories if they don't exist."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def write_memory_md(
    path: str,
    *,
    goals: Optional[list[str]] = None,
    overwrite: bool = True,
) -> bool:
    """Write MEMORY.md seed content to disk.

    Args:
        path: Target file path.
        goals: Optional custom goals.
        overwrite: If False, skip if file exists.

    Returns:
        True if written, False if skipped.
    """
    if not overwrite and os.path.exists(path):
        return False

    _ensure_parent(path)
    content = generate_seed_content(goals=goals)
    Path(path).write_text(content, encoding="utf-8")
    return True


def write_openclaw_config(
    path: str,
    *,
    extra_paths: Optional[list[str]] = None,
) -> bool:
    """Write openclaw.json config to disk.

    Args:
        path: Target file path.
        extra_paths: Additional paths for memory search.

    Returns:
        True if written.
    """
    _ensure_parent(path)
    config = build_openclaw_config(extra_paths=extra_paths)
    Path(path).write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return True


def write_cron_jobs(path: str) -> bool:
    """Write cron jobs JSON to disk.

    Args:
        path: Target file path.

    Returns:
        True if written.
    """
    _ensure_parent(path)
    jobs = build_all_jobs()
    Path(path).write_text(json.dumps(jobs, indent=2) + "\n", encoding="utf-8")
    return True


def write_all(
    *,
    memory_path: str,
    config_path: str,
    cron_path: str,
    **kwargs,
) -> dict[str, bool]:
    """Write all Genesis config files to disk.

    Returns:
        Dict mapping file type to success boolean.
    """
    return {
        "memory": write_memory_md(memory_path, **{k: v for k, v in kwargs.items() if k in ("goals", "overwrite")}),
        "config": write_openclaw_config(config_path, **{k: v for k, v in kwargs.items() if k == "extra_paths"}),
        "cron": write_cron_jobs(cron_path),
    }
