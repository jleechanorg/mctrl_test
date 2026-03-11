"""Tests for LeetCode #42 — Trapping Rain Water.

Covers the canonical examples, edge cases, and stress patterns.
"""
from __future__ import annotations

import pytest

from orchestration.trapping_rain_water import trap


# --- Canonical LeetCode examples ---

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


# --- Structural patterns ---

def test_v_shape() -> None:
    # Simple valley: min(3,3)-0 + min(3,3)-1 + min(3,3)-0 = 3+2+3 = 8
    assert trap([3, 0, 1, 0, 3]) == 8


def test_w_shape() -> None:
    assert trap([3, 0, 3, 0, 3]) == 6


def test_single_trap() -> None:
    assert trap([2, 0, 2]) == 2


def test_tall_walls_deep_valley() -> None:
    assert trap([100, 0, 0, 0, 100]) == 300


def test_staircase_up_then_down() -> None:
    # Pyramid: 1,2,3,4,3,2,1 — no water trapped
    assert trap([1, 2, 3, 4, 3, 2, 1]) == 0


def test_multiple_pools() -> None:
    # Two separate pools
    height = [3, 0, 3, 0, 0, 3]
    # Pool 1 (index 1): 3-0 = 3
    # Pool 2 (indices 3-4): 3-0 + 3-0 = 6
    assert trap(height) == 9


def test_all_zeros() -> None:
    assert trap([0, 0, 0, 0]) == 0


def test_spike_pattern() -> None:
    # 0,5,0,5,0 — two pools of depth 5 each? No: min(5,5)-0 at indices 2
    # Index 0: bounded only on right, no left wall → 0
    # Index 2: min(5,5)-0 = 5
    # Index 4: bounded only on left, no right wall → 0
    assert trap([0, 5, 0, 5, 0]) == 5


def test_large_uniform_pool() -> None:
    # Walls of 10 with 98 zeros in between
    height = [10] + [0] * 98 + [10]
    assert trap(height) == 980


# --- Parametrized for conciseness ---

@pytest.mark.parametrize("height, expected", [
    ([1, 0, 1], 1),
    ([2, 1, 2], 1),
    ([5, 2, 1, 2, 1, 5], 14),
    ([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1], 6),
])
def test_parametrized_cases(height: list[int], expected: int) -> None:
    assert trap(height) == expected
