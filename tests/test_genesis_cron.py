"""Tests for genesis.cron — Cron job definition builder."""

import json

import pytest

from genesis.cron import build_curation_job, build_all_jobs, validate_cron_job


class TestBuildCurationJob:
    """Tests for build_curation_job()."""

    def test_returns_dict(self):
        job = build_curation_job()
        assert isinstance(job, dict)

    def test_has_id(self):
        job = build_curation_job()
        assert job["id"] == "genesis-memory-curation"

    def test_has_name(self):
        job = build_curation_job()
        assert "Genesis" in job["name"]
        assert "curation" in job["name"].lower()

    def test_enabled_by_default(self):
        job = build_curation_job()
        assert job["enabled"] is True

    def test_schedule_is_weekly(self):
        job = build_curation_job()
        assert job["schedule"]["kind"] == "cron"
        assert job["schedule"]["expr"] == "0 22 * * 0"  # Sunday 10PM
        assert job["schedule"]["tz"] == "America/Los_Angeles"

    def test_session_target_isolated(self):
        job = build_curation_job()
        assert job["sessionTarget"] == "isolated"

    def test_payload_is_agent_turn(self):
        job = build_curation_job()
        assert job["payload"]["kind"] == "agentTurn"
        assert "MEMORY.md" in job["payload"]["message"]
        assert "daily" in job["payload"]["message"].lower()

    def test_delivery_mode_none(self):
        job = build_curation_job()
        assert job["delivery"]["mode"] == "none"

    def test_serializable_to_json(self):
        job = build_curation_job()
        dumped = json.dumps(job)
        assert isinstance(dumped, str)

    def test_custom_schedule(self):
        job = build_curation_job(cron_expr="0 8 * * 1")
        assert job["schedule"]["expr"] == "0 8 * * 1"


class TestBuildAllJobs:
    """Tests for build_all_jobs()."""

    def test_returns_list(self):
        jobs = build_all_jobs()
        assert isinstance(jobs, list)

    def test_contains_curation_job(self):
        jobs = build_all_jobs()
        ids = [j["id"] for j in jobs]
        assert "genesis-memory-curation" in ids

    def test_all_have_ids(self):
        jobs = build_all_jobs()
        for job in jobs:
            assert "id" in job
            assert isinstance(job["id"], str)


class TestValidateCronJob:
    """Tests for validate_cron_job()."""

    def test_valid_job_passes(self):
        job = build_curation_job()
        assert validate_cron_job(job) is True

    def test_missing_id_fails(self):
        job = build_curation_job()
        del job["id"]
        assert validate_cron_job(job) is False

    def test_missing_schedule_fails(self):
        job = build_curation_job()
        del job["schedule"]
        assert validate_cron_job(job) is False

    def test_missing_payload_fails(self):
        job = build_curation_job()
        del job["payload"]
        assert validate_cron_job(job) is False

    def test_invalid_schedule_kind_fails(self):
        job = build_curation_job()
        job["schedule"]["kind"] = "invalid"
        assert validate_cron_job(job) is False

    def test_empty_dict_fails(self):
        assert validate_cron_job({}) is False
