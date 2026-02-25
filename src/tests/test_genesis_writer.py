"""Tests for genesis.writer — disk writer for OpenClaw config files."""

import json
import os
import tempfile

import pytest

from genesis.writer import (
    write_memory_md,
    write_openclaw_config,
    write_cron_jobs,
    write_all,
)
from genesis.config import build_openclaw_config
from genesis.memory import generate_seed_content
from genesis.cron import build_all_jobs


class TestWriteMemoryMd:
    def test_writes_file(self, tmp_path):
        target = tmp_path / "workspace" / "MEMORY.md"
        write_memory_md(str(target))
        assert target.exists()
        content = target.read_text()
        assert content.startswith("# MEMORY.md")

    def test_creates_parent_dirs(self, tmp_path):
        target = tmp_path / "deep" / "nested" / "MEMORY.md"
        write_memory_md(str(target))
        assert target.exists()

    def test_custom_content(self, tmp_path):
        target = tmp_path / "MEMORY.md"
        write_memory_md(str(target), goals=["Custom goal"])
        content = target.read_text()
        assert "Custom goal" in content

    def test_no_overwrite_by_default(self, tmp_path):
        target = tmp_path / "MEMORY.md"
        target.write_text("existing content")
        write_memory_md(str(target), overwrite=False)
        assert target.read_text() == "existing content"

    def test_overwrite_when_forced(self, tmp_path):
        target = tmp_path / "MEMORY.md"
        target.write_text("existing content")
        write_memory_md(str(target), overwrite=True)
        assert target.read_text().startswith("# MEMORY.md")


class TestWriteOpenclawConfig:
    def test_writes_json(self, tmp_path):
        target = tmp_path / "openclaw.json"
        write_openclaw_config(str(target))
        assert target.exists()
        data = json.loads(target.read_text())
        assert "agents" in data

    def test_valid_json(self, tmp_path):
        target = tmp_path / "openclaw.json"
        write_openclaw_config(str(target))
        # Should not raise
        data = json.loads(target.read_text())
        assert data["agents"]["defaults"]["memorySearch"]["enabled"] is True

    def test_creates_parent_dirs(self, tmp_path):
        target = tmp_path / "nested" / "openclaw.json"
        write_openclaw_config(str(target))
        assert target.exists()


class TestWriteCronJobs:
    def test_writes_json(self, tmp_path):
        target = tmp_path / "jobs.json"
        write_cron_jobs(str(target))
        assert target.exists()
        data = json.loads(target.read_text())
        assert isinstance(data, list)
        assert len(data) > 0

    def test_contains_curation_job(self, tmp_path):
        target = tmp_path / "jobs.json"
        write_cron_jobs(str(target))
        data = json.loads(target.read_text())
        ids = [j["id"] for j in data]
        assert "genesis-memory-curation" in ids


class TestWriteAll:
    def test_writes_all_files(self, tmp_path):
        workspace = str(tmp_path / "workspace")
        config = str(tmp_path / "openclaw.json")
        cron = str(tmp_path / "cron" / "jobs.json")
        results = write_all(
            memory_path=workspace + "/MEMORY.md",
            config_path=config,
            cron_path=cron,
        )
        assert results["memory"] is True
        assert results["config"] is True
        assert results["cron"] is True
        assert os.path.exists(workspace + "/MEMORY.md")
        assert os.path.exists(config)
        assert os.path.exists(cron)
