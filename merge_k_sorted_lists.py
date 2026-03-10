"""
Merge k Sorted Lists - LeetCode 23 (Hard)

You are given an array of k linked-lists lists, each linked-list is sorted in ascending order.
Merge all the linked-lists into one sorted linked-list and return it.

Approach: Use a min-heap to efficiently find the minimum element among all lists.
- Time Complexity: O(N log k) where N = total nodes, k = number of lists
- Space Complexity: O(k) for the heap

Alternative approaches:
1. Brute force: Collect all values, sort, rebuild - O(N log N)
2. Divide and conquer: Pairwise merging - O(N log k)
"""

from __future__ import annotations

import heapq
from typing import Optional


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

    def __lt__(self, other: 'ListNode') -> bool:
        """Required for heap comparison."""
        return self.val < other.val

    @classmethod
    def from_list(cls, values: list[int]) -> Optional['ListNode']:
        """Create a linked list from a list of values."""
        if not values:
            return None
        dummy = cls()
        current = dummy
        for val in values:
            current.next = cls(val)
            current = current.next
        return dummy.next

    def to_list(self) -> list[int]:
        """Convert linked list to Python list for easy verification."""
        result = []
        current = self
        while current:
            result.append(current.val)
            current = current.next
        return result


def merge_k_sorted_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists into one sorted linked list.

    Args:
        lists: List of k sorted linked lists

    Returns:
        The merged sorted linked list

    Example:
        >>> list1 = ListNode.from_list([1, 4, 5])
        >>> list2 = ListNode.from_list([1, 3, 4])
        >>> list3 = ListNode.from_list([2, 6])
        >>> merged = merge_k_sorted_lists([list1, list2, list3])
        >>> merged.to_list()
        [1, 1, 2, 3, 4, 4, 5, 6]
    """
    # Handle edge cases
    k = len(lists)
    if k == 0:
        return None

    # Count non-empty lists
    non_empty = [l for l in lists if l is not None]
    if not non_empty:
        return None

    # Initialize heap with first node from each non-empty list
    # Heap stores (value, list_index, node) tuples
    heap = []
    for i, head in enumerate(non_empty):
        heapq.heappush(heap, (head.val, i, head))

    # Dummy node to simplify head/tail manipulation
    dummy = ListNode(-1)
    current = dummy

    # Extract min, add to result, push next from same list
    while heap:
        val, list_idx, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        # Push next node from same list if exists
        if node.next:
            heapq.heappush(heap, (node.next.val, list_idx, node.next))

    return dummy.next


# Optimized version using index-based heap for better memory
def merge_k_sorted_lists_optimized(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Optimized version that uses list indices instead of ListNode objects in heap.
    This is more memory efficient for very large k.
    """
    k = len(lists)
    if k == 0:
        return None

    # Track current position in each list
    curr = [l for l in lists]

    # Filter out None lists and track original indices
    valid = [(curr[i], i) for i in range(k) if curr[i] is not None]
    if not valid:
        return None

    # Initialize heap with (value, list_index)
    heap = [(node.val, i) for node, i in valid]
    heapq.heapify(heap)

    dummy = ListNode(-1)
    tail = dummy

    while heap:
        val, i = heapq.heappop(heap)
        tail.next = curr[i]
        tail = tail.next
        curr[i] = curr[i].next

        if curr[i]:
            heapq.heappush(heap, (curr[i].val, i))

    return dummy.next
