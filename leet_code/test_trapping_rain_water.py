"""Focused tests for LeetCode #42 — Trapping Rain Water."""

from __future__ import annotations

import pytest
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
    assert trap([2, 2, 2, 2]) == 0


def test_ascending():
    assert trap([1, 2, 3, 4, 5]) == 0


def test_descending():
    assert trap([5, 4, 3, 2, 1]) == 0


# --- Shape patterns ---

def test_simple_valley():
    # 3 . . 3  →  water fills middle 2 slots to height 3
    assert trap([3, 0, 0, 3]) == 6


def test_v_shape():
    assert trap([3, 1, 3]) == 2


def test_asymmetric_valley():
    # bounded by min(2, 5) = 2
    assert trap([2, 0, 5]) == 2


def test_multiple_valleys():
    # [3,0,3] traps 3, then [3,0,3] traps 3 → total 6
    assert trap([3, 0, 3, 0, 3]) == 6


def test_staircase_down_up():
    # [5,4,1,2] → water at idx1=0, idx2=1 (bounded by min(5,2)=2) → 1+1=1? No.
    # Actually: left_max[0]=5, left_max[1]=5, left_max[2]=5, left_max[3]=5
    #           right_max[3]=2, right_max[2]=2, right_max[1]=2, right_max[0]=5
    # water[1] = min(5,2)-4 = -2 → 0
    # water[2] = min(5,2)-1 = 1
    assert trap([5, 4, 1, 2]) == 1


def test_tall_walls_deep_valley():
    assert trap([100, 0, 0, 0, 100]) == 300


# --- All zeros ---

def test_all_zeros():
    assert trap([0, 0, 0, 0]) == 0


# --- Large uniform pool ---

def test_uniform_pool():
    # walls of height 10 with 98 zeros in between
    height = [10] + [0] * 98 + [10]
    assert trap(height) == 980


# --- Zigzag ---

def test_zigzag():
    # [2,0,2,0,2] → two pools of 2 each
    assert trap([2, 0, 2, 0, 2]) == 4


# --- Single trapped unit ---

def test_minimal_trap():
    assert trap([1, 0, 1]) == 1
