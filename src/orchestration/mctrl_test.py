"""LeetCode #42 — Trapping Rain Water.

Given n non-negative integers representing an elevation map where the width
of each bar is 1, compute how much water it can trap after raining.

Two-pointer O(n) time, O(1) space solution.
"""
from __future__ import annotations


def trap(height: list[int]) -> int:
    """Return total units of water trapped between bars.

    Uses the two-pointer technique: maintain left/right pointers and
    track the max height seen from each side.  At each step, advance
    the pointer on the lower side — the water above that bar is
    determined by the known max on its side (the other side is at
    least as high).

    >>> trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1])
    6
    >>> trap([4, 2, 0, 3, 2, 5])
    9
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
