"""Focused tests for LeetCode #42 Trapping Rain Water."""

from __future__ import annotations

import pytest
from trapping_rain_water import trap


class TestLeetCodeExamples:
    """Official LeetCode examples."""

    def test_example_1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_example_2(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9


class TestEdgeCases:
    """Boundary and degenerate inputs."""

    def test_single_bar(self) -> None:
        assert trap([5]) == 0

    def test_two_bars(self) -> None:
        assert trap([3, 7]) == 0

    def test_empty(self) -> None:
        assert trap([]) == 0

    def test_flat(self) -> None:
        assert trap([3, 3, 3, 3]) == 0

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0, 0]) == 0


class TestMonotonicShapes:
    """No water should be trapped in purely ascending or descending."""

    def test_ascending(self) -> None:
        assert trap([1, 2, 3, 4, 5]) == 0

    def test_descending(self) -> None:
        assert trap([5, 4, 3, 2, 1]) == 0


class TestClassicPatterns:
    """Common trapping patterns."""

    def test_v_shape(self) -> None:
        # Valley: walls of 3, dip to 0
        assert trap([3, 0, 3]) == 3

    def test_w_shape(self) -> None:
        # Two valleys
        assert trap([3, 0, 3, 0, 3]) == 6

    def test_uneven_walls(self) -> None:
        # Water bounded by shorter wall
        assert trap([5, 0, 3]) == 3

    def test_staircase_down_then_up(self) -> None:
        assert trap([4, 3, 2, 1, 2, 3, 4]) == 9

    def test_deep_narrow_well(self) -> None:
        assert trap([10, 0, 10]) == 10

    def test_plateau_with_dip(self) -> None:
        assert trap([5, 5, 1, 5, 5]) == 4


class TestLargeInput:
    """Performance sanity check."""

    def test_large_alternating(self) -> None:
        # 20000 bars alternating 0 and 1
        height = [i % 2 for i in range(20000)]
        result = trap(height)
        assert result == 9999

    def test_large_v(self) -> None:
        n = 20000
        height = list(range(n // 2, 0, -1)) + list(range(1, n // 2 + 1))
        result = trap(height)
        # Symmetric V: both left descent and right ascent trap water
        expected = 2 * sum(n // 2 - h for h in range(1, n // 2))
        assert result == expected
