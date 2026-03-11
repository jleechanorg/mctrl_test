"""Tests for LeetCode #42 — Trapping Rain Water."""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "leet_code"))

from trapping_rain_water import trap


class TestTrappingRainWater:
    """Focused tests for the two-pointer trapping rain water solution."""

    # --- LeetCode examples ---

    def test_example_1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_example_2(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9

    # --- Edge cases ---

    def test_empty(self) -> None:
        assert trap([]) == 0

    def test_single_bar(self) -> None:
        assert trap([5]) == 0

    def test_two_bars(self) -> None:
        assert trap([3, 7]) == 0

    def test_flat_surface(self) -> None:
        assert trap([3, 3, 3, 3]) == 0

    def test_ascending(self) -> None:
        assert trap([1, 2, 3, 4, 5]) == 0

    def test_descending(self) -> None:
        assert trap([5, 4, 3, 2, 1]) == 0

    # --- Structural patterns ---

    def test_simple_valley(self) -> None:
        # 3 _ 3  →  water = 3
        assert trap([3, 0, 3]) == 3

    def test_asymmetric_valley(self) -> None:
        # 3 _ 2  →  water = 2 (bounded by shorter wall)
        assert trap([3, 0, 2]) == 2

    def test_nested_valleys(self) -> None:
        # Four zero-height bars bounded by walls of height 3 → 4 × 3 = 12
        assert trap([3, 0, 0, 3, 0, 0, 3]) == 12

    def test_staircase_down_up(self) -> None:
        assert trap([5, 4, 3, 2, 3, 4, 5]) == 9

    def test_single_tall_peak(self) -> None:
        # V-shape: 5 1 0 1 5  →  water at indices 1,2,3 = 4+5+4 = 13
        assert trap([5, 1, 0, 1, 5]) == 13

    def test_plateau_walls(self) -> None:
        assert trap([4, 4, 0, 0, 4, 4]) == 8

    # --- Large / stress ---

    def test_large_flat(self) -> None:
        assert trap([0] * 20000) == 0

    def test_large_bowl(self) -> None:
        # Descend then ascend: 10000 9999 ... 0 ... 9999 10000
        n = 10001
        height = list(range(n - 1, -1, -1)) + list(range(1, n))
        # Water at each interior bar = max_boundary - height[i] = 10000 - height[i]
        expected = sum(n - 1 - h for h in height[1:-1])
        assert trap(height) == expected

    def test_all_zeros_except_walls(self) -> None:
        height = [100] + [0] * 9998 + [100]
        assert trap(height) == 100 * 9998
