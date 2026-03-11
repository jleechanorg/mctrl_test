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

def test_simple_valley() -> None:
    # 3 _ 3  → 3 units trapped in the middle
    assert trap([3, 0, 3]) == 3


def test_deep_valley() -> None:
    assert trap([5, 0, 0, 0, 5]) == 15


def test_asymmetric_valley() -> None:
    # Water bounded by shorter wall (2)
    assert trap([2, 0, 5]) == 2


def test_staircase_up_down() -> None:
    # 0,1,2,3,2,1,0 — pyramid, no trapped water
    assert trap([0, 1, 2, 3, 2, 1, 0]) == 0


def test_multiple_pools() -> None:
    # Two separate pools
    assert trap([3, 0, 3, 0, 3]) == 6


def test_nested_valleys() -> None:
    # [5,2,1,2,1,5]: water = (5-2)+(5-1)+(5-2)+(5-1) = 3+4+3+4 = 14
    assert trap([5, 2, 1, 2, 1, 5]) == 14


# --- Stress / boundary ---

def test_large_uniform() -> None:
    assert trap([1] * 20000) == 0


def test_large_single_valley() -> None:
    # tall walls on edges, zeros in between
    n = 20000
    height = [100000] + [0] * (n - 2) + [100000]
    assert trap(height) == 100000 * (n - 2)


def test_all_zeros() -> None:
    assert trap([0, 0, 0, 0]) == 0


def test_single_peak() -> None:
    assert trap([0, 0, 5, 0, 0]) == 0
