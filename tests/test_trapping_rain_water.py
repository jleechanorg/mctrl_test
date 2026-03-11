"""Tests for LeetCode #42 — Trapping Rain Water."""
from __future__ import annotations

from orchestration.trapping_rain_water import trap


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
    assert trap([3, 4]) == 0


def test_flat() -> None:
    assert trap([3, 3, 3, 3]) == 0


def test_ascending() -> None:
    assert trap([1, 2, 3, 4, 5]) == 0


def test_descending() -> None:
    assert trap([5, 4, 3, 2, 1]) == 0


# --- Shape patterns ---

def test_v_shape() -> None:
    assert trap([3, 0, 3]) == 3


def test_deep_valley() -> None:
    assert trap([5, 0, 0, 0, 5]) == 15


def test_asymmetric_walls() -> None:
    # Water limited by the shorter wall (3)
    assert trap([3, 0, 5]) == 3


def test_multiple_pools() -> None:
    # Two separate pools: between 3..2 and 2..3
    assert trap([3, 0, 2, 0, 3]) == 7


def test_staircase_down_up() -> None:
    assert trap([4, 3, 2, 1, 2, 3, 4]) == 9


def test_plateau_with_dip() -> None:
    assert trap([5, 5, 1, 5, 5]) == 4


# --- Stress / large input ---

def test_large_alternating() -> None:
    # [0, 10, 0, 10, ...] — each interior 0 traps 10
    n = 10_000
    height = [10 * (i % 2) for i in range(n)]
    # Interior zeros: indices 0, 2, 4, ... but first (0) and last trap nothing
    # if n is even, last element is 0 and traps nothing
    expected = 10 * ((n // 2) - 1)
    assert trap(height) == expected


def test_all_zeros() -> None:
    assert trap([0, 0, 0, 0]) == 0


def test_single_peak() -> None:
    assert trap([0, 0, 5, 0, 0]) == 0
