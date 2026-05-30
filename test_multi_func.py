"""Tests for merge_train_demo/multi_func.py — symbol-level lock demo."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "merge_train_demo"))

from multi_func import alpha, beta, gamma, delta, helper_a, helper_b, helper_c, helper_d, helper_e, helper_f



class TestAlpha:
    """Worker A owns alpha — these verify baseline behavior."""

    def test_positive(self):
        assert alpha(3) == 6

    def test_zero(self):
        assert alpha(0) == 0

    def test_negative(self):
        assert alpha(-4) == -8


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


class TestHelpers:
    """Worker B3 / A3 / C3 owns helper functions — verify behavior."""

    def test_helper_a(self):
        assert helper_a(5) == 5
        assert helper_a(0) == 0
        assert helper_a(-10) == -10

    def test_helper_b(self):
        assert helper_b(3) == 4
        assert helper_b(0) == 1
        assert helper_b(-3) == -2

    def test_helper_c(self):
        assert helper_c(5) == 4
        assert helper_c(0) == -1
        assert helper_c(-5) == -6

    def test_helper_d(self):
        assert helper_d(2) == 20
        assert helper_d(0) == 0

    def test_helper_e(self):
        assert helper_e(2) == 200
        assert helper_e(0) == 0

    def test_helper_f(self):
        assert helper_f(2) == 2000
        assert helper_f(0) == 0


