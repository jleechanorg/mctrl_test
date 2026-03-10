"""
Merge k Sorted Lists - LeetCode Hard Problem

Given an array of k linked-lists lists, each linked-list is sorted in ascending order.
Merge all the linked-lists into one sorted linked-list and return it.

This implementation uses a heap (priority queue) for optimal time complexity.

Time Complexity: O(N log k) where N is total nodes, k is number of lists
Space Complexity: O(k) for the heap
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


def merge_k_lists_heap(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using a min-heap.

    Uses heapq to always pick the smallest next node across all lists.
    Heap stores tuples of (value, list_index, node) for proper ordering.
    """
    # Dummy head to simplify edge cases
    dummy = ListNode(0)
    current = dummy

    # Min-heap: (value, list_index, node)
    heap = []

    # Initialize heap with first node from each non-empty list
    for i, head in enumerate(lists):
        if head:
            heapq.heappush(heap, (head.val, i, head))

    # Extract min and add next node from same list
    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_lists_divide_conquer(
    lists: list[Optional[ListNode]],
) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer.

    Recursively pairs up lists and merges them until one remains.
    """
    if not lists:
        return None

    # Base case: single list
    if len(lists) == 1:
        return lists[0]

    # Merge pairs
    new_lists = []
    for i in range(0, len(lists), 2):
        if i + 1 < len(lists):
            new_lists.append(_merge_two_lists(lists[i], lists[i + 1]))
        else:
            new_lists.append(lists[i])

    return merge_k_lists_divide_conquer(new_lists)


def _merge_two_lists(
    l1: Optional[ListNode], l2: Optional[ListNode]
) -> Optional[ListNode]:
    """Merge two sorted linked lists."""
    dummy = ListNode(0)
    current = dummy

    while l1 and l2:
        if l1.val <= l2.val:
            current.next = l1
            l1 = l1.next
        else:
            current.next = l2
            l2 = l2.next
        current = current.next

    current.next = l1 or l2
    return dummy.next


# --- Helper functions for testing ---

def list_to_linkedlist(values: list[int]) -> Optional[ListNode]:
    """Convert Python list to linked list."""
    if not values:
        return None

    dummy = ListNode(0)
    current = dummy
    for val in values:
        current.next = ListNode(val)
        current = current.next

    return dummy.next


def linkedlist_to_list(node: Optional[ListNode]) -> list[int]:
    """Convert linked list to Python list."""
    result = []
    while node:
        result.append(node.val)
        node = node.next
    return result
