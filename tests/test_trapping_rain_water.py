"""Tests for LeetCode #42 — Trapping Rain Water."""
from __future__ import annotations

import pytest

from orchestration.trapping_rain_water import trap


class TestTrapBasic:
    """Core examples from the problem statement."""

    def test_example_1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_example_2(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9


class TestTrapEdgeCases:
    """Edge cases and boundary conditions."""

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

    def test_valley(self) -> None:
        # 3 _ _ 3  →  water = 3+3 = 6
        assert trap([3, 0, 0, 3]) == 6

    def test_uneven_walls(self) -> None:
        # min(2,3)=2 for middle bar → 2-0 = 2
        assert trap([2, 0, 3]) == 2

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0]) == 0

    def test_single_trap(self) -> None:
        assert trap([1, 0, 1]) == 1


class TestTrapLarger:
    """Larger / stress scenarios."""

    def test_w_shape(self) -> None:
        # Two valleys: [5,0,5,0,5]
        assert trap([5, 0, 5, 0, 5]) == 10

    def test_staircase_up_down(self) -> None:
        assert trap([0, 1, 2, 3, 2, 1, 0]) == 0

    def test_deep_valley(self) -> None:
        assert trap([5, 0, 0, 0, 0, 5]) == 20

    def test_multiple_pools(self) -> None:
        #  3 _ 3 _ 3
        assert trap([3, 0, 3, 0, 3]) == 6

    @pytest.mark.parametrize("n", [100, 1_000, 10_000])
    def test_large_v_shape(self, n: int) -> None:
        """V-shape: descending then ascending. Water = sum of gaps."""
        half = n // 2
        heights = list(range(half, -1, -1)) + list(range(1, half + 1))
        expected = sum(half - h for h in heights)
        assert trap(heights) == expected
