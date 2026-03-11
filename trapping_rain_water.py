"""
LeetCode 42 - Trapping Rain Water

Given n non-negative integers representing an elevation map where the width of each bar is 1,
compute how much water it can trap after raining.

https://leetcode.com/problems/trapping-rain-water/
"""

from __future__ import annotations


def trap(height: list[int]) -> int:
    """
    Calculate how much water can be trapped between bars.

    Uses two-pointer approach: maintain left and right pointers moving inward,
    tracking max heights from both sides.

    For each position, water trapped = min(max_left, max_right) - height[i]

    Args:
        height: List of non-negative integers representing bar heights

    Returns:
        Total units of water that can be trapped

    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not height:
        return 0

    left, right = 0, len(height) - 1
    left_max, right_max = 0, 0
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


def trap_dp(height: list[int]) -> int:
    """
    Calculate trapped water using dynamic programming (pre-computation).

    Pre-computes max height to the left and right of each position.

    Args:
        height: List of non-negative integers representing bar heights

    Returns:
        Total units of water that can be trapped

    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    if not height:
        return 0

    n = len(height)
    left_max = [0] * n
    right_max = [0] * n

    # Compute left max for each position
    left_max[0] = height[0]
    for i in range(1, n):
        left_max[i] = max(left_max[i - 1], height[i])

    # Compute right max for each position
    right_max[n - 1] = height[n - 1]
    for i in range(n - 2, -1, -1):
        right_max[i] = max(right_max[i + 1], height[i])

    # Calculate water trapped
    water = 0
    for i in range(n):
        water += min(left_max[i], right_max[i]) - height[i]

    return water


def trap_stack(height: list[int]) -> int:
    """
    Calculate trapped water using a monotonic stack.

    Uses a stack to track bars in decreasing order and computes water
    when a wider bar is found.

    Args:
        height: List of non-negative integers representing bar heights

    Returns:
        Total units of water that can be trapped

    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    if not height:
        return 0

    stack = []
    water = 0

    for i, h in enumerate(height):
        # Process when we find a bar higher than stack top
        while stack and h > height[stack[-1]]:
            top = stack.pop()
            if not stack:
                break
            distance = i - stack[-1] - 1
            bounded_height = min(h, height[stack[-1]]) - height[top]
            water += distance * bounded_height
        stack.append(i)

    return water


if __name__ == "__main__":
    # Example usage
    print(trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]))  # 6
    print(trap([4, 2, 0, 3, 2, 5]))  # 9
