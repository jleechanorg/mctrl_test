"""
Trapping Rain Water - LeetCode Hard #42

Given n non-negative integers representing an elevation map where the width of each bar is 1,
compute how much water it can trap after raining.

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

Time Complexity: O(n) using two-pointer approach
Space Complexity: O(1)
"""

from __future__ import annotations
from typing import List


def trap(height: List[int]) -> int:
    """
    Calculate trapped rain water using two-pointer technique.

    The key insight: water at any position is determined by the minimum of
    the maximum height to its left and the maximum height to its right,
    minus the height at that position.

    Two pointers converge from both ends. We track the max height seen
    from each side. The pointer with the smaller max moves inward, because
    we know the water level at that pointer is bounded by its side's max
    (the other side is at least as tall).

    Args:
        height: List of non-negative integers representing elevation map.

    Returns:
        Total units of trapped rain water.
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
