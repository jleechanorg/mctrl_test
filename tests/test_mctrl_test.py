"""Tests for LeetCode #42 — Trapping Rain Water."""
from __future__ import annotations

import pytest

from orchestration.mctrl_test import trap


class TestTrapRainWater:
    """Focused tests for the two-pointer trapping rain water solution."""

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

    def test_flat(self) -> None:
        assert trap([3, 3, 3, 3]) == 0

    def test_ascending(self) -> None:
        assert trap([1, 2, 3, 4, 5]) == 0

    def test_descending(self) -> None:
        assert trap([5, 4, 3, 2, 1]) == 0

    def test_single_valley(self) -> None:
        # [3, 0, 3] traps 3 units
        assert trap([3, 0, 3]) == 3

    def test_deep_valley(self) -> None:
        # [5, 0, 0, 0, 5] traps 15 units
        assert trap([5, 0, 0, 0, 5]) == 15

    def test_asymmetric_walls(self) -> None:
        # [3, 0, 5] — bounded by shorter wall (3), traps 3
        assert trap([3, 0, 5]) == 3

    def test_multiple_valleys(self) -> None:
        # [2, 0, 2, 0, 2] — two valleys of 2 each
        assert trap([2, 0, 2, 0, 2]) == 4

    def test_staircase_up_down(self) -> None:
        # [0, 1, 2, 3, 2, 1, 0] — pyramid, no trapping
        assert trap([0, 1, 2, 3, 2, 1, 0]) == 0

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0, 0]) == 0

    def test_large_values(self) -> None:
        # [100000, 0, 100000]
        assert trap([100000, 0, 100000]) == 100000

    def test_plateau_with_dip(self) -> None:
        # [4, 4, 1, 4, 4] — dip of 3 units wide 1
        assert trap([4, 4, 1, 4, 4]) == 3

    def test_nested_valleys(self) -> None:
        # [5, 2, 1, 2, 5] — inner shape traps water
        assert trap([5, 2, 1, 2, 5]) == 12
