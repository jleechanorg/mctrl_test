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
    """Tests for the helper functions in multi_func.py."""

    def test_helper_a(self):
        from multi_func import helper_a
        assert helper_a(3) == 3
        assert helper_a(0) == 0
        assert helper_a(-5) == -5

    def test_helper_b(self):
        from multi_func import helper_b
        assert helper_b(3) == 4
        assert helper_b(0) == 1
        assert helper_b(-5) == -4

    def test_helper_c(self):
        from multi_func import helper_c
        assert helper_c(3) == 2
        assert helper_c(0) == -1
        assert helper_c(-5) == -6

    def test_helper_d(self):
        from multi_func import helper_d
        assert helper_d(3) == 30
        assert helper_d(0) == 0
        assert helper_d(-5) == -50

    def test_helper_e(self):
        from multi_func import epsilon
        assert epsilon(3) == 303
        assert epsilon(0) == 0
        assert epsilon(-5) == -505

    def test_helper_f(self):
        from multi_func import helper_f
        assert helper_f(3) == 3000
        assert helper_f(0) == 0
        assert helper_f(-5) == -5000


class TestMultiFunc2:
    """Tests for the functions in multi_func_2.py."""

    def test_alpha2(self):
        from multi_func_2 import alpha2
        assert alpha2(5) == 1006
        assert alpha2(0) == 1001

    def test_beta2(self):
        from multi_func_2 import beta2
        assert beta2(5) == 2005
        assert beta2(0) == 2000

    def test_gamma2(self):
        from multi_func_2 import gamma2
        assert gamma2(5) == 3005
        assert gamma2(0) == 3000

    def test_delta2(self):
        from multi_func_2 import delta2
        assert delta2(5) == 4005
        assert delta2(0) == 4000

    def test_epsilon2(self):
        from multi_func_2 import epsilon2
        assert epsilon2(5) == 5005
        assert epsilon2(0) == 5000

    def test_zeta2(self):
        from multi_func_2 import zeta2
        assert zeta2(5) == 6005
        assert zeta2(0) == 6000

