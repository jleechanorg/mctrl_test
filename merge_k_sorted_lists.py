"""
Merge k Sorted Lists - LeetCode #23 (Hard)

You are given an array of k linked-lists, each linked-list is sorted in ascending order.
Merge all the linked-lists into one sorted linked-list and return it.

Approach: Use a min-heap to efficiently get the smallest element among all lists.
- Time Complexity: O(N log k) where N is total nodes, k is number of lists
- Space Complexity: O(k) for the heap

Alternative divide-and-conquer approach:
- Time Complexity: O(N log k)
- Space Complexity: O(1) extra space (excluding recursion stack)
"""

from __future__ import annotations
from typing import Optional
import heapq


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional[ListNode] = None):
        self.val = val
        self.next = next

    def __repr__(self) -> str:
        return f"ListNode({self.val})"

    def __lt__(self, other: "ListNode") -> bool:
        """Required for heap comparison."""
        return self.val < other.val


def merge_k_lists_heap(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using a min-heap.

    Args:
        lists: List of sorted linked list heads (can be None)

    Returns:
        Head of the merged sorted linked list

    Time Complexity: O(N log k)
    Space Complexity: O(k)
    """
    # Min-heap stores (value, list_index, node) tuples
    # list_index ensures deterministic comparison when values are equal
    heap = []

    # Initialize heap with first node from each non-empty list
    for i, head in enumerate(lists):
        if head:
            heapq.heappush(heap, (head.val, i, head))

    # Dummy node to simplify head/tail manipulation
    dummy = ListNode(0)
    tail = dummy

    # Extract min and add next node from same list
    while heap:
        val, i, node = heapq.heappop(heap)
        tail.next = node
        tail = tail.next

        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_lists_divide_conquer(
    lists: list[Optional[ListNode]],
) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide-and-conquer.

    Pairs up lists and merges them recursively.

    Args:
        lists: List of sorted linked list heads (can be None)

    Returns:
        Head of the merged sorted linked list

    Time Complexity: O(N log k)
    Space Complexity: O(log k) for recursion stack
    """
    if not lists:
        return None

    if len(lists) == 1:
        return lists[0]

    mid = len(lists) // 2
    left = merge_k_lists_divide_conquer(lists[:mid])
    right = merge_k_lists_divide_conquer(lists[mid:])

    return _merge_two_lists(left, right)


def _merge_two_lists(
    l1: Optional[ListNode], l2: Optional[ListNode]
) -> Optional[ListNode]:
    """Merge two sorted linked lists into one sorted list."""
    dummy = ListNode(0)
    tail = dummy

    while l1 and l2:
        if l1.val <= l2.val:
            tail.next = l1
            l1 = l1.next
        else:
            tail.next = l2
            l2 = l2.next
        tail = tail.next

    tail.next = l1 or l2
    return dummy.next


# Convenience function to create linked list from list
def create_linked_list(values: list[int]) -> Optional[ListNode]:
    """Create a linked list from a list of values."""
    if not values:
        return None

    dummy = ListNode(0)
    tail = dummy
    for val in values:
        tail.next = ListNode(val)
        tail = tail.next

    return dummy.next


# Convenience function to convert linked list to list
def linked_list_to_list(node: Optional[ListNode]) -> list[int]:
    """Convert a linked list to a Python list."""
    result = []
    while node:
        result.append(node.val)
        node = node.next
    return result
