"""Focused tests for LeetCode #42 — Trapping Rain Water."""

from __future__ import annotations

import sys
import os

# Ensure leet_code is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from leet_code.trapping_rain_water import trap


class TestTrappingRainWater:
    """Core correctness tests."""

    def test_example_1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_example_2(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9

    def test_no_bars(self) -> None:
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

    def test_single_valley(self) -> None:
        # [3, 0, 3] -> 3 units in the middle
        assert trap([3, 0, 3]) == 3

    def test_asymmetric_valley(self) -> None:
        # [5, 0, 3] -> water level = 3, trapped = 3
        assert trap([5, 0, 3]) == 3

    def test_deep_well(self) -> None:
        # [5, 0, 0, 0, 5] -> 5*3 = 15
        assert trap([5, 0, 0, 0, 5]) == 15

    def test_staircase_down_up(self) -> None:
        # [3, 2, 1, 2, 3] -> water fills symmetrically
        # level 3: positions 1,2,3 trap (3-2)+(3-1)+(3-2) = 1+2+1 = 4
        assert trap([3, 2, 1, 2, 3]) == 4

    def test_multiple_pools(self) -> None:
        # [2, 0, 2, 0, 2] -> two pools of 2 each
        assert trap([2, 0, 2, 0, 2]) == 4

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0, 0]) == 0

    def test_tall_edges_complex_middle(self) -> None:
        # [5, 1, 3, 1, 5] -> water level 5 everywhere
        # (5-1)+(5-3)+(5-1) = 4+2+4 = 10
        assert trap([5, 1, 3, 1, 5]) == 10

    def test_large_values(self) -> None:
        # Constraint: height[i] <= 10^5
        assert trap([100000, 0, 100000]) == 100000

    def test_plateau_with_dip(self) -> None:
        # [4, 4, 1, 4, 4] -> 3 units trapped at index 2
        assert trap([4, 4, 1, 4, 4]) == 3

    def test_gradual_slope_and_cliff(self) -> None:
        # [0, 1, 2, 3, 0, 3] -> only index 4 traps: 3
        assert trap([0, 1, 2, 3, 0, 3]) == 3
