"""Tests for LeetCode #42 — Trapping Rain Water.

Focused test suite covering edge cases, LeetCode examples, and stress patterns.
"""

from __future__ import annotations

import pytest

from orchestration.trapping_rain_water import trap


# --- LeetCode official examples ---

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


# --- Simple patterns ---

def test_v_shape() -> None:
    assert trap([3, 0, 3]) == 3


def test_valley() -> None:
    assert trap([5, 0, 0, 0, 5]) == 15


def test_asymmetric_valley() -> None:
    # Water limited by shorter wall (2), fills 3 slots: 2+1+2 = 5
    assert trap([3, 1, 2, 0, 2]) == 3


def test_single_dip() -> None:
    assert trap([2, 0, 2]) == 2


def test_multiple_valleys() -> None:
    # [3,0,3,0,3] -> 3 trapped in first valley + 3 in second = 6
    assert trap([3, 0, 3, 0, 3]) == 6


# --- Tall peaks ---

def test_tall_peak_in_middle() -> None:
    assert trap([0, 100, 0]) == 0


def test_tall_walls_shallow_valley() -> None:
    assert trap([100, 1, 100]) == 99


# --- Staircase patterns ---

def test_staircase_up_down() -> None:
    assert trap([0, 1, 2, 3, 2, 1, 0]) == 0


def test_staircase_with_dip() -> None:
    # [3, 2, 1, 2, 3] -> water: 0 + 1 + 2 + 1 + 0 = 4
    assert trap([3, 2, 1, 2, 3]) == 4


# --- All zeros ---

def test_all_zeros() -> None:
    assert trap([0, 0, 0, 0]) == 0


# --- Stress / larger inputs ---

def test_large_valley() -> None:
    # Two walls of height 1000 with 998 zeros between them
    height = [1000] + [0] * 998 + [1000]
    assert trap(height) == 1000 * 998


def test_sawtooth() -> None:
    # [5,0,5,0,5,0,5] -> 3 valleys of 5 each = 15
    assert trap([5, 0, 5, 0, 5, 0, 5]) == 15


def test_plateau_with_gap() -> None:
    assert trap([4, 4, 0, 0, 4, 4]) == 8


@pytest.mark.parametrize(
    "height, expected",
    [
        ([1, 0, 1], 1),
        ([2, 1, 0, 1, 2], 4),
        ([0, 7, 1, 4, 6], 7),
        ([6, 4, 2, 0, 3, 2, 0, 3, 1, 4, 5, 3, 2, 7, 5, 3, 0, 1, 2, 1, 3, 4, 6, 8, 1, 3], 83),
    ],
    ids=["tiny-v", "symmetric-v", "left-heavy", "complex"],
)
def test_parametrized(height: list[int], expected: int) -> None:
    assert trap(height) == expected
