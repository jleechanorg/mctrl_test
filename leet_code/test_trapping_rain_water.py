"""Focused tests for LeetCode #42 — Trapping Rain Water."""

from __future__ import annotations

import pytest
from trapping_rain_water import trap


# --- LeetCode examples ---

def test_example_1() -> None:
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6


def test_example_2() -> None:
    assert trap([4, 2, 0, 3, 2, 5]) == 9


# --- Edge cases ---

def test_empty_list() -> None:
    assert trap([]) == 0


def test_single_bar() -> None:
    assert trap([5]) == 0


def test_two_bars() -> None:
    assert trap([3, 7]) == 0


def test_flat_surface() -> None:
    assert trap([3, 3, 3, 3]) == 0


def test_ascending() -> None:
    assert trap([1, 2, 3, 4, 5]) == 0


def test_descending() -> None:
    assert trap([5, 4, 3, 2, 1]) == 0


# --- Structural patterns ---

def test_single_valley() -> None:
    # 3 _ _ 3  → 2 units in each of the 2 middle slots = 6
    assert trap([3, 1, 1, 3]) == 4


def test_deep_v() -> None:
    assert trap([5, 0, 5]) == 5


def test_multiple_valleys() -> None:
    # Two separate pools
    assert trap([3, 0, 3, 0, 3]) == 6


def test_staircase_down_up() -> None:
    assert trap([4, 3, 2, 1, 2, 3, 4]) == 9


def test_tall_walls_shallow_middle() -> None:
    assert trap([100, 0, 100]) == 100


def test_asymmetric_walls() -> None:
    # Water bounded by the shorter wall (2)
    assert trap([2, 0, 5]) == 2


def test_plateau_with_dip() -> None:
    assert trap([5, 5, 1, 5, 5]) == 4


# --- Stress / boundary ---

def test_large_uniform() -> None:
    assert trap([0] * 20000) == 0


def test_large_bowl() -> None:
    n = 20000
    height = list(range(n // 2, 0, -1)) + list(range(1, n // 2 + 1))
    # Symmetric bowl: each side descends from n//2 to 1 then ascends back
    expected = sum(n // 2 - h for h in height)
    assert trap(height) == expected


def test_all_zeros() -> None:
    assert trap([0, 0, 0]) == 0


def test_spike() -> None:
    assert trap([0, 10, 0]) == 0


def test_alternating() -> None:
    # 2,0,2,0,2 → 2 units in each of the 2 gaps = 4
    assert trap([2, 0, 2, 0, 2]) == 4
