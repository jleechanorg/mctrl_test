"""Focused tests for LeetCode #42 — Trapping Rain Water."""

from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "leet_code"))

from trapping_rain_water import trap


# --- LeetCode examples ---

def test_example_1():
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6


def test_example_2():
    assert trap([4, 2, 0, 3, 2, 5]) == 9


# --- Edge cases ---

def test_empty():
    assert trap([]) == 0


def test_single_bar():
    assert trap([5]) == 0


def test_two_bars():
    assert trap([3, 7]) == 0


def test_flat():
    assert trap([3, 3, 3, 3]) == 0


def test_ascending():
    assert trap([1, 2, 3, 4, 5]) == 0


def test_descending():
    assert trap([5, 4, 3, 2, 1]) == 0


# --- Structural patterns ---

def test_v_shape():
    # [3, 0, 3] traps 3 units in the middle
    assert trap([3, 0, 3]) == 3


def test_deep_valley():
    # [5, 0, 0, 0, 5] traps 5*3 = 15
    assert trap([5, 0, 0, 0, 5]) == 15


def test_asymmetric_valley():
    # [3, 0, 5] — bounded by shorter side (3), traps 3
    assert trap([3, 0, 5]) == 3


def test_multiple_valleys():
    # [3,0,3,0,3] — two valleys of 3 each
    assert trap([3, 0, 3, 0, 3]) == 6


def test_staircase_up_down():
    # [0,1,2,3,2,1,0] — pyramid, no water trapped
    assert trap([0, 1, 2, 3, 2, 1, 0]) == 0


def test_plateau_with_dip():
    # [4,4,0,4,4] — dip of depth 4
    assert trap([4, 4, 0, 4, 4]) == 4


def test_all_zeros():
    assert trap([0, 0, 0, 0]) == 0


def test_large_values():
    # [100000, 0, 100000]
    assert trap([100000, 0, 100000]) == 100000


# --- Regression / tricky ---

def test_alternating():
    # [0,1,0,1,0,1,0] — small pools between each pair of 1s
    assert trap([0, 1, 0, 1, 0, 1, 0]) == 2


def test_nested_valleys():
    # [5,2,1,2,1,5] — water fills to level 5
    # positions: 5 2 1 2 1 5
    # water:     0 3 4 3 4 0 = 14
    assert trap([5, 2, 1, 2, 1, 5]) == 14
