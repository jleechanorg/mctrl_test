"""LeetCode #23 - Merge k Sorted Lists.

Merge k sorted linked lists and return it as one sorted list.
Uses a min-heap for O(N log k) time complexity.
"""
from __future__ import annotations

import heapq
from typing import Optional


class ListNode:
    def __init__(self, val: int = 0, next: Optional[ListNode] = None):
        self.val = val
        self.next = next


def merge_k_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """Merge k sorted linked lists into one sorted list.

    Time: O(N log k) where N is total nodes, k is number of lists.
    Space: O(k) for the heap.
    """
    heap: list[tuple[int, int, ListNode]] = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    dummy = ListNode(0)
    current = dummy

    while heap:
        val, idx, node = heapq.heappop(heap)
        current.next = node
        current = current.next
        if node.next:
            heapq.heappush(heap, (node.next.val, idx, node.next))

    return dummy.next


# Helpers for testing
def build_list(values: list[int]) -> Optional[ListNode]:
    """Build a linked list from a list of integers."""
    dummy = ListNode(0)
    current = dummy
    for v in values:
        current.next = ListNode(v)
        current = current.next
    return dummy.next


def to_list(node: Optional[ListNode]) -> list[int]:
    """Convert a linked list to a Python list."""
    result: list[int] = []
    while node:
        result.append(node.val)
        node = node.next
    return result
