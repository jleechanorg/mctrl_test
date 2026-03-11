"""LeetCode #42 — Trapping Rain Water.

Given n non-negative integers representing an elevation map where the width
of each bar is 1, compute how much water it can trap after raining.

Two-pointer O(n) time, O(1) space solution.
"""
from __future__ import annotations


def trap(height: list[int]) -> int:
    """Return total units of trapped rain water using two pointers."""
    if len(height) < 3:
        return 0

    left, right = 0, len(height) - 1
    left_max, right_max = height[left], height[right]
    water = 0

    while left < right:
        if left_max <= right_max:
            left += 1
            left_max = max(left_max, height[left])
            water += left_max - height[left]
        else:
            right -= 1
            right_max = max(right_max, height[right])
            water += right_max - height[right]

    return water


# --------------- tests ---------------
import pytest


class TestTrapRainWater:
    """Focused tests for LeetCode #42."""

    def test_leetcode_example1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_leetcode_example2(self) -> None:
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
        # [3, 0, 3] traps 3 units in the middle
        assert trap([3, 0, 3]) == 3

    def test_tall_walls_deep_valley(self) -> None:
        # [5, 0, 0, 0, 5] traps 5*3 = 15
        assert trap([5, 0, 0, 0, 5]) == 15

    def test_staircase_up_down(self) -> None:
        # [0, 1, 2, 3, 2, 1, 0] — pyramid, no water
        assert trap([0, 1, 2, 3, 2, 1, 0]) == 0

    def test_multiple_pools(self) -> None:
        # [3,0,3,0,3] — two pools of 3 each
        assert trap([3, 0, 3, 0, 3]) == 6

    def test_uneven_walls(self) -> None:
        # [2, 0, 5] — limited by shorter wall: 2 units
        assert trap([2, 0, 5]) == 2

    def test_large_uniform_valley(self) -> None:
        height = [10] + [0] * 100 + [10]
        assert trap(height) == 1000

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0, 0]) == 0

    def test_single_dip(self) -> None:
        # [2, 1, 2] — 1 unit trapped
        assert trap([2, 1, 2]) == 1

    def test_complex_terrain(self) -> None:
        # [0,1,0,2,1,0,1,3,2,1,2,1] is example 1 = 6
        # Adding extra: [5,2,1,2,1,5,2,1,3,1,2,1,5,1]
        height = [5, 2, 1, 2, 1, 5, 2, 1, 3, 1, 2, 1, 5, 1]
        # Manual: between walls at 5(idx0) and 5(idx5): 3+4+3+4=14
        #         between 5(idx5) and 5(idx12): 3+4+2+4+3+4=20
        #         idx13 bounded by 5(idx12) and 1: no water past last wall
        assert trap(height) == 34
