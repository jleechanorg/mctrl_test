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
    """Worker A3 should NOT define helpers B through F to prevent symbol pollution/overlap."""

    def test_no_extra_helpers_defined(self):
        import multi_func
        # These helpers should not be present in Worker A3's scope
        assert not hasattr(multi_func, "helper_b"), "helper_b should be defined by Worker B3"
        assert not hasattr(multi_func, "helper_c"), "helper_c should be defined by Worker C3"
        assert not hasattr(multi_func, "helper_d"), "helper_d should not be defined yet"
        assert not hasattr(multi_func, "helper_e"), "helper_e should not be defined yet"
        assert not hasattr(multi_func, "helper_f"), "helper_f should not be defined yet"
