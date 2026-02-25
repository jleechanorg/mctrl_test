"""Tests for genesis.memory — MEMORY.md seed content generator."""

import pytest

from genesis.memory import generate_seed_content, parse_memory_sections


class TestGenerateSeedContent:
    """Tests for generate_seed_content()."""

    def test_returns_string(self):
        content = generate_seed_content()
        assert isinstance(content, str)

    def test_starts_with_header(self):
        content = generate_seed_content()
        assert content.startswith("# MEMORY.md")

    def test_contains_architecture_decisions(self):
        content = generate_seed_content()
        assert "## Architecture Decisions" in content

    def test_contains_patterns_that_work(self):
        content = generate_seed_content()
        assert "## Patterns That Work" in content

    def test_contains_key_paths(self):
        content = generate_seed_content()
        assert "## Key Paths" in content

    def test_contains_current_goals(self):
        content = generate_seed_content()
        assert "## Current Goals" in content

    def test_contains_openclaw_workspace_path(self):
        content = generate_seed_content()
        assert "~/.openclaw/workspace/" in content

    def test_contains_jleechanclaw_repo_path(self):
        content = generate_seed_content()
        assert "jleechanclaw" in content

    def test_contains_worldarchitect_reference(self):
        content = generate_seed_content()
        assert "worldarchitect" in content

    def test_custom_goals(self):
        goals = ["Launch MVP", "Fix CI pipeline"]
        content = generate_seed_content(goals=goals)
        assert "Launch MVP" in content
        assert "Fix CI pipeline" in content

    def test_not_empty(self):
        content = generate_seed_content()
        assert len(content) > 100  # Meaningful content, not just headers


class TestParseMemorySections:
    """Tests for parse_memory_sections()."""

    def test_parses_sections(self):
        md = "# MEMORY.md\n\n## Section A\n- item 1\n\n## Section B\n- item 2\n"
        sections = parse_memory_sections(md)
        assert "Section A" in sections
        assert "Section B" in sections

    def test_empty_input(self):
        sections = parse_memory_sections("")
        assert sections == {}

    def test_section_content_preserved(self):
        md = "# MEMORY.md\n\n## Architecture Decisions\n- Use worktrees\n- CI must pass\n"
        sections = parse_memory_sections(md)
        assert "Use worktrees" in sections["Architecture Decisions"]

    def test_no_sections(self):
        md = "# Just a title\nSome text without sections\n"
        sections = parse_memory_sections(md)
        assert sections == {}
