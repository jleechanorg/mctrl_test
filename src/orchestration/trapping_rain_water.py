"""LeetCode #42 — Trapping Rain Water.

Given n non-negative integers representing an elevation map where the width
of each bar is 1, compute how much water it can trap after raining.

Two-pointer O(n) time, O(1) space solution.
"""

from __future__ import annotations


def trap(height: list[int]) -> int:
    """Return total units of water trapped between bars.

    Uses the two-pointer technique: maintain left/right pointers and track
    the running max height from each side. Water at any position is
    determined by the minimum of the two maxes minus the bar height.

    Args:
        height: List of non-negative integers representing bar heights.

    Returns:
        Total trapped water units.
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
