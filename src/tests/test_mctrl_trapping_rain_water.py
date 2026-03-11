"""Focused tests for LeetCode #42 — Trapping Rain Water."""

from __future__ import annotations

import sys
import os

# Ensure leet_code is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from leet_code.trapping_rain_water import trap


class TestTrappingRainWater:
    """Core correctness tests."""

    def test_example_1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_example_2(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9

    def test_empty(self) -> None:
        assert trap([]) == 0

    def test_single_bar(self) -> None:
        assert trap([5]) == 0

    def test_two_bars(self) -> None:
        assert trap([3, 7]) == 0

    def test_flat(self) -> None:
        assert trap([3, 3, 3, 3]) == 0

    def test_ascending(self) -> None:
        assert trap([1, 2, 3, 4, 5]) == 0

    def test_descending(self) -> None:
        assert trap([5, 4, 3, 2, 1]) == 0

    def test_v_shape(self) -> None:
        # [5, 0, 5] traps 5 units
        assert trap([5, 0, 5]) == 5

    def test_w_shape(self) -> None:
        # [3, 0, 3, 0, 3] = 3 + 3 = 6
        assert trap([3, 0, 3, 0, 3]) == 6

    def test_single_valley(self) -> None:
        # [2, 0, 2] traps 2
        assert trap([2, 0, 2]) == 2

    def test_asymmetric_walls(self) -> None:
        # [3, 0, 1] — water limited by shorter wall: min(3,1)-0 = 1
        assert trap([3, 0, 1]) == 1

    def test_deep_narrow_pool(self) -> None:
        # [100, 0, 100]
        assert trap([100, 0, 100]) == 100

    def test_staircase_up_down(self) -> None:
        # [0, 1, 2, 3, 2, 1, 0] — pyramid, no trapping
        assert trap([0, 1, 2, 3, 2, 1, 0]) == 0

    def test_multiple_pools(self) -> None:
        # [3, 0, 1, 0, 3] = 3 + 2 + 3 = 8
        assert trap([3, 0, 1, 0, 3]) == 8

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0, 0]) == 0

    def test_large_plateau_with_dip(self) -> None:
        # [5, 5, 1, 5, 5] — dip of 4 in middle
        assert trap([5, 5, 1, 5, 5]) == 4

    def test_constraint_max_height(self) -> None:
        # heights at max constraint value
        assert trap([100000, 0, 100000]) == 100000

    def test_long_uniform_valley(self) -> None:
        # [5] + [0]*100 + [5] = 500
        height = [5] + [0] * 100 + [5]
        assert trap(height) == 500
