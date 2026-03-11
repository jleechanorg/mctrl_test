"""Focused tests for LeetCode #42 — Trapping Rain Water."""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "leet_code"))

from trapping_rain_water import trap


# --- LeetCode examples ---

def test_example_1() -> None:
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6


def test_example_2() -> None:
    assert trap([4, 2, 0, 3, 2, 5]) == 9


# --- Edge cases ---

def test_empty() -> None:
    assert trap([]) == 0


def test_single_bar() -> None:
    assert trap([5]) == 0


def test_two_bars() -> None:
    assert trap([3, 7]) == 0


def test_flat() -> None:
    assert trap([3, 3, 3, 3]) == 0


def test_ascending() -> None:
    assert trap([1, 2, 3, 4, 5]) == 0


def test_descending() -> None:
    assert trap([5, 4, 3, 2, 1]) == 0


# --- Structural patterns ---

def test_v_shape() -> None:
    # [3, 0, 3] traps 3 units in the valley
    assert trap([3, 0, 3]) == 3


def test_w_shape() -> None:
    # [3, 0, 2, 0, 3] — pos1: 3, pos2: 1, pos3: 3 = 7
    assert trap([3, 0, 2, 0, 3]) == 7


def test_single_puddle() -> None:
    # [2, 0, 2] — simple puddle
    assert trap([2, 0, 2]) == 2


def test_uneven_walls() -> None:
    # [5, 0, 3] — bounded by shorter wall
    assert trap([5, 0, 3]) == 3


def test_tall_spike_middle() -> None:
    # No water trapped on a spike: [0, 5, 0]
    assert trap([0, 5, 0]) == 0


def test_plateau_with_dip() -> None:
    assert trap([4, 4, 1, 4, 4]) == 3


def test_staircase_up_down() -> None:
    # [0,1,2,3,2,1,0] — pyramid, no pooling
    assert trap([0, 1, 2, 3, 2, 1, 0]) == 0


def test_large_values() -> None:
    # Constraint boundary: height up to 10^5
    assert trap([100000, 0, 100000]) == 100000


def test_long_flat_valley() -> None:
    # [5, 0, 0, 0, 0, 5] — 4 units wide, 5 deep
    assert trap([5, 0, 0, 0, 0, 5]) == 20


def test_multiple_pools() -> None:
    # [3, 0, 1, 0, 3] — pos1: 3, pos2: 2, pos3: 3 = 8
    assert trap([3, 0, 1, 0, 3]) == 8
