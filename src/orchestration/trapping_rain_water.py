"""LeetCode #42 — Trapping Rain Water.

Given n non-negative integers representing an elevation map where the width
of each bar is 1, compute how much water it can trap after raining.

Three implementations provided:
  - two-pointer (O(n) time, O(1) space) — preferred
  - stack-based (O(n) time, O(n) space)
  - prefix-max (O(n) time, O(n) space)
"""

from __future__ import annotations


def trap_two_pointer(height: list[int]) -> int:
    """Two-pointer approach — optimal O(n) time, O(1) space."""
    if len(height) < 3:
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


def trap_stack(height: list[int]) -> int:
    """Monotonic-stack approach — O(n) time, O(n) space."""
    stack: list[int] = []
    water = 0

    for i, h in enumerate(height):
        while stack and height[stack[-1]] < h:
            bottom = height[stack.pop()]
            if not stack:
                break
            bounded_height = min(height[stack[-1]], h) - bottom
            width = i - stack[-1] - 1
            water += bounded_height * width
        stack.append(i)

    return water


def trap_prefix_max(height: list[int]) -> int:
    """Prefix/suffix max approach — O(n) time, O(n) space."""
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
