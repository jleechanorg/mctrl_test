"""Tests for LeetCode #42 - Trapping Rain Water."""

from __future__ import annotations

import pytest

from trapping_rain_water import trap


class TestTrappingRainWater:
    """Core problem cases from LeetCode."""

    def test_example_1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_example_2(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9


class TestEdgeCases:
    """Boundary and degenerate inputs."""

    def test_empty_array(self) -> None:
        assert trap([]) == 0

    def test_single_bar(self) -> None:
        assert trap([5]) == 0

    def test_two_bars(self) -> None:
        assert trap([3, 7]) == 0

    def test_three_bars_no_trap(self) -> None:
        assert trap([1, 2, 3]) == 0

    def test_three_bars_with_trap(self) -> None:
        assert trap([3, 0, 3]) == 3

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0, 0]) == 0

    def test_all_same_height(self) -> None:
        assert trap([5, 5, 5, 5]) == 0


class TestPatterns:
    """Characteristic elevation patterns."""

    def test_ascending(self) -> None:
        assert trap([1, 2, 3, 4, 5]) == 0

    def test_descending(self) -> None:
        assert trap([5, 4, 3, 2, 1]) == 0

    def test_v_shape(self) -> None:
        assert trap([5, 0, 5]) == 5

    def test_mountain(self) -> None:
        assert trap([1, 3, 5, 3, 1]) == 0

    def test_valley(self) -> None:
        assert trap([5, 3, 1, 3, 5]) == 8

    def test_multiple_valleys(self) -> None:
        # Two pools: between 3,0,3 = 3 and between 3,0,3 = 3
        assert trap([3, 0, 3, 0, 3]) == 6

    def test_staircase_down_up(self) -> None:
        assert trap([4, 3, 2, 1, 2, 3, 4]) == 9

    def test_uneven_walls(self) -> None:
        # Left wall shorter: water limited by left wall
        assert trap([2, 0, 5]) == 2

    def test_large_gap(self) -> None:
        assert trap([10, 0, 0, 0, 0, 10]) == 40

    def test_single_tall_spike(self) -> None:
        assert trap([0, 0, 100, 0, 0]) == 0


class TestLargeInput:
    """Performance on constraint-boundary inputs."""

    def test_max_size_alternating(self) -> None:
        # 20000 elements alternating 0 and 1: pools of 1 between each pair of 1s
        n = 20000
        height = [i % 2 for i in range(n)]
        result = trap(height)
        # Every even index (except 0) between two 1s traps 1 unit
        assert result == (n // 2) - 1

    def test_max_height_walls(self) -> None:
        height = [100000, 0, 100000]
        assert trap(height) == 100000
