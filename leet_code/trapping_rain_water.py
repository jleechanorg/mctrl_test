"""
Trapping Rain Water - LeetCode Hard #42

Given n non-negative integers representing an elevation map where the width
of each bar is 1, compute how much water it can trap after raining.

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


def trap(height: list[int]) -> int:
    """
    Calculate trapped rain water using two-pointer technique.

    The key insight: water at any position is determined by
    min(max_left, max_right) - height[position].

    Two pointers converge from both ends. We track the running
    max from each side. The smaller side determines the water
    level, so we advance from that side.
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


def trap_dp(height: list[int]) -> int:
    """
    DP approach for verification: precompute left_max and right_max arrays.

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
