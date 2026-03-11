"""Focused tests for LeetCode #42 — Trapping Rain Water."""

from __future__ import annotations

import pytest

from trapping_rain_water import trap


# -- LeetCode examples -------------------------------------------------------

def test_example_1() -> None:
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6


def test_example_2() -> None:
    assert trap([4, 2, 0, 3, 2, 5]) == 9


# -- Edge cases ---------------------------------------------------------------

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


# -- Structural patterns ------------------------------------------------------

def test_v_shape() -> None:
    # [3,1,0,1,3] → water: 2+3+2 = 7
    assert trap([3, 1, 0, 1, 3]) == 7


def test_single_trap() -> None:
    # One unit of water between two bars
    assert trap([1, 0, 1]) == 1


def test_deep_well() -> None:
    # [5, 0, 0, 0, 5] → 5*3 = 15
    assert trap([5, 0, 0, 0, 5]) == 15


def test_asymmetric_walls() -> None:
    # Water level limited by shorter wall
    # [3, 0, 2] → min(3,2)-0 = 2
    assert trap([3, 0, 2]) == 2


def test_multiple_pools() -> None:
    # Two separate pools
    # [2,0,2,0,2] → pool1=2, pool2=2 → 4
    assert trap([2, 0, 2, 0, 2]) == 4


def test_staircase_and_back() -> None:
    # [0,1,2,3,2,1,0] — pyramid, no water trapped
    assert trap([0, 1, 2, 3, 2, 1, 0]) == 0


def test_plateau_with_dip() -> None:
    # [4,4,1,4,4] → trapped = 3
    assert trap([4, 4, 1, 4, 4]) == 3


# -- Stress / large input -----------------------------------------------------

def test_large_alternating() -> None:
    # [5,0,5,0,5,...] for 1000 bars → 499 gaps of 5 each
    n = 1000
    height = [5 if i % 2 == 0 else 0 for i in range(n)]
    assert trap(height) == 5 * (n // 2 - 1)


def test_large_single_valley() -> None:
    # 10000 zeros flanked by height-100 walls
    wall = 100
    width = 10000
    height = [wall] + [0] * width + [wall]
    assert trap(height) == wall * width


def test_all_zeros() -> None:
    assert trap([0, 0, 0, 0, 0]) == 0


def test_constraint_max_height() -> None:
    # max height per constraints is 10^5
    assert trap([100000, 0, 100000]) == 100000
