"""
LeetCode #239 - Sliding Window Maximum

Given an integer array nums, there is a sliding window of size k which moves from
the very left to the very right. Only the k numbers in each sliding window are
considered. Return the max sliding window as an array.

Example 1:
    Input: nums = [1,3,-1,-3,5,3,6,7], k = 3
    Output: [3,3,5,5,6,7]

Example 2:
    Input: nums = [1], k = 1
    Output: [1]

Constraints:
    - 1 <= nums.length <= 10^5
    - -10^4 <= nums[i] <= 10^4
    - 1 <= k <= nums.length
"""
from __future__ import annotations
from collections import deque


def max_sliding_window(nums: list[int], k: int) -> list[int]:
    """
    Find the maximum element in each sliding window of size k.

    Uses a monotonic deque (decreasing order) to achieve O(n) time complexity.
    The deque stores indices, and we maintain elements in decreasing order.

    Args:
        nums: List of integers
        k: Size of the sliding window

    Returns:
        List of maximum values in each window position

    Time Complexity: O(n) - each element is pushed and popped at most once
    Space Complexity: O(k) - deque holds at most k elements
    """
    if not nums or k == 0:
        return []

    if k == 1:
        return nums[:]

    n = len(nums)
    result = []
    # Monotonic decreasing deque - stores indices
    dq = deque()

    for i in range(n):
        # Remove indices that are out of the current window
        while dq and dq[0] < i - k + 1:
            dq.popleft()

        # Remove indices whose corresponding values are less than current
        # These can never be the maximum while current element is in window
        while dq and nums[dq[-1]] < nums[i]:
            dq.pop()

        # Add current index
        dq.append(i)

        # Start recording results once we have a full window
        if i >= k - 1:
            result.append(nums[dq[0]])

    return result


if __name__ == "__main__":
    # Example usage
    nums = [1, 3, -1, -3, 5, 3, 6, 7]
    k = 3
    print(f"Input: nums={nums}, k={k}")
    print(f"Output: {max_sliding_window(nums, k)}")
    print(f"Expected: [3, 3, 5, 5, 6, 7]")
