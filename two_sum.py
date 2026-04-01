"""
Two Sum — LeetCode 1

Given an array of integers nums and an integer target, return indices of the two
numbers such that they add up to target. You may not use the same element twice.

Raises:
    ValueError: If no pair of elements sums to ``target``.
"""
from __future__ import annotations

from typing import List


def two_sum(nums: List[int], target: int) -> List[int]:
    """
    O(n) time, O(n) space: hash map of value -> index while scanning.
    """
    seen: dict[int, int] = {}
    for i, x in enumerate(nums):
        need = target - x
        if need in seen:
            return [seen[need], i]
        seen[x] = i
    raise ValueError("No two elements sum to target")
