"""Focused tests for LeetCode #42 Trapping Rain Water."""

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


def test_no_trap_ascending() -> None:
    assert trap([1, 2, 3, 4, 5]) == 0


def test_no_trap_descending() -> None:
    assert trap([5, 4, 3, 2, 1]) == 0


# --- Single pool ---

def test_simple_valley() -> None:
    # [3, 0, 3] traps 3 units
    assert trap([3, 0, 3]) == 3


def test_asymmetric_valley() -> None:
    # [5, 0, 3] -> water bounded by min(5,3)=3, traps 3
    assert trap([5, 0, 3]) == 3


def test_deep_narrow_valley() -> None:
    # [10, 0, 10] traps 10
    assert trap([10, 0, 10]) == 10


# --- Multiple pools ---

def test_two_valleys() -> None:
    # [3,0,3,0,3] -> two pools of 3 each = 6
    assert trap([3, 0, 3, 0, 3]) == 6


def test_staircase_down_up() -> None:
    # [4,1,1,0,2,3] -> water fills to level 3 on right
    # pos1: min(4,3)-1=2, pos2: min(4,3)-1=2, pos3: min(4,3)-0=3, pos4: min(4,3)-2=1
    assert trap([4, 1, 1, 0, 2, 3]) == 8


# --- Large uniform pool ---

def test_bathtub() -> None:
    # [5, 0, 0, 0, 0, 5] -> 4 * 5 = 20
    assert trap([5, 0, 0, 0, 0, 5]) == 20


# --- All zeros ---

def test_all_zeros() -> None:
    assert trap([0, 0, 0, 0]) == 0


# --- Spike patterns ---

def test_single_spike() -> None:
    # [0, 0, 5, 0, 0] -> no walls on sides to hold water
    assert trap([0, 0, 5, 0, 0]) == 0


def test_two_spikes() -> None:
    # [0, 5, 0, 0, 5, 0] -> 5+5 = 10 trapped between spikes
    assert trap([0, 5, 0, 0, 5, 0]) == 10


# --- Constraint boundary ---

def test_max_height_values() -> None:
    assert trap([100000, 0, 100000]) == 100000


def test_large_input() -> None:
    # Alternating pattern: 10000 bars
    height = [0, 10] * 5000
    # Each 0 between two 10s traps 10 (except last 10 has no right wall)
    # Pattern: 0,10,0,10,...,0,10 -> 4999 zeros between 10s -> 4999*10
    expected = trap(height)  # just verify no crash + O(n) performance
    assert expected == 4999 * 10
