"""
LeetCode Hard: Trapping Rain Water

Given n non-negative integers representing an elevation map where the width of each bar is 1,
compute how much water it can trap after raining.

Example:
Input: height = [0,1,0,2,1,0,1,3,2,1,2,1]
Output: 6
Explanation: The elevation map is represented by array [0,1,0,2,1,0,1,3,2,1,2,1].
In this case, 6 units of rain water are being trapped.

Time Complexity: O(n) - single pass with two pointers
Space Complexity: O(1) - constant extra space
"""

from typing import List


class Solution:
    def trap(self, height: List[int]) -> int:
        """
        Using two-pointer approach:
        - Track max height from left and right
        - At each position, water trapped = min(left_max, right_max) - height[i]
        """
        if not height:
            return 0

        left, right = 0, len(height) - 1
        left_max, right_max = height[left], height[right]
        water = 0

        while left < right:
            if left_max < right_max:
                left += 1
                left_max = max(left_max, height[left])
                water += left_max - height[left]
            else:
                right -= 1
                right_max = max(right_max, height[right])
                water += right_max - height[right]

        return water


def trap_brute_force(height: List[int]) -> int:
    """
    Brute force approach for reference.
    Time: O(n^2), Space: O(1)
    """
    if not height:
        return 0

    n = len(height)
    water = 0

    for i in range(1, n - 1):
        left_max = max(height[:i])
        right_max = max(height[i + 1:])
        trapped = min(left_max, right_max) - height[i]
        water += max(0, trapped)

    return water


def trap_dp(height: List[int]) -> int:
    """
    Dynamic programming approach.
    Time: O(n), Space: O(n)
    """
    if not height:
        return 0

    n = len(height)
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


if __name__ == "__main__":
    sol = Solution()

    # Test cases
    test_cases = [
        ([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1], 6),
        ([4, 2, 0, 3, 2, 5], 9),
        ([], 0),
        ([1, 0, 1], 1),
        ([5, 4, 1, 2], 1),
        ([1, 2, 3, 4, 5], 0),
    ]

    for i, (height, expected) in enumerate(test_cases, 1):
        result = sol.trap(height)
        status = "✓" if result == expected else "✗"
        print(f"Test {i}: {status} trap({height}) = {result}, expected {expected}")
