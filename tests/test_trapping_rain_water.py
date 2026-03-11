"""Focused tests for LeetCode #42 — Trapping Rain Water."""
from __future__ import annotations

import pytest

from orchestration.trapping_rain_water import trap


# --- canonical examples from LeetCode ---

def test_leetcode_example_1() -> None:
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6


def test_leetcode_example_2() -> None:
    assert trap([4, 2, 0, 3, 2, 5]) == 9


# --- edge cases ---

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


# --- structural patterns ---

def test_v_shape() -> None:
    # [3, 0, 3] traps 3 units in the middle
    assert trap([3, 0, 3]) == 3


def test_deep_valley() -> None:
    # [5, 0, 0, 0, 5] traps 5*3 = 15
    assert trap([5, 0, 0, 0, 5]) == 15


def test_uneven_walls() -> None:
    # [3, 0, 5] — bounded by shorter wall (3), traps 3
    assert trap([3, 0, 5]) == 3


def test_multiple_pools() -> None:
    # Two separate pools
    assert trap([2, 0, 2, 0, 2]) == 4


def test_staircase_down_then_up() -> None:
    # [4, 3, 2, 1, 2, 3, 4] — symmetric staircase
    assert trap([4, 3, 2, 1, 2, 3, 4]) == 9


def test_plateau_with_dip() -> None:
    assert trap([5, 5, 1, 5, 5]) == 4


def test_all_zeros() -> None:
    assert trap([0, 0, 0, 0]) == 0


def test_large_values() -> None:
    # Tall walls, deep valley
    assert trap([100000, 0, 100000]) == 100000


# --- stress / correctness against brute force ---

def _trap_bruteforce(height: list[int]) -> int:
    """O(n^2) reference implementation for validation."""
    n = len(height)
    if n < 3:
        return 0
    water = 0
    for i in range(1, n - 1):
        left_max = max(height[:i + 1])
        right_max = max(height[i:])
        water += min(left_max, right_max) - height[i]
    return water


@pytest.mark.parametrize("height", [
    [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],
    [4, 2, 0, 3, 2, 5],
    [1, 0, 1],
    [2, 1, 0, 1, 3],
    [3, 1, 2, 4, 0, 1, 3, 2],
    [0] * 10,
    list(range(10)) + list(range(10, -1, -1)),
])
def test_matches_bruteforce(height: list[int]) -> None:
    assert trap(height) == _trap_bruteforce(height)
