"""
LeetCode 84: Largest Rectangle in Histogram

Given an array of heights representing a histogram, find the largest rectangle
that can be formed in the histogram.

Approach: Monotonic Stack
- Use a monotonic increasing stack to track bar indices
- When a shorter bar is encountered, pop taller bars and calculate areas
- Add a sentinel bar (height 0) at the end to flush the stack

Time Complexity: O(n) - each bar is pushed and popped at most once
Space Complexity: O(n) - for the stack
"""

from typing import List


def largest_rectangle_area(heights: List[int]) -> int:
    """
    Find the largest rectangle area in a histogram.

    Args:
        heights: List of non-negative integers representing bar heights

    Returns:
        The largest rectangular area that can be formed

    Example:
        >>> largest_rectangle_area([2, 1, 5, 6, 2, 3])
        10
    """
    if not heights:
        return 0

    stack: List[int] = []  # stores indices
    max_area = 0

    # Add sentinel to flush remaining bars in stack
    for i, height in enumerate(heights + [0]):
        # While current bar is shorter than stack top, calculate areas
        while stack and heights[stack[-1]] > height:
            h = heights[stack.pop()]
            # Width extends from after the bar at stack top to current index
            w = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, h * w)
        stack.append(i)

    return max_area


def largest_rectangle_area_brute(heights: List[int]) -> int:
    """
    Brute force solution for comparison - O(n^2) time.

    For each bar, expand left and right to find the maximum width
    where this bar is the shortest.
    """
    if not heights:
        return 0

    max_area = 0
    n = len(heights)

    for i in range(n):
        # Expand left
        left = i
        while left > 0 and heights[left - 1] >= heights[i]:
            left -= 1

        # Expand right
        right = i
        while right < n - 1 and heights[right + 1] >= heights[i]:
            right += 1

        width = right - left + 1
        max_area = max(max_area, heights[i] * width)

    return max_area


# Definition for ListNode (if we need to compare with merge-k-lists)
class ListNode:
    """Definition for singly-linked list node."""
    def __init__(self, val: int = 0, next: 'ListNode' = None):
        self.val = val
        self.next = next

    def __repr__(self):
        return f"ListNode({self.val})"


if __name__ == "__main__":
    # Test cases
    test_cases = [
        ([2, 1, 5, 6, 2, 3], 10),  # Expected: 10
        ([2, 4], 4),               # Expected: 4
        ([1], 1),                  # Expected: 1
        ([1, 1], 1),               # Expected: 1 (both bars same height)
        ([0, 0], 0),               # Expected: 0
        ([2, 1, 2], 3),           # Expected: 3
        ([1, 2, 3, 4, 5], 9),     # Expected: 9
        ([5, 4, 3, 2, 1], 9),     # Expected: 9
    ]

    print("Testing largest_rectangle_area:")
    for heights, expected in test_cases:
        result = largest_rectangle_area(heights)
        status = "✓" if result == expected else "✗"
        print(f"  {status} heights={heights}, expected={expected}, got={result}")

    print("\nComparing with brute force:")
    for heights, expected in test_cases:
        opt = largest_rectangle_area(heights)
        brute = largest_rectangle_area_brute(heights)
        match = "✓" if opt == brute else "✗"
        print(f"  {match} Optimized={opt}, Brute={brute}")
