"""Focused tests for LeetCode #42 — Trapping Rain Water."""

from __future__ import annotations

import sys
import os

# Allow imports from leet_code/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from leet_code.trapping_rain_water import trap


class TestTrappingRainWater:
    """Core correctness tests."""

    def test_leetcode_example_1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_leetcode_example_2(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9

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

    def test_simple_valley(self) -> None:
        # [3, 0, 3] traps 3 units
        assert trap([3, 0, 3]) == 3

    def test_asymmetric_valley(self) -> None:
        # [3, 0, 2] — bounded by min(3,2)=2, so 2 units
        assert trap([3, 0, 2]) == 2

    def test_multiple_valleys(self) -> None:
        # Two valleys: [2,0,2] traps 2, then [2,0,2] traps 2
        assert trap([2, 0, 2, 0, 2]) == 4

    def test_tall_walls_deep_valley(self) -> None:
        assert trap([5, 0, 0, 0, 5]) == 15

    def test_staircase_up_down(self) -> None:
        # [0,1,2,3,2,1,0] — pyramid, no water trapped
        assert trap([0, 1, 2, 3, 2, 1, 0]) == 0

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0, 0]) == 0

    def test_single_dip(self) -> None:
        # [5, 2, 5] traps 3
        assert trap([5, 2, 5]) == 3

    def test_complex_terrain(self) -> None:
        # Manually verified
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_large_values(self) -> None:
        assert trap([100000, 0, 100000]) == 100000

    def test_alternating(self) -> None:
        # [1,0,1,0,1] — two valleys of 1 each
        assert trap([1, 0, 1, 0, 1]) == 2
