"""LeetCode 480: Sliding Window Median.

This module provides an O(n log k) implementation using a max-heap/min-heap
pair with lazy deletion.
"""

from __future__ import annotations

import heapq
from collections import defaultdict
from typing import DefaultDict


class DualHeap:
    def __init__(self, k: int) -> None:
        self.small: list[int] = []  # Max heap via negative values.
        self.large: list[int] = []  # Min heap.
        self.delayed: DefaultDict[int, int] = defaultdict(int)
        self.k = k
        self.small_size = 0
        self.large_size = 0

    def prune(self, heap: list[int]) -> None:
        while heap:
            num = -heap[0] if heap is self.small else heap[0]
            if self.delayed[num] > 0:
                self.delayed[num] -= 1
                if self.delayed[num] == 0:
                    del self.delayed[num]
                heapq.heappop(heap)
            else:
                break

    def rebalance(self) -> None:
        if self.small_size > self.large_size + 1:
            heapq.heappush(self.large, -heapq.heappop(self.small))
            self.small_size -= 1
            self.large_size += 1
            self.prune(self.small)
        elif self.small_size < self.large_size:
            heapq.heappush(self.small, -heapq.heappop(self.large))
            self.small_size += 1
            self.large_size -= 1
            self.prune(self.large)

    def add_num(self, num: int) -> None:
        if not self.small or num <= -self.small[0]:
            heapq.heappush(self.small, -num)
            self.small_size += 1
        else:
            heapq.heappush(self.large, num)
            self.large_size += 1
        self.rebalance()

    def remove_num(self, num: int) -> None:
        self.delayed[num] += 1
        if num <= -self.small[0]:
            self.small_size -= 1
            if num == -self.small[0]:
                self.prune(self.small)
        else:
            self.large_size -= 1
            if self.large and num == self.large[0]:
                self.prune(self.large)
        self.rebalance()

    def get_median(self) -> float:
        if self.k % 2 == 1:
            return float(-self.small[0])
        return (-self.small[0] + self.large[0]) / 2.0


def median_sliding_window(nums: list[int], k: int) -> list[float]:
    """Return medians for each sliding window of size ``k``.

    Args:
        nums: Input list of integers.
        k: Positive window size where ``1 <= k <= len(nums)``.

    Returns:
        A list of float medians.

    Raises:
        ValueError: If ``k`` is invalid for ``nums``.
    """

    if k <= 0 or k > len(nums):
        raise ValueError("k must satisfy 1 <= k <= len(nums)")

    dh = DualHeap(k)
    for i in range(k):
        dh.add_num(nums[i])

    result = [dh.get_median()]

    for i in range(k, len(nums)):
        dh.add_num(nums[i])
        dh.remove_num(nums[i - k])
        result.append(dh.get_median())

    return result
