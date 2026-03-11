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
Space Complexity: O(1) for two-pointer approach
"""

from __future__ import annotations
from typing import List


def trap(height: List[int]) -> int:
    """
    Calculate trapped rain water using the two-pointer technique.

    The key insight: water at any position is determined by the minimum of
    the maximum height to its left and the maximum height to its right,
    minus the height at that position.

    Two pointers converge from both ends. We always advance the pointer
    with the smaller max, because that side is the bottleneck for water level.

    Args:
        height: List of non-negative integers representing elevation map.

    Returns:
        Total units of trapped water.
    """
    if len(height) < 3:
        return 0

    left = 0
    right = len(height) - 1
    left_max = height[left]
    right_max = height[right]
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


def trap_dp(height: List[int]) -> int:
    """
    Alternative DP approach for verification.

    Pre-compute left_max[i] and right_max[i] arrays, then sum
    min(left_max[i], right_max[i]) - height[i] for each position.

    Time: O(n), Space: O(n)
    """
    n = len(height)
    if n < 3:
        return 0

    left_max = [0] * n
    right_max = [0] * n

    left_max[0] = height[0]
    for i in range(1, n):
        left_max[i] = max(left_max[i - 1], height[i])

    right_max[n - 1] = height[n - 1]
    for i in range(n - 2, -1, -1):
        right_max[i] = max(right_max[i + 1], height[i])

    water = 0
    for i in range(n):
        water += min(left_max[i], right_max[i]) - height[i]

    return water


# --------------- pytest test suite ---------------

import pytest


class TestTrappingRainWater:
    """Focused tests for LeetCode #42."""

    def test_example_1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_example_2(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9

    def test_empty_and_tiny(self) -> None:
        assert trap([]) == 0
        assert trap([5]) == 0
        assert trap([3, 7]) == 0

    def test_flat(self) -> None:
        assert trap([3, 3, 3, 3]) == 0

    def test_ascending(self) -> None:
        assert trap([1, 2, 3, 4, 5]) == 0

    def test_descending(self) -> None:
        assert trap([5, 4, 3, 2, 1]) == 0

    def test_single_valley(self) -> None:
        # |     |
        # | _ _ |
        # 3 0 0 3  -> water = 6
        assert trap([3, 0, 0, 3]) == 6

    def test_asymmetric_valley(self) -> None:
        # Water bounded by the shorter wall
        # 5 _ 3  -> min(5,3)=3, positions 1 has height 0 -> 3 water
        assert trap([5, 0, 3]) == 3

    def test_multiple_valleys(self) -> None:
        #  3   3   3
        #  | _ | _ |
        #  3 0 3 0 3  -> 2 valleys of 3 each = 6
        assert trap([3, 0, 3, 0, 3]) == 6

    def test_staircase_down_up(self) -> None:
        # 4 3 2 1 2 3 4 -> valley in middle
        # water at each position: 0,1,2,3,2,1,0 = 9
        assert trap([4, 3, 2, 1, 2, 3, 4]) == 9

    def test_tall_walls_deep_valley(self) -> None:
        assert trap([100000, 0, 100000]) == 100000

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0, 0]) == 0

    def test_plateau_with_dip(self) -> None:
        # 5 5 1 5 5 -> dip of 4 at index 2
        assert trap([5, 5, 1, 5, 5]) == 4

    def test_dp_matches_two_pointer(self) -> None:
        """Cross-validate both implementations on several inputs."""
        cases = [
            [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],
            [4, 2, 0, 3, 2, 5],
            [3, 0, 3, 0, 3],
            [1, 0, 2, 0, 3, 0, 2, 0, 1],
            [5, 2, 1, 2, 1, 5],
            [0, 7, 1, 4, 6],
        ]
        for h in cases:
            assert trap(h) == trap_dp(h), f"Mismatch on {h}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
