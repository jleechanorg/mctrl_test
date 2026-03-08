"""Tests for orchestration.agent_registry — persistent agent ID mapping."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orchestration.agent_registry import AgentRegistry


@pytest.fixture
def tmp_registry(tmp_path: Path) -> AgentRegistry:
    """Create a registry with a temporary file path."""
    return AgentRegistry(file_path=tmp_path / "test_registry.json")


class TestAgentRegistry:
    """Tests for AgentRegistry class."""

    def test_register_and_lookup_roundtrip(self, tmp_registry: AgentRegistry):
        """Register a tmux session and lookup returns the agent ID."""
        tmp_registry.register("session-1", "mc-agent-123")

        result = tmp_registry.lookup("session-1")

        assert result == "mc-agent-123"

    def test_lookup_nonexistent_returns_none(self, tmp_registry: AgentRegistry):
        """Lookup of nonexistent session returns None."""
        result = tmp_registry.lookup("nonexistent")

        assert result is None

    def test_remove_existing(self, tmp_registry: AgentRegistry):
        """Remove an existing session returns True and removes it."""
        tmp_registry.register("session-1", "mc-agent-123")

        result = tmp_registry.remove("session-1")

        assert result is True
        assert tmp_registry.lookup("session-1") is None

    def test_remove_nonexistent_returns_false(self, tmp_registry: AgentRegistry):
        """Remove nonexistent session returns False."""
        result = tmp_registry.remove("nonexistent")

        assert result is False

    def test_list_all_empty(self, tmp_registry: AgentRegistry):
        """list_all returns empty dict when no registrations."""
        result = tmp_registry.list_all()

        assert result == {}

    def test_list_all_returns_all(self, tmp_registry: AgentRegistry):
        """list_all returns all registered sessions."""
        tmp_registry.register("session-1", "agent-1")
        tmp_registry.register("session-2", "agent-2")
        tmp_registry.register("session-3", "agent-3")

        result = tmp_registry.list_all()

        assert len(result) == 3
        assert result["session-1"] == "agent-1"
        assert result["session-2"] == "agent-2"
        assert result["session-3"] == "agent-3"

    def test_file_created_on_first_write(self, tmp_path: Path):
        """Registry file is created on first register."""
        file_path = tmp_path / "new_registry.json"
        registry = AgentRegistry(file_path=file_path)

        assert not file_path.exists()

        registry.register("session-1", "agent-123")

        assert file_path.exists()

    def test_file_contains_valid_json(self, tmp_path: Path):
        """Registry file contains valid JSON."""
        file_path = tmp_path / "json_test.json"
        registry = AgentRegistry(file_path=file_path)

        registry.register("session-1", "agent-123")

        with open(file_path) as f:
            data = json.load(f)

        assert isinstance(data, dict)
        assert data["session-1"] == "agent-123"

    def test_register_overwrites_existing(self, tmp_registry: AgentRegistry):
        """Registering same session twice overwrites the agent ID."""
        tmp_registry.register("session-1", "agent-1")
        tmp_registry.register("session-1", "agent-2")

        result = tmp_registry.lookup("session-1")

        assert result == "agent-2"
