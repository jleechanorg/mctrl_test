"""Tests for genesis.config — OpenClaw configuration builder."""

import json

import pytest

from genesis.config import build_openclaw_config, validate_config


class TestBuildOpenclawConfig:
    """Tests for build_openclaw_config()."""

    def test_returns_dict(self):
        config = build_openclaw_config()
        assert isinstance(config, dict)

    def test_has_agents_defaults(self):
        config = build_openclaw_config()
        assert "agents" in config
        assert "defaults" in config["agents"]

    def test_memory_search_enabled(self):
        config = build_openclaw_config()
        mem = config["agents"]["defaults"]["memorySearch"]
        assert mem["enabled"] is True

    def test_extra_paths_included(self):
        config = build_openclaw_config()
        paths = config["agents"]["defaults"]["memorySearch"]["extraPaths"]
        assert isinstance(paths, list)
        assert len(paths) > 0
        assert any("worldarchitect" in p for p in paths)

    def test_temporal_decay_enabled(self):
        config = build_openclaw_config()
        query = config["agents"]["defaults"]["memorySearch"]["query"]
        td = query["hybrid"]["temporalDecay"]
        assert td["enabled"] is True
        assert td["halfLifeDays"] == 30

    def test_mmr_enabled(self):
        config = build_openclaw_config()
        mmr = config["agents"]["defaults"]["memorySearch"]["query"]["hybrid"]["mmr"]
        assert mmr["enabled"] is True
        assert mmr["lambda"] == 0.7

    def test_session_memory_experimental(self):
        config = build_openclaw_config()
        exp = config["agents"]["defaults"]["memorySearch"]["experimental"]
        assert exp["sessionMemory"] is True

    def test_compaction_memory_flush(self):
        config = build_openclaw_config()
        comp = config["agents"]["defaults"]["compaction"]
        assert comp["memoryFlush"]["enabled"] is True

    def test_serializable_to_json(self):
        config = build_openclaw_config()
        dumped = json.dumps(config)
        assert isinstance(dumped, str)

    def test_custom_extra_paths(self):
        custom = ["/custom/path/file.md"]
        config = build_openclaw_config(extra_paths=custom)
        paths = config["agents"]["defaults"]["memorySearch"]["extraPaths"]
        assert "/custom/path/file.md" in paths


class TestValidateConfig:
    """Tests for validate_config()."""

    def test_valid_config_passes(self):
        config = build_openclaw_config()
        assert validate_config(config) is True

    def test_missing_agents_key_fails(self):
        assert validate_config({}) is False

    def test_missing_memory_search_fails(self):
        config = {"agents": {"defaults": {}}}
        assert validate_config(config) is False

    def test_memory_search_disabled_fails(self):
        config = build_openclaw_config()
        config["agents"]["defaults"]["memorySearch"]["enabled"] = False
        assert validate_config(config) is False
