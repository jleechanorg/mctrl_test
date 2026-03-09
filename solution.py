from typing import List


class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        """
        LeetCode 84 (Hard): Largest Rectangle in Histogram

        Monotonic increasing stack of indices.
        For each bar, pop higher bars and compute their max rectangle width
        using current index as the first smaller bar on the right.

        Time: O(n)
        Space: O(n)
        """
        max_area = 0
        stack: List[int] = []

        # Sentinel 0 flushes remaining bars in stack.
        for i, h in enumerate(heights + [0]):
            while stack and heights[stack[-1]] > h:
                height = heights[stack.pop()]
                left = stack[-1] if stack else -1
                width = i - left - 1
                max_area = max(max_area, height * width)
            stack.append(i)

        return max_area
