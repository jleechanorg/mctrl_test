"""Focused tests for LeetCode #42 — Trapping Rain Water."""

from __future__ import annotations

import sys
import os
import pytest

# Ensure leet_code/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "leet_code"))

from trapping_rain_water import trap


# --- LeetCode examples ---

def test_example_1():
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6


def test_example_2():
    assert trap([4, 2, 0, 3, 2, 5]) == 9


# --- Edge cases ---

def test_empty():
    assert trap([]) == 0


def test_single_bar():
    assert trap([5]) == 0


def test_two_bars():
    assert trap([3, 7]) == 0


def test_flat():
    assert trap([3, 3, 3, 3]) == 0


def test_ascending():
    assert trap([1, 2, 3, 4, 5]) == 0


def test_descending():
    assert trap([5, 4, 3, 2, 1]) == 0


# --- Structural patterns ---

def test_v_shape():
    # Simple valley: 3 _ _ 3  =>  3 units
    assert trap([3, 0, 0, 3]) == 6


def test_single_trap():
    assert trap([2, 0, 2]) == 2


def test_multiple_valleys():
    # Two valleys: between 3-1-3 and 3-0-3
    assert trap([3, 1, 3, 0, 3]) == 2 + 3


def test_plateau_walls():
    assert trap([5, 5, 1, 5, 5]) == 4


def test_tall_walls_deep_valley():
    assert trap([100, 0, 0, 0, 100]) == 300


# --- Asymmetric cases ---

def test_left_wall_higher():
    # Water limited by shorter right wall
    assert trap([5, 0, 3]) == 3


def test_right_wall_higher():
    assert trap([3, 0, 5]) == 3


def test_staircase_up_then_down():
    # 0,1,2,3,2,1,0 — peak in middle, no water trapped
    assert trap([0, 1, 2, 3, 2, 1, 0]) == 0


def test_staircase_down_then_up():
    # 3,2,1,0,1,2,3 — valley, water = 3+2+1+0+1+2 wait let me calc
    # min(left_max, right_max) - h for each inner position
    # left_max progresses: 3,3,3,3,3,3,3
    # right_max progresses: 3,3,3,3,3,3,3
    # water: (3-2)+(3-1)+(3-0)+(3-1)+(3-2) = 1+2+3+2+1 = 9
    assert trap([3, 2, 1, 0, 1, 2, 3]) == 9


# --- Large / stress ---

def test_large_alternating():
    # [5,0,5,0,5,...] with 1000 bars — each valley traps 5
    n = 1000
    height = [5 if i % 2 == 0 else 0 for i in range(n)]
    # 499 valleys of depth 5
    assert trap(height) == 499 * 5


def test_all_zeros():
    assert trap([0] * 100) == 0
