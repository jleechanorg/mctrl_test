"""Genesis config builder — generates OpenClaw configuration."""

from __future__ import annotations

import os
from typing import Optional

# Default extra paths for memory search indexing
DEFAULT_EXTRA_PATHS = [
    os.path.expanduser("~/projects/worldarchitect.ai/.claude/learnings.md"),
    os.path.expanduser("~/projects/worldarchitect.ai/CLAUDE.md"),
]


def build_openclaw_config(
    *,
    extra_paths: Optional[list[str]] = None,
) -> dict:
    """Build the complete openclaw.json config dict.

    Args:
        extra_paths: Additional file paths to index for memory search.
                     Merged with defaults.
    """
    paths = list(DEFAULT_EXTRA_PATHS)
    if extra_paths:
        paths.extend(extra_paths)

    return {
        "agents": {
            "defaults": {
                "memorySearch": {
                    "enabled": True,
                    "extraPaths": paths,
                    "query": {
                        "hybrid": {
                            "enabled": True,
                            "vectorWeight": 0.7,
                            "textWeight": 0.3,
                            "temporalDecay": {
                                "enabled": True,
                                "halfLifeDays": 30,
                            },
                            "mmr": {
                                "enabled": True,
                                "lambda": 0.7,
                            },
                        },
                    },
                    "experimental": {
                        "sessionMemory": True,
                    },
                },
                "compaction": {
                    "memoryFlush": {
                        "enabled": True,
                    },
                },
            },
        },
    }


def validate_config(config: dict) -> bool:
    """Validate that an OpenClaw config dict has all required keys.

    Returns True if valid, False otherwise.
    """
    try:
        agents = config["agents"]
        defaults = agents["defaults"]
        mem = defaults["memorySearch"]
        if not mem.get("enabled", False):
            return False
        # Check nested structure exists
        _ = mem["extraPaths"]
        _ = mem["query"]["hybrid"]["temporalDecay"]
        _ = mem["query"]["hybrid"]["mmr"]
        _ = mem["experimental"]
        _ = defaults["compaction"]["memoryFlush"]
        return True
    except (KeyError, TypeError):
        return False
