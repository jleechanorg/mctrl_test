"""Tests for LeetCode #42 — Trapping Rain Water."""
from __future__ import annotations

import pytest

from orchestration.trapping_rain_water import trap


# --- LeetCode examples ---


def test_leetcode_example_1() -> None:
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6


def test_leetcode_example_2() -> None:
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


# --- Shape patterns ---


def test_valley() -> None:
    # Simple V-shape: walls of 3, valley at 0
    assert trap([3, 0, 3]) == 3


def test_deep_valley() -> None:
    assert trap([5, 0, 0, 0, 5]) == 15


def test_asymmetric_walls() -> None:
    # Water limited by shorter wall
    assert trap([3, 0, 5]) == 3


def test_staircase_up_then_down() -> None:
    # Pyramid — no water trapped
    assert trap([1, 2, 3, 2, 1]) == 0


def test_multiple_valleys() -> None:
    # Two separate pools
    assert trap([3, 0, 3, 0, 3]) == 6


def test_nested_valleys() -> None:
    assert trap([5, 2, 1, 2, 5]) == 10


# --- Stress / large inputs ---


def test_large_alternating() -> None:
    # 10k bars alternating 0 and 100000
    height = [100000 if i % 2 == 0 else 0 for i in range(10000)]
    # Each 0-valley between two 100000-walls traps 100000 units
    assert trap(height) == 100000 * 4999


def test_large_single_pool() -> None:
    # Two tall walls with 10k zeros between them
    height = [100000] + [0] * 10000 + [100000]
    assert trap(height) == 100000 * 10000


# --- All zeros ---


def test_all_zeros() -> None:
    assert trap([0, 0, 0, 0]) == 0


# --- Plateau with dip ---


def test_plateau_with_dip() -> None:
    assert trap([4, 4, 0, 4, 4]) == 4


@pytest.mark.parametrize(
    "height, expected",
    [
        ([2, 0, 2], 2),
        ([1, 0, 2, 0, 1], 2),
        ([0, 7, 1, 4, 6], 7),
        ([6, 4, 2, 0, 3, 2, 0, 3, 1, 4, 5, 3, 2, 7, 5, 3, 0, 1, 2, 1, 3, 4, 6, 8, 1, 3], 83),
    ],
    ids=["symmetric_small", "asymmetric_small", "left_heavy", "complex_terrain"],
)
def test_parametrized(height: list[int], expected: int) -> None:
    assert trap(height) == expected
