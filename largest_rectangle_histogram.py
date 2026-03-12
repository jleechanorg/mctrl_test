"""
Largest Rectangle in Histogram

Given an array of heights representing a histogram, find the largest rectangle
that can be formed within the bounds of the histogram.

Approach: Monotonic Stack
-------------------------
We use a monotonic increasing stack to track indices of bars.
When we encounter a bar shorter than the stack top, we know the height at
the stack top can't extend further to the right, so we calculate its area.

For each bar at index i with height h:
- Width = right_boundary - left_boundary - 1
- right_boundary = current index i (where smaller bar found)
- left_boundary = index after the previous smaller bar in stack

Time Complexity: O(n) - each bar is pushed and popped at most once
Space Complexity: O(n) - for the stack
"""
from typing import List


def largest_rectangle_area(heights: List[int]) -> int:
    """
    Find the largest rectangle area in a histogram.

    Args:
        heights: List of non-negative integers representing bar heights.

    Returns:
        The largest rectangle area that can be formed.

    Examples:
        >>> largest_rectangle_area([2, 1, 5, 6, 2, 3])
        10
        >>> largest_rectangle_area([2, 4])
        4
    """
    if not heights:
        return 0

    stack: List[int] = []  # stores indices
    max_area = 0
    n = len(heights)

    for i in range(n):
        # While current height is less than height at stack top,
        # calculate areas for bars in the stack
        while stack and heights[i] < heights[stack[-1]]:
            h = heights[stack.pop()]
            # Width calculation:
            # - If stack is empty, width = i (bars from start to i-1)
            # - Otherwise, width = i - stack[-1] - 1
            w = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, h * w)

        stack.append(i)

    # Process remaining bars in stack
    # These bars extend to the right edge of the histogram
    while stack:
        h = heights[stack.pop()]
        w = n if not stack else n - stack[-1] - 1
        max_area = max(max_area, h * w)

    return max_area


def largest_rectangle_area_2(heights: List[int]) -> int:
    """
    Alternative O(n) solution using a sentinel-based approach.

    Adds sentinel values (0) at both ends to simplify boundary handling,
    avoiding the final while loop to process remaining stack elements.

    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    if not heights:
        return 0

    # Add sentinel at the end to flush remaining stack
    stack: List[int] = [-1]  # Use -1 as sentinel for left boundary
    max_area = 0

    for i, h in enumerate(heights):
        # While current height is less than height at stack top,
        # calculate and pop areas
        while stack[-1] != -1 and h < heights[stack[-1]]:
            height = heights[stack.pop()]
            width = i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)

    # Process remaining bars (all extend to the right boundary)
    n = len(heights)
    while len(stack) > 1:  # Keep the sentinel
        height = heights[stack.pop()]
        width = n - stack[-1] - 1
        max_area = max(max_area, height * width)

    return max_area


if __name__ == "__main__":
    # Example usage
    test_cases = [
        [2, 1, 5, 6, 2, 3],  # Expected: 10
        [2, 4],              # Expected: 4
        [1, 2, 3, 4, 5],    # Expected: 9
        [5, 4, 3, 2, 1],    # Expected: 9
        [2, 1, 2],          # Expected: 3
        [],                 # Expected: 0
        [1],                # Expected: 1
        [1, 1],             # Expected: 2
    ]

    for heights in test_cases:
        result = largest_rectangle_area(heights)
        print(f"heights={heights} -> largest area = {result}")
