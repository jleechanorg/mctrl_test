"""Tests for merge_train_demo/multi_func.py — symbol-level lock demo."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "merge_train_demo"))

from multi_func import alpha, beta, gamma, delta
from multi_func_2 import alpha2, beta2, gamma2, delta2, epsilon2, zeta2


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


class TestMultiFunc2:
    """Worker M2 owns multi_func_2 functions — verify all of them."""

    def test_alpha2(self):
        assert alpha2(5) == 1005

    def test_beta2_green(self):
        # Green phase of TDD
        assert beta2(3) == 2004

    def test_gamma2(self):
        assert gamma2(10) == 3010

    def test_delta2(self):
        assert delta2(0) == 4000

    def test_epsilon2(self):
        assert epsilon2(-5) == 4995

    def test_zeta2(self):
        assert zeta2(100) == 6100
