"""Tests for merge_train_demo/multi_func.py — symbol-level lock demo."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "merge_train_demo"))

from multi_func import alpha, beta, gamma, delta, helper_a


class TestAlpha:
    """Worker A owns alpha — these verify baseline behavior."""

    def test_positive(self):
        assert alpha(3) == 7

    def test_zero(self):
        assert alpha(0) == 1

    def test_negative(self):
        assert alpha(-4) == -7


class TestBeta:
    """Worker B owns beta — these verify baseline behavior."""

    def test_positive(self):
        assert beta(3) == 9

    def test_zero(self):
        assert beta(0) == 0

    def test_negative(self):
        assert beta(-3) == 9

    def test_one(self):
        assert beta(1) == 1


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
    """Worker C2 owns delta — primary test surface for this PR."""

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


class TestHelperA:
    """Worker A3 owns helper_a — these verify baseline behavior."""

    def test_positive(self):
        assert helper_a(3) == 10

    def test_zero(self):
        assert helper_a(0) == 7

    def test_negative(self):
        assert helper_a(-4) == 3


class TestUnreservedHelpers:
    """Worker A3 should NOT define helpers B through F to prevent symbol pollution/overlap.

    We use conditional assertions for B3/C3 symbols to ensure they pass on A3's isolated
    branch (where they are absent) and also when integrated/merged with companion PRs
    (where they are present with B3/C3 metadata).
    """

    def test_no_extra_helpers_defined(self):
        import multi_func
        # If helper_b is defined, it must belong to Worker B3 (not accidentally defined by A3)
        if hasattr(multi_func, "helper_b"):
            doc = multi_func.helper_b.__doc__ or ""
            assert "Worker B3" in doc, f"helper_b exists but docstring '{doc}' does not mention Worker B3"

        # If helper_c is defined, it must belong to Worker C3 (not accidentally defined by A3)
        if hasattr(multi_func, "helper_c"):
            doc = multi_func.helper_c.__doc__ or ""
            assert "Worker C3" in doc, f"helper_c exists but docstring '{doc}' does not mention Worker C3"

        # Spare slots should not be defined yet
        assert not hasattr(multi_func, "helper_d"), "helper_d should not be defined yet"
        assert not hasattr(multi_func, "helper_e"), "helper_e should not be defined yet"
        assert not hasattr(multi_func, "helper_f"), "helper_f should not be defined yet"

    def test_conditional_assertions_simulate(self):
        import multi_func
        import pytest

        # Test case 1: Helper B3 is defined with the correct docstring (simulating merge integration)
        class DummyB3:
            """Worker B3 helper"""
            pass

        multi_func.helper_b = DummyB3
        try:
            # Should not raise exception
            self.test_no_extra_helpers_defined()
        finally:
            if hasattr(multi_func, "helper_b"):
                delattr(multi_func, "helper_b")

        # Test case 2: Helper is defined but with a polluted/incorrect docstring (should raise AssertionError)
        class DummyInvalid:
            """Polluted helper"""
            pass

        multi_func.helper_b = DummyInvalid
        try:
            with pytest.raises(AssertionError, match="does not mention Worker B3"):
                self.test_no_extra_helpers_defined()
        finally:
            if hasattr(multi_func, "helper_b"):
                delattr(multi_func, "helper_b")


