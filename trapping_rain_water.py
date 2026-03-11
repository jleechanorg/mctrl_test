"""LeetCode 42 - Trapping Rain Water

Given n non-negative integers representing an elevation map where the width
of each bar is 1, compute how much water it can trap after raining.
"""

from __future__ import annotations


def trap(height: list[int]) -> int:
    """Two-pointer O(n) time, O(1) space solution."""
    left, right = 0, len(height) - 1
    left_max = right_max = 0
    water = 0

    while left < right:
        if height[left] < height[right]:
            if height[left] >= left_max:
                left_max = height[left]
            else:
                water += left_max - height[left]
            left += 1
        else:
            if height[right] >= right_max:
                right_max = height[right]
            else:
                water += right_max - height[right]
            right -= 1

    return water
