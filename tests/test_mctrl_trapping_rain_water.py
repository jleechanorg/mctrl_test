"""Focused tests for LeetCode #42 — Trapping Rain Water."""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from orchestration.trapping_rain_water import trap


class TestTrapClassicCases:
    """Core examples from LeetCode."""

    def test_example_1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_example_2(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9


class TestEdgeCases:
    """Boundary and degenerate inputs."""

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


class TestSinglePool:
    """Variations with one trapped pool."""

    def test_v_shape(self) -> None:
        assert trap([3, 0, 3]) == 3

    def test_asymmetric_v(self) -> None:
        # Water bounded by min(5, 3) = 3; depth at middle = 3 - 1 = 2
        assert trap([5, 1, 3]) == 2

    def test_wide_valley(self) -> None:
        assert trap([5, 0, 0, 0, 5]) == 15

    def test_shallow_valley(self) -> None:
        assert trap([2, 1, 2]) == 1


class TestMultiplePools:
    """Multiple distinct pools."""

    def test_two_pools(self) -> None:
        # Pool 1 between idx 0-2, pool 2 between idx 3-5
        assert trap([3, 0, 3, 0, 0, 3]) == 9

    def test_staircase_down_up(self) -> None:
        # [4,1,1,0,1,1,4]: water = (3+3+4+3+3) = 16
        assert trap([4, 1, 1, 0, 1, 1, 4]) == 16


class TestLargeValues:
    """Stress and large-value correctness."""

    def test_tall_walls(self) -> None:
        assert trap([100000, 0, 100000]) == 100000

    def test_long_flat_valley(self) -> None:
        n = 10000
        height = [n] + [0] * (n - 2) + [n]
        assert trap(height) == n * (n - 2)

    def test_all_zeros(self) -> None:
        assert trap([0] * 100) == 0

    def test_alternating(self) -> None:
        # [0, 1, 0, 1, 0, 1] — each inner 0 traps 1 unit (bounded by 1s)
        assert trap([0, 1, 0, 1, 0, 1]) == 2
