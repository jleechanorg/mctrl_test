"""Genesis memory — MEMORY.md seed content generator and parser."""

from __future__ import annotations

import re
from typing import Optional


_DEFAULT_SEED = """\
# MEMORY.md - Long-Term Knowledge

## Architecture Decisions
- worldarchitect.ai: LLM decides, server executes (core principle)
- FastEmbed classifier for intent detection (<50ms)
- Gemini 3 code execution mode REQUIRED
- 10min/600s timeout across all layers

## Patterns That Work
- Use worktrees for parallel agent work
- CI must pass before merge, no exceptions
- memory_search for semantic recall, memory_get for direct reads
- Daily memory files for session context; MEMORY.md for durable facts
- Markdown files are source of truth; sqlite is just the index

## Key Paths
- OpenClaw workspace: ~/.openclaw/workspace/
- OpenClaw config: ~/.openclaw/openclaw.json
- jleechanclaw repo: /Users/jleechan/project_jleechanclaw/jleechanclaw
- worldarchitect.ai: /Users/jleechan/projects/worldarchitect.ai

## Current Goals
- Get first 100 users for worldarchitect.ai (AI RPG)
- Set up Genesis orchestration layer
"""


def generate_seed_content(
    *,
    goals: Optional[list[str]] = None,
) -> str:
    """Generate MEMORY.md seed content.

    Args:
        goals: Optional list of custom goals to replace the default ones.
    """
    if goals is None:
        return _DEFAULT_SEED

    # Replace the Current Goals section with custom goals
    lines = _DEFAULT_SEED.split("\n")
    result = []
    in_goals = False
    for line in lines:
        if line.startswith("## Current Goals"):
            in_goals = True
            result.append(line)
            for goal in goals:
                result.append(f"- {goal}")
            continue
        if in_goals:
            if line.startswith("## "):
                in_goals = False
                result.append(line)
            # Skip default goal lines
            continue
        result.append(line)

    return "\n".join(result)


def parse_memory_sections(content: str) -> dict[str, str]:
    """Parse a MEMORY.md file into sections.

    Args:
        content: Raw markdown content.

    Returns:
        Dict mapping section headers (without ##) to their content.
    """
    if not content.strip():
        return {}

    sections: dict[str, str] = {}
    current_section: str | None = None
    current_lines: list[str] = []

    for line in content.split("\n"):
        match = re.match(r"^## (.+)$", line)
        if match:
            if current_section is not None:
                sections[current_section] = "\n".join(current_lines).strip()
            current_section = match.group(1)
            current_lines = []
        elif current_section is not None:
            current_lines.append(line)

    if current_section is not None:
        sections[current_section] = "\n".join(current_lines).strip()

    return sections
