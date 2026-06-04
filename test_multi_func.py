"""Tests for merge_train_demo/multi_func.py — symbol-level lock demo."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "merge_train_demo"))

from multi_func import alpha, beta, gamma, delta


class TestAlpha:
    """Worker A owns alpha — these verify baseline behavior."""

    def test_positive(self):
        assert alpha(3) == 6

    def test_zero(self):
        assert alpha(0) == 0

    def test_negative(self):
        assert alpha(-4) == -8


class TestBeta:
    """Worker B2 owns beta — returns x² + 100."""

    def test_positive(self):
        assert beta(3) == 109

    def test_zero(self):
        assert beta(0) == 100

    def test_negative(self):
        assert beta(-3) == 109

    def test_one(self):
        assert beta(1) == 101


class TestGamma:
    """Unreserved — verify baseline."""

    def test_positive(self):
        assert gamma(2) == 8

    def test_zero(self):
        assert gamma(0) == 0

    def test_negative(self):
        assert gamma(-2) == -8

    def test_one(self):
        assert gamma(1) == 1


class TestDelta:
    """Worker C2 owns delta — verified in PR #194."""

    def test_positive(self):
        assert delta(5) == -6

    def test_zero(self):
        assert delta(0) == -1

    def test_negative(self):
        assert delta(-5) == 4

    def test_one(self):
        assert delta(1) == -2

    def test_minus_one(self):
        assert delta(-1) == 0

    def test_large(self):
        assert delta(1000) == -1001


class TestLockReservation:
    """Programmatic verification of domain lock reservation and isolation."""

    def test_locks_exist(self):
        import json
        log_path = os.path.join(os.path.dirname(__file__), "pr_domain_locks.jsonl")
        assert os.path.exists(log_path)
        
        expected_locks = {
            193: "beta",
            192: "alpha",
            194: "delta"
        }
        found_locks = {}
        
        with open(log_path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("domain") == "demo" and entry.get("status") == "active":
                    pr = entry.get("pr")
                    symbols = entry.get("symbols", [])
                    if pr in expected_locks and expected_locks[pr] in symbols:
                        found_locks[pr] = expected_locks[pr]
        
        for pr, symbol in expected_locks.items():
            assert pr in found_locks, f"Active reservation for PR #{pr} holding symbol '{symbol}' not found in pr_domain_locks.jsonl"

    def test_json_parsing_propagates_other_exceptions(self):
        import unittest.mock as mock
        import json
        import pytest

        class CustomException(Exception):
            pass

        log_path = os.path.join(os.path.dirname(__file__), "pr_domain_locks.jsonl")
        
        with mock.patch("json.loads", side_effect=CustomException("propagate me")):
            with pytest.raises(CustomException):
                with open(log_path, "r") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        try:
                            entry = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if entry.get("domain") == "demo" and entry.get("status") == "active":
                            pr = entry.get("pr")
                            symbols = entry.get("symbols", [])
                            if pr in {193: "beta"} and "beta" in symbols:
                                pass

    def test_domain_lock_check_programmatic(self):
        try:
            from merge_train.domain_lock import load_registry, LockLog, check
        except ModuleNotFoundError:
            import pytest
            pytest.skip("merge_train module not installed in this environment")
        
        registry_path = os.path.join(os.path.dirname(__file__), "merge_train_demo", "file_domains.yaml")
        log_path = os.path.join(os.path.dirname(__file__), "pr_domain_locks.jsonl")
        
        registry = load_registry(registry_path)
        log = LockLog(log_path)
        
        target_file = "merge_train_demo/multi_func.py"
        
        # 1. Verification for Owner (PR 193 owns beta)
        res_beta_owner = check(
            log, registry,
            files=[target_file],
            pr=193,
            touched_symbols_by_path={target_file: {"beta"}}
        )
        assert res_beta_owner.ok, "Beta should be free to modify for PR #193"
        
        # 2. Verification for Non-Owner (PR 999 blocks on beta)
        res_beta_blocked = check(
            log, registry,
            files=[target_file],
            pr=999,
            touched_symbols_by_path={target_file: {"beta"}}
        )
        assert not res_beta_blocked.ok, "Beta should be blocked for PR #999"
        assert res_beta_blocked.held[0][1].pr == 193, "Beta should be held by PR #193"
