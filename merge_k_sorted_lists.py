from __future__ import annotations

from heapq import heappush, heappop
from typing import Optional


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional["ListNode"] = None):
        self.val = val
        self.next = next


def merge_k_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """Merge k sorted linked lists into one sorted linked list.

    Args:
        lists: List of heads of k sorted linked lists (may be None)

    Returns:
        Head of the merged sorted linked list
    """
    # Use a min-heap to always get the smallest element
    heap: list[tuple[int, int, ListNode]] = []  # (value, index, node)

    for i, node in enumerate(lists):
        if node:
            heappush(heap, (node.val, i, node))

    dummy = ListNode(0)
    current = dummy

    while heap:
        val, i, node = heappop(heap)
        current.next = node
        current = current.next

        if node.next:
            heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def list_to_linked_list(values: list[int]) -> Optional[ListNode]:
    """Convert a list to a linked Python list."""
    if not values:
        return None

    dummy = ListNode(0)
    current = dummy
    for val in values:
        current.next = ListNode(val)
        current = current.next

    return dummy.next


def linked_list_to_list(node: Optional[ListNode]) -> list[int]:
    """Convert a linked list to a Python list."""
    result = []
    while node:
        result.append(node.val)
        node = node.next
    return result
