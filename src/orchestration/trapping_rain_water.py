"""LeetCode #42 — Trapping Rain Water.

Given n non-negative integers representing an elevation map where the width
of each bar is 1, compute how much water it can trap after raining.

Two-pointer O(n) time, O(1) space solution.
"""
from __future__ import annotations


def trap(height: list[int]) -> int:
    """Return total units of water trapped between bars.

    Uses the two-pointer technique: maintain left/right pointers and track
    the running max from each side. Water at any position is determined by
    the minimum of the two maxima minus the bar height at that position.
    """
    if not height:
        return 0

    left, right = 0, len(height) - 1
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
