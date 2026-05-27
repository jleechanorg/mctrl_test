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
    """Worker B owns beta — these verify Worker B's implementation (x*x+100)."""

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
