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
from typing import List


def trap(height: List[int]) -> int:
    """
    Calculate trapped rain water using the two-pointer approach.

    Algorithm:
    1. Use two pointers starting from both ends.
    2. Track the max height seen from the left and right.
    3. The pointer with the smaller max moves inward — water at that
       position is determined by its side's max minus its own height.
    4. Continue until pointers meet.

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


if __name__ == "__main__":
    # --- LeetCode examples ---
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6, "Example 1"
    assert trap([4, 2, 0, 3, 2, 5]) == 9, "Example 2"

    # --- Edge cases ---
    assert trap([]) == 0, "Empty list"
    assert trap([5]) == 0, "Single bar"
    assert trap([3, 7]) == 0, "Two bars"
    assert trap([0, 0, 0]) == 0, "All zeros"
    assert trap([3, 3, 3]) == 0, "Flat surface"

    # --- Monotonic sequences (no water) ---
    assert trap([1, 2, 3, 4, 5]) == 0, "Strictly ascending"
    assert trap([5, 4, 3, 2, 1]) == 0, "Strictly descending"

    # --- Simple traps ---
    assert trap([2, 0, 2]) == 2, "Single valley"
    assert trap([3, 0, 0, 3]) == 6, "Wide valley"
    assert trap([5, 0, 5]) == 5, "Deep valley"

    # --- Asymmetric walls ---
    assert trap([3, 0, 1]) == 1, "Right wall shorter"
    assert trap([1, 0, 3]) == 1, "Left wall shorter"
    assert trap([5, 2, 1, 2, 1, 5]) == 14, "Tall outer walls"

    # --- Multiple valleys ---
    assert trap([3, 0, 3, 0, 3]) == 6, "Two valleys"
    assert trap([2, 0, 2, 0, 2, 0, 2]) == 6, "Three valleys"

    # --- Staircase patterns ---
    assert trap([0, 1, 0, 2, 0, 3, 0, 2, 0, 1, 0]) == 6, "Rising then falling stairs"

    # --- Large uniform trap ---
    assert trap([10] + [0] * 100 + [10]) == 1000, "Wide uniform valley"

    # --- Single-unit traps scattered ---
    assert trap([1, 0, 1, 0, 1, 0, 1]) == 3, "Alternating 1-0"

    # --- Peak in the middle ---
    assert trap([1, 2, 3, 4, 3, 2, 1]) == 0, "Mountain (no water)"

    print("All tests passed!")
