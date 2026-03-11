"""
Trapping Rain Water - LeetCode Hard #42

Given n non-negative integers representing an elevation map where the width of
each bar is 1, compute how much water it can trap after raining.

Example 1:
Input: height = [0,1,0,2,1,0,1,3,2,1,2,1]
Output: 6

Example 2:
Input: height = [4,2,0,3,2,5]
Output: 9

Constraints:
- n == height.length
- 1 <= n <= 2 * 10^4
- 0 <= height[i] <= 10^5

Time Complexity: O(n)
Space Complexity: O(1) using two-pointer approach
"""

from __future__ import annotations
from typing import List


def trap(height: List[int]) -> int:
    """
    Calculate trapped rain water using the two-pointer technique.

    At each position, the water level is determined by
    min(max_left, max_right) - height[i]. We maintain two pointers
    and track the running max from each side to compute this in O(1) space.

    Args:
        height: List of non-negative integers representing elevation map.

    Returns:
        Total units of trapped water.
    """
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


# --------------- pytest tests ---------------

import pytest


class TestTrapRainWater:
    """Focused tests for LeetCode #42 Trapping Rain Water."""

    def test_example_1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_example_2(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9

    def test_no_water_ascending(self) -> None:
        assert trap([1, 2, 3, 4, 5]) == 0

    def test_no_water_descending(self) -> None:
        assert trap([5, 4, 3, 2, 1]) == 0

    def test_single_element(self) -> None:
        assert trap([5]) == 0

    def test_two_elements(self) -> None:
        assert trap([3, 7]) == 0

    def test_flat(self) -> None:
        assert trap([3, 3, 3, 3]) == 0

    def test_simple_valley(self) -> None:
        # 3 _ 3  ->  water = 3 at middle
        assert trap([3, 0, 3]) == 3

    def test_asymmetric_valley(self) -> None:
        # min(2,3)=2, height=0 -> 2
        assert trap([2, 0, 3]) == 2

    def test_multiple_valleys(self) -> None:
        # [3,0,3,0,3] -> two valleys of 3 each = 6
        assert trap([3, 0, 3, 0, 3]) == 6

    def test_plateau_in_middle(self) -> None:
        assert trap([5, 0, 0, 0, 5]) == 15

    def test_staircase_up_then_down(self) -> None:
        # [0,1,2,3,2,1,0] -> symmetric pyramid, no trapping
        assert trap([0, 1, 2, 3, 2, 1, 0]) == 0

    def test_deep_narrow_well(self) -> None:
        assert trap([10, 0, 10]) == 10

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0, 0]) == 0

    def test_large_uniform_walls(self) -> None:
        # [100000, 0, 0, ...(98 zeros)..., 100000] -> 100000 * 98
        height = [100000] + [0] * 98 + [100000]
        assert trap(height) == 100000 * 98

    def test_alternating(self) -> None:
        # [2,0,2,0,2] -> 2+2 = 4
        assert trap([2, 0, 2, 0, 2]) == 4

    def test_complex_terrain(self) -> None:
        # Hand-verified: [0,1,0,2,1,0,3,1,0,1,2]
        # Position:  0 1 2 3 4 5 6 7 8 9 10
        # Height:    0 1 0 2 1 0 3 1 0 1  2
        # Water:     0 0 1 0 1 2 0 1 2 1  0  = 8
        assert trap([0, 1, 0, 2, 1, 0, 3, 1, 0, 1, 2]) == 8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
