"""Tests for merge_train_demo/multi_func_2.py and helper functions."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "merge_train_demo"))

from multi_func import helper_e
from multi_func_2 import alpha2


class TestHelperE:
    """Worker M1 owns helper_e — these verify behavior."""

    def test_helper_e_positive(self):
        assert helper_e(3) == 303

    def test_helper_e_zero(self):
        assert helper_e(0) == 0

    def test_helper_e_negative(self):
        assert helper_e(-5) == -505


class TestAlpha2:
    """Worker M1 owns alpha2 — these verify behavior."""

    def test_alpha2_positive(self):
        assert alpha2(10) == 1011

    def test_alpha2_zero(self):
        assert alpha2(0) == 1001

    def test_alpha2_negative(self):
        assert alpha2(-10) == 991
