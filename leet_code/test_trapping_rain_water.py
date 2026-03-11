"""Tests for LeetCode #42 — Trapping Rain Water."""

from __future__ import annotations

import pytest
from trapping_rain_water import trap


# --- LeetCode examples ---

def test_example_1() -> None:
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6


def test_example_2() -> None:
    assert trap([4, 2, 0, 3, 2, 5]) == 9


# --- Edge cases ---

def test_empty_single_double() -> None:
    assert trap([]) == 0
    assert trap([5]) == 0
    assert trap([3, 7]) == 0


def test_flat() -> None:
    assert trap([3, 3, 3, 3]) == 0


def test_ascending() -> None:
    assert trap([1, 2, 3, 4, 5]) == 0


def test_descending() -> None:
    assert trap([5, 4, 3, 2, 1]) == 0


# --- Structural patterns ---

def test_single_valley() -> None:
    # |   |
    # | _ |  height=[3,0,3] → water=3
    assert trap([3, 0, 3]) == 3


def test_asymmetric_walls() -> None:
    # tall left, short right: water bounded by shorter wall
    assert trap([5, 0, 2]) == 2


def test_staircase_pool() -> None:
    # [3,1,2,1,3] → indices 1-3 trapped
    # min(3,3)-1 + min(3,3)-2 + min(3,3)-1 = 2+1+2 = 5
    assert trap([3, 1, 2, 1, 3]) == 5


def test_multiple_pools() -> None:
    # Two separate pools
    assert trap([2, 0, 2, 0, 2]) == 4


def test_large_plateau() -> None:
    assert trap([0, 5, 5, 5, 0]) == 0


def test_all_zeros() -> None:
    assert trap([0, 0, 0, 0]) == 0


# --- Stress / scale ---

def test_large_v_shape() -> None:
    # V-shape: [10000, 9999, ..., 1, 0, 1, ..., 9999, 10000]
    n = 10_000
    left = list(range(n, -1, -1))
    right = list(range(1, n + 1))
    height = left + right
    # Water at position i from left side: n - (n-i) = i for i in [0..n]
    # Total = sum(i - height[i] for each side) = sum(0..n-1) * 2 = n*(n-1)
    # Actually: left_max at pos i (0-indexed) = n (first element), height[i]=n-i
    # water contribution = n - (n-i) - 0 ... let me just compute expected
    expected = sum(max(0, min(max(left[:i+1]), max(right[i-len(left):] if i >= len(left) else left[i:])) - height[i]) for i, height_i in enumerate(height))
    # Simpler: just trust the two-pointer and verify against brute force
    expected = _brute_force_trap(height)
    assert trap(height) == expected


def test_large_random_deterministic() -> None:
    """Deterministic pseudo-random heights, cross-checked against brute force."""
    import random
    rng = random.Random(42)
    height = [rng.randint(0, 100_000) for _ in range(20_000)]
    assert trap(height) == _brute_force_trap(height)


# --- Brute-force reference for cross-checking ---

def _brute_force_trap(height: list[int]) -> int:
    """O(n) prefix/suffix max approach as reference implementation."""
    n = len(height)
    if n < 3:
        return 0
    left_max = [0] * n
    right_max = [0] * n
    left_max[0] = height[0]
    for i in range(1, n):
        left_max[i] = max(left_max[i - 1], height[i])
    right_max[-1] = height[-1]
    for i in range(n - 2, -1, -1):
        right_max[i] = max(right_max[i + 1], height[i])
    return sum(min(left_max[i], right_max[i]) - height[i] for i in range(n))
