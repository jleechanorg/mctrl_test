from __future__ import annotations

import pytest

from orchestration.trapping_rain_water import trap


class TestTrapBasicExamples:
    """LeetCode provided examples."""

    def test_example_1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_example_2(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9


class TestTrapEdgeCases:
    """Edge cases: empty, single, two elements, flat."""

    def test_empty(self) -> None:
        assert trap([]) == 0

    def test_single(self) -> None:
        assert trap([5]) == 0

    def test_two_elements(self) -> None:
        assert trap([3, 7]) == 0

    def test_flat(self) -> None:
        assert trap([3, 3, 3, 3]) == 0


class TestTrapMonotonic:
    """No water trapped in strictly increasing or decreasing sequences."""

    def test_increasing(self) -> None:
        assert trap([1, 2, 3, 4, 5]) == 0

    def test_decreasing(self) -> None:
        assert trap([5, 4, 3, 2, 1]) == 0


class TestTrapSingleValley:
    """Single valley (V-shape) patterns."""

    def test_symmetric_v(self) -> None:
        # [3, 0, 3] -> 3 units trapped
        assert trap([3, 0, 3]) == 3

    def test_asymmetric_v(self) -> None:
        # [5, 0, 3] -> water limited by shorter wall: 3
        assert trap([5, 0, 3]) == 3

    def test_wide_valley(self) -> None:
        # [3, 1, 1, 1, 3] -> 2+2+2 = 6
        assert trap([3, 1, 1, 1, 3]) == 6


class TestTrapMultipleValleys:
    """Multiple separate pools."""

    def test_two_pools(self) -> None:
        # [2, 0, 2, 0, 2] -> pool1=2, pool2=2 -> 4
        assert trap([2, 0, 2, 0, 2]) == 4

    def test_staircase_down_up(self) -> None:
        # [4, 1, 3, 1, 5] -> between 4&3: 2, between 3&5: 2 -> but
        # actually: min(4,5)-1 + min(4,5)-3 + min(4,5)-1 = 3+1+3=7? No.
        # Index 1: min(4,5)-1=3; Index 2: min(4,5)-3=1; Index 3: min(4,5)-1=3 -> 7
        assert trap([4, 1, 3, 1, 5]) == 7


class TestTrapLargeValues:
    """Stress / large value correctness."""

    def test_tall_walls_deep_valley(self) -> None:
        assert trap([10000, 0, 10000]) == 10000

    def test_large_uniform_valley(self) -> None:
        # [100, 0, 0, ...(98 zeros)..., 0, 100] -> 100 * 98 = 9800
        height = [100] + [0] * 98 + [100]
        assert trap(height) == 9800


class TestTrapAllZeros:
    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0, 0]) == 0


class TestTrapPlateau:
    """Plateau shapes where edges are higher than middle."""

    def test_plateau_with_dip(self) -> None:
        # [5, 5, 1, 5, 5] -> 4 units in the middle
        assert trap([5, 5, 1, 5, 5]) == 4
