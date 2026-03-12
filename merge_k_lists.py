"""
Merge k Sorted Lists

Given an array of k sorted linked lists, merge them into one sorted linked list.

Solution uses a min-heap (priority queue) to efficiently find the smallest
element among all k lists at each step.

Time Complexity: O(N log k) where N is total nodes, k is number of lists
Space Complexity: O(k) for the heap + O(1) for the result (excluding output)
"""

from __future__ import annotations

import heapq
from typing import Optional


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional[ListNode] = None):
        self.val = val
        self.next = next

    def __repr__(self) -> str:
        return f"ListNode({self.val})"

    def __lt__(self, other: "ListNode") -> bool:
        """For heap comparison based on node value."""
        return self.val < other.val


def merge_k_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists into one sorted linked list.

    Args:
        lists: List of sorted linked list heads (can include None)

    Returns:
        Head of the merged sorted linked list

    Example:
        >>> l1 = ListNode(1, ListNode(4, ListNode(5)))
        >>> l2 = ListNode(1, ListNode(3, ListNode(4)))
        >>> l3 = ListNode(2, ListNode(6))
        >>> merged = merge_k_lists([l1, l2, l3])
        >>> # Result: 1 -> 1 -> 2 -> 3 -> 4 -> 4 -> 5 -> 6
    """
    # Dummy node to simplify head handling
    dummy = ListNode(0)
    current = dummy

    # Initialize min-heap with (value, list_index, node)
    # list_index breaks ties when values are equal
    heap: list[tuple[int, int, ListNode]] = []

    for idx, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, idx, node))

    # Extract minimum and add next node from same list
    while heap:
        val, idx, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        if node.next:
            heapq.heappush(heap, (node.next.val, idx, node.next))

    return dummy.next


# Helper functions for testing
def list_to_linkedlist(values: list[int]) -> Optional[ListNode]:
    """Convert a Python list to a linked list."""
    if not values:
        return None
    dummy = ListNode(0)
    current = dummy
    for val in values:
        current.next = ListNode(val)
        current = current.next
    return dummy.next


def linkedlist_to_list(node: Optional[ListNode]) -> list[int]:
    """Convert a linked list to a Python list."""
    result = []
    while node:
        result.append(node.val)
        node = node.next
    return result
