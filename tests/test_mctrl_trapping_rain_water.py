"""Focused tests for LeetCode #42 — Trapping Rain Water."""
from __future__ import annotations

import pytest

from orchestration.mctrl_test import trap


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
    assert trap([2, 2, 2, 2]) == 0


def test_ascending() -> None:
    assert trap([1, 2, 3, 4, 5]) == 0


def test_descending() -> None:
    assert trap([5, 4, 3, 2, 1]) == 0


# --- Shape patterns ---


def test_v_shape() -> None:
    # Simple valley: walls of 3, dip to 0
    assert trap([3, 0, 3]) == 3


def test_deep_valley() -> None:
    assert trap([5, 0, 0, 0, 5]) == 15


def test_multiple_pools() -> None:
    # Two separate pools
    assert trap([3, 0, 3, 0, 3]) == 6


def test_staircase_up_then_down() -> None:
    # Pyramid: 1 2 3 2 1  — no trapped water
    assert trap([1, 2, 3, 2, 1]) == 0


def test_asymmetric_walls() -> None:
    # Left wall shorter — water bounded by shorter wall
    assert trap([2, 0, 5]) == 2


def test_tall_ends_low_middle() -> None:
    assert trap([10, 0, 0, 0, 0, 10]) == 40


def test_plateau_with_dip() -> None:
    assert trap([4, 4, 0, 4, 4]) == 4


# --- Larger / stress ---


def test_alternating() -> None:
    # 0 5 0 5 0 5 — three pools of 5
    assert trap([0, 5, 0, 5, 0, 5]) == 10


def test_large_uniform_valley() -> None:
    height = [100] + [0] * 998 + [100]
    assert trap(height) == 100 * 998


@pytest.mark.parametrize(
    "height, expected",
    [
        ([0], 0),
        ([1, 0, 1], 1),
        ([2, 1, 0, 1, 2], 4),
        ([3, 1, 2, 1, 3], 5),
        ([0, 0, 0], 0),
    ],
)
def test_parametrized(height: list[int], expected: int) -> None:
    assert trap(height) == expected
