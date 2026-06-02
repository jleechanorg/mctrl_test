"""Tests for merge_train_demo/multi_func_2.py and helper functions."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "merge_train_demo"))

from multi_func import epsilon
from multi_func_2 import alpha2


class TestEpsilon:
    """Worker M1 owns epsilon — these verify behavior."""

    def test_epsilon_positive(self):
        assert epsilon(3) == 303

    def test_epsilon_zero(self):
        assert epsilon(0) == 0

    def test_epsilon_negative(self):
        assert epsilon(-5) == -505


class TestAlpha2:
    """Worker M1 owns alpha2 — these verify behavior."""

    def test_alpha2_positive(self):
        assert alpha2(10) == 1011

    def test_alpha2_zero(self):
        assert alpha2(0) == 1001

    def test_alpha2_negative(self):
        assert alpha2(-10) == 991
