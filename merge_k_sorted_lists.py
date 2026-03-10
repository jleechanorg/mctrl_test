from __future__ import annotations

from heapq import heappush, heappop
from typing import Optional


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional[ListNode] = None):
        self.val = val
        self.next = next


def merge_k_sorted_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists and return it as one sorted list.

    Uses a min-heap to efficiently find the smallest element across all lists.
    Time complexity: O(N log k) where N is total nodes, k is number of lists
    Space complexity: O(k) for the heap

    Args:
        lists: List of sorted linked list heads

    Returns:
        Head of the merged sorted linked list
    """
    if not lists:
        return None

    # Create a min-heap with (value, list_index, node)
    # We include list_index to handle duplicate values correctly
    heap: list[tuple[int, int, ListNode]] = []

    # Initialize heap with first node from each non-empty list
    for i, head in enumerate(lists):
        if head:
            heappush(heap, (head.val, i, head))

    # Dummy head to simplify edge cases
    dummy = ListNode(0)
    current = dummy

    while heap:
        val, i, node = heappop(heap)
        current.next = node
        current = current.next

        # Add next node from same list if available
        if node.next:
            heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def list_to_linked(arr: list[int]) -> Optional[ListNode]:
    """Convert a Python list to a linked list."""
    if not arr:
        return None
    dummy = ListNode(0)
    current = dummy
    for val in arr:
        current.next = ListNode(val)
        current = current.next
    return dummy.next


def linked_to_list(head: Optional[ListNode]) -> list[int]:
    """Convert a linked list to a Python list."""
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result
