"""Tests for LeetCode #42 — Trapping Rain Water.

Focused test suite covering edge cases, canonical examples, and stress patterns.
"""
from __future__ import annotations

import sys
import os

# Ensure src/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from orchestration.trapping_rain_water import trap


class TestTrappingRainWater:
    """Core correctness tests."""

    # --- LeetCode canonical examples ---

    def test_leetcode_example_1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_leetcode_example_2(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9

    # --- Edge cases ---

    def test_empty(self) -> None:
        assert trap([]) == 0

    def test_single_bar(self) -> None:
        assert trap([5]) == 0

    def test_two_bars(self) -> None:
        assert trap([3, 7]) == 0

    def test_three_bars_valley(self) -> None:
        assert trap([3, 0, 3]) == 3

    def test_flat(self) -> None:
        assert trap([2, 2, 2, 2]) == 0

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0, 0]) == 0

    # --- Monotonic sequences (no trapping) ---

    def test_ascending(self) -> None:
        assert trap([1, 2, 3, 4, 5]) == 0

    def test_descending(self) -> None:
        assert trap([5, 4, 3, 2, 1]) == 0

    # --- Shape patterns ---

    def test_v_shape(self) -> None:
        assert trap([5, 0, 5]) == 5

    def test_deep_v(self) -> None:
        assert trap([10, 0, 0, 0, 10]) == 30

    def test_w_shape(self) -> None:
        # Two valleys
        assert trap([3, 0, 3, 0, 3]) == 6

    def test_staircase_up_down(self) -> None:
        assert trap([0, 1, 2, 3, 2, 1, 0]) == 0

    def test_tall_walls_short_middle(self) -> None:
        # [5, 1, 1, 1, 5]: 3 interior bars, each traps (5-1)=4 → total 12
        assert trap([5, 1, 1, 1, 5]) == 12

    def test_asymmetric_walls(self) -> None:
        # Water limited by shorter wall (height 3)
        assert trap([3, 0, 5]) == 3

    def test_multiple_pools(self) -> None:
        assert trap([2, 0, 2, 0, 2]) == 4

    # --- Stress / large inputs ---

    def test_large_symmetric(self) -> None:
        # 1000-bar valley: walls of 1000, floor of 0
        n = 1000
        height = [n] + [0] * (n - 2) + [n]
        assert trap(height) == n * (n - 2)

    def test_sawtooth(self) -> None:
        # Alternating 0,1,0,1... — each gap holds 0 water (wall=1)
        height = [0, 1] * 50
        # Max from left grows to 1, each 0 traps 1 unit
        # except first 0 (no left wall) and last position
        assert trap(height) == 49

    def test_single_peak(self) -> None:
        # Pyramid shape — no water trapped
        height = list(range(50)) + list(range(50, -1, -1))
        assert trap(height) == 0
