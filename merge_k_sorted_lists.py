"""
Merge k Sorted Lists - LeetCode Hard Problem

You are given an array of k linked-lists, each linked-list is sorted in ascending order.
Merge all the linked-lists into one sorted linked-list and return it.

Approach: Use a min-heap to always get the smallest element among all lists.
- Time Complexity: O(N log k) where N is total nodes, k is number of lists
- Space Complexity: O(k) for the heap

Alternative: Divide and Conquer - O(N log k) time, O(1) space
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
        """For heap comparison."""
        return self.val < other.val


def merge_k_lists_heap(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using a min-heap.

    Args:
        lists: List of sorted linked list heads (may be None)

    Returns:
        Head of the merged sorted linked list
    """
    # Initialize min-heap with first node from each non-empty list
    heap = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    # Dummy head for result
    dummy = ListNode(0)
    current = dummy

    # Extract min, add next node from same list
    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_lists_divide_conquer(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer.

    Args:
        lists: List of sorted linked list heads (may be None)

    Returns:
        Head of the merged sorted linked list
    """
    if not lists:
        return None

    # Repeatedly merge pairs until one list remains
    while len(lists) > 1:
        new_lists = []
        for i in range(0, len(lists), 2):
            l1 = lists[i]
            l2 = lists[i + 1] if i + 1 < len(lists) else None
            new_lists.append(_merge_two_lists(l1, l2))
        lists = new_lists

    return lists[0] if lists else None


def _merge_two_lists(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
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


if __name__ == "__main__":
    # Example usage
    lists = [
        list_to_linkedlist([1, 4, 5]),
        list_to_linkedlist([1, 3, 4]),
        list_to_linkedlist([2, 6])
    ]

    result = merge_k_lists_heap(lists)
    print("Heap result:", linkedlist_to_list(result))

    lists = [
        list_to_linkedlist([1, 4, 5]),
        list_to_linkedlist([1, 3, 4]),
        list_to_linkedlist([2, 6])
    ]
    result = merge_k_lists_divide_conquer(lists)
    print("Divide-Conquer result:", linkedlist_to_list(result))
