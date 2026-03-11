from __future__ import annotations

from collections import deque


def max_sliding_window(nums: list[int], k: int) -> list[int]:
    """LeetCode 239 - Sliding Window Maximum.

    Given an array nums and a sliding window of size k moving from left
    to right, return the max value in each window position.

    Uses a monotonic decreasing deque for O(n) time.
    """
    if not nums or k == 0:
        return []

    result: list[int] = []
    dq: deque[int] = deque()  # stores indices

    for i, val in enumerate(nums):
        # Remove indices outside the current window
        while dq and dq[0] < i - k + 1:
            dq.popleft()

        # Remove smaller elements from the back
        while dq and nums[dq[-1]] < val:
            dq.pop()

        dq.append(i)

        # Window is fully formed starting at index k-1
        if i >= k - 1:
            result.append(nums[dq[0]])

    return result
