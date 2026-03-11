"""Focused tests for LeetCode #42 — Trapping Rain Water."""

from __future__ import annotations

import pytest

from leet_code.trapping_rain_water import trap


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


def test_flat_surface() -> None:
    assert trap([3, 3, 3, 3]) == 0


def test_ascending() -> None:
    assert trap([1, 2, 3, 4, 5]) == 0


def test_descending() -> None:
    assert trap([5, 4, 3, 2, 1]) == 0


# --- Shape patterns ---

def test_single_valley() -> None:
    # 3 _ 3  ->  1 unit trapped
    assert trap([3, 0, 3]) == 3


def test_asymmetric_valley() -> None:
    # 2 _ 5  ->  water bounded by shorter wall (2), so 2 units
    assert trap([2, 0, 5]) == 2


def test_multiple_valleys() -> None:
    # Two separate pools
    assert trap([3, 0, 3, 0, 3]) == 6


def test_staircase_up_down() -> None:
    # 0 1 2 3 2 1 0  -> no water (pyramid)
    assert trap([0, 1, 2, 3, 2, 1, 0]) == 0


def test_nested_valleys() -> None:
    # Deep valley with a bump in the middle
    assert trap([5, 0, 2, 0, 5]) == 13


def test_wide_plateau() -> None:
    assert trap([4, 1, 1, 1, 4]) == 9


# --- Stress / boundary ---

def test_large_uniform() -> None:
    """20k bars, all same height — no water."""
    assert trap([7] * 20_000) == 0


def test_large_v_shape() -> None:
    """V-shape: descend then ascend. Water = sum of (max - h) for interior."""
    n = 10_000
    height = list(range(n, 0, -1)) + list(range(1, n + 1))
    # Each side mirrors; water at position i from center = n - height[i]
    # Interior positions (indices 1 to 2n-2) each hold (n - height) water
    expected = sum(n - h for h in height[1:-1])
    assert trap(height) == expected


def test_zeros_between_walls() -> None:
    assert trap([10] + [0] * 100 + [10]) == 1000
