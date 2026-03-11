"""Tests for LeetCode #42 - Trapping Rain Water."""

from __future__ import annotations

import pytest

from trapping_rain_water import trap


class TestTrappingRainWater:
    """Focused tests for the two-pointer trap() implementation."""

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

    def test_single_valley(self) -> None:
        # Simple V shape: 3 _ 3 -> holds 3 units
        assert trap([3, 0, 3]) == 3

    def test_asymmetric_valley(self) -> None:
        # Water bounded by shorter wall: min(2, 5) - 0 = 2
        assert trap([2, 0, 5]) == 2

    def test_stepped_pools(self) -> None:
        # Two separate pools
        assert trap([3, 0, 3, 0, 3]) == 6

    def test_deep_narrow_well(self) -> None:
        assert trap([5, 0, 5]) == 5

    def test_wide_shallow_pool(self) -> None:
        # 2,1,1,1,2 -> 1+1+1 = 3
        assert trap([2, 1, 1, 1, 2]) == 3

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0, 0]) == 0

    def test_zero_height_bars(self) -> None:
        assert trap([0, 0, 0]) == 0

    # --- Larger / stress ---

    def test_mountain_shape(self) -> None:
        # Peak in middle, no water trapped
        assert trap([1, 2, 3, 4, 3, 2, 1]) == 0

    def test_bowl_shape(self) -> None:
        # 4,1,1,1,4 -> 3+3+3 = 9
        assert trap([4, 1, 1, 1, 4]) == 9

    def test_multiple_peaks(self) -> None:
        # [3,1,2,1,3] -> pool between 3..2 (1 unit) + pool between 2..3 (1 unit)
        # Actually: min(3,3)-1 + min(3,3)-2 + min(3,3)-1 = 2+1+2 = 5
        assert trap([3, 1, 2, 1, 3]) == 5

    def test_large_uniform_pool(self) -> None:
        # Walls of 100 with 998 zeros in between
        height = [100] + [0] * 998 + [100]
        assert trap(height) == 100 * 998

    def test_staircase_up_down(self) -> None:
        # [0,1,2,3,2,1,0] - no trapping (monotonic sides)
        assert trap([0, 1, 2, 3, 2, 1, 0]) == 0

    def test_constraint_max_height(self) -> None:
        # height[i] up to 10^5
        assert trap([100000, 0, 100000]) == 100000
