"""
LeetCode #1: Two Sum

Given an array of integers nums and an integer target, return indices of the two numbers
such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the
same element twice.

You can return the answer in any order.

Example 1:
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].

Example 2:
Input: nums = [3,2,4], target = 6
Output: [1,2]

Example 3:
Input: nums = [3,3], target = 6
Output: [0,1]

Constraints:
- 2 <= nums.length <= 10^4
- -10^9 <= nums[i] <= 10^9
- -10^9 <= target <= 10^9
- Only one valid answer exists.

Time Complexity: O(n)
Space Complexity: O(n)
"""
from __future__ import annotations


def two_sum(nums: list[int], target: int) -> list[int]:
    """
    Find two numbers in the array that add up to the target.

    Args:
        nums: List of integers
        target: The target sum

    Returns:
        List of two indices that sum to target

    Raises:
        ValueError: If no two numbers sum to target
    """
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    raise ValueError("No two sum solution")


def two_sum_brute_force(nums: list[int], target: int) -> list[int]:
    """
    Brute force O(n^2) solution for comparison.
    """
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return [i, j]
    raise ValueError("No two sum solution")
