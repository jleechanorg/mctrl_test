"""Tests for LeetCode #42 — Trapping Rain Water."""
from __future__ import annotations

import pytest

from orchestration.trapping_rain_water import trap


class TestTrapClassicExamples:
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
    """Ascending / descending — no water trapped."""

    def test_ascending(self) -> None:
        assert trap([1, 2, 3, 4, 5]) == 0

    def test_descending(self) -> None:
        assert trap([5, 4, 3, 2, 1]) == 0


class TestTrapShapes:
    """Various terrain shapes."""

    def test_v_shape(self) -> None:
        assert trap([3, 0, 3]) == 3

    def test_deep_valley(self) -> None:
        assert trap([5, 0, 0, 0, 5]) == 15

    def test_asymmetric_valley(self) -> None:
        # min(3,5)=3, trapped: (3-0)+(3-1)=5
        assert trap([3, 0, 1, 5]) == 5

    def test_multiple_valleys(self) -> None:
        # Two valleys: between 3s and between 3/4
        assert trap([3, 0, 3, 0, 4]) == 6

    def test_staircase_down_then_up(self) -> None:
        assert trap([4, 3, 2, 1, 2, 3, 4]) == 9

    def test_plateau_with_dip(self) -> None:
        assert trap([2, 2, 0, 2, 2]) == 2


class TestTrapLargeInput:
    """Performance: O(n) should handle large inputs quickly."""

    def test_large_alternating(self) -> None:
        # [0,1,0,1,...,0,1] — each 0 between two 1s traps 1 unit
        n = 100_000
        height = [i % 2 for i in range(n)]
        # positions 2,4,6,...,99998 are 0s bounded by 1s → 49999 water
        assert trap(height) == 49999

    def test_large_bowl(self) -> None:
        # [n, 0, 0, ..., 0, n] — traps n*(n-2) water
        n = 50_000
        height = [n] + [0] * (n - 2) + [n]
        assert trap(height) == n * (n - 2)
