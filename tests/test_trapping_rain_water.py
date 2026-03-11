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
    assert trap([3, 7]) == 0


def test_flat() -> None:
    assert trap([3, 3, 3, 3]) == 0


def test_ascending() -> None:
    assert trap([1, 2, 3, 4, 5]) == 0


def test_descending() -> None:
    assert trap([5, 4, 3, 2, 1]) == 0


# --- Structural patterns ---

def test_valley() -> None:
    assert trap([3, 0, 3]) == 3


def test_deep_valley() -> None:
    assert trap([5, 0, 0, 0, 5]) == 15


def test_asymmetric_valley() -> None:
    assert trap([3, 0, 2]) == 2


def test_multiple_valleys() -> None:
    assert trap([2, 0, 2, 0, 2]) == 4


def test_staircase_up_down() -> None:
    assert trap([0, 1, 2, 3, 2, 1, 0]) == 0


def test_plateau_with_dip() -> None:
    assert trap([4, 4, 1, 4, 4]) == 3


def test_tall_walls_short_middle() -> None:
    assert trap([10, 0, 0, 0, 0, 10]) == 40


def test_all_zeros() -> None:
    assert trap([0, 0, 0, 0]) == 0


def test_single_trap_cell() -> None:
    assert trap([1, 0, 1]) == 1


# --- Larger / stress ---

def test_large_uniform_valley() -> None:
    n = 1000
    height = [n] + [0] * (n - 2) + [n]
    assert trap(height) == n * (n - 2)


def test_sawtooth() -> None:
    # Alternating 0,2 pattern: water trapped in each 0 cell is min(2,2)-0 = 2
    height = [2, 0] * 50 + [2]
    assert trap(height) == 100
