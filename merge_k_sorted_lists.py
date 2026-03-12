"""
Merge k Sorted Lists - LeetCode Hard Problem

You are given an array of k linked-lists, each linked-list is sorted in ascending order.
Merge all the linked-lists into one sorted linked-list and return it.

Approach:
- Use a min-heap to always get the smallest element among all lists
- Time: O(N log k) where N is total nodes, k is number of lists
- Space: O(k) for the heap

Alternative divide-and-conquer approach:
- Time: O(N log k)
- Space: O(1) extra (excluding recursion stack)
"""
from __future__ import annotations

import heapq
from typing import Optional


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional[ListNode] = None):
        self.val = val
        self.next = next

    def __lt__(self, other: "ListNode") -> bool:
        """Enable comparison for heapq."""
        return self.val < other.val


def merge_k_sorted_lists_heap(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using a min-heap.

    Args:
        lists: List of sorted linked-list heads

    Returns:
        Head of the merged sorted linked list

    Time Complexity: O(N log k) where N = total nodes, k = number of lists
    Space Complexity: O(k) for the heap
    """
    # Dummy head to simplify edge cases
    dummy = ListNode(0)
    current = dummy

    # Heap stores (value, list_index, node) tuples
    # list_index breaks ties when values are equal
    heap: list[tuple[int, int, ListNode]] = []

    # Initialize heap with first node from each non-empty list
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    # Extract min, add to result, push next from same list
    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_sorted_lists_divide_conquer(
    lists: list[Optional[ListNode]],
) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer.

    Repeatedly pair up and merge adjacent lists until one remains.

    Args:
        lists: List of sorted linked-list heads

    Returns:
        Head of the merged sorted linked list

    Time Complexity: O(N log k)
    Space Complexity: O(1) extra (excluding recursion stack)
    """

    def merge_two_lists(
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

    if not lists:
        return None
    if len(lists) == 1:
        return lists[0]

    # Repeatedly merge pairs until one list remains
    while len(lists) > 1:
        new_lists = []
        for i in range(0, len(lists) - 1, 2):
            merged = merge_two_lists(lists[i], lists[i + 1])
            new_lists.append(merged)
        # If odd number of lists, add the last one
        if len(lists) % 2 == 1:
            new_lists.append(lists[-1])
        lists = new_lists

    return lists[0]


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


# Default export: heap-based solution (more intuitive)
merge_k_sorted_lists = merge_k_sorted_lists_heap
