"""
Merge k Sorted Lists

You are given an array of k linked-lists, each linked-list is sorted in ascending order.
Merge all the linked-lists into one sorted linked-list and return it.

This module provides two solutions:
1. Heap-based approach: O(N log k) time, O(k) space
2. Divide and conquer: O(N log k) time, O(1) space

Example:
    Input: lists = [[1,4,5],[1,3,4],[2,6]]
    Output: [1,1,2,3,4,4,5,6]
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
import heapq


@dataclass
class ListNode:
    """Definition for singly-linked list node."""
    val: int
    next: Optional[ListNode] = None


def merge_k_lists_heap(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using a min-heap.

    Time Complexity: O(N log k) where N is total nodes, k is number of lists
    Space Complexity: O(k) for the heap

    Args:
        lists: List of sorted linked lists

    Returns:
        The head of the merged sorted linked list
    """
    # Dummy node to simplify head handling
    dummy = ListNode(0)
    current = dummy

    # Initialize heap with (value, list_index, node)
    # list_index breaks ties when values are equal
    heap = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    # Extract min, add to result, push next node from same list
    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_lists_divide_conquer(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer.

    Time Complexity: O(N log k)
    Space Complexity: O(1) excluding recursion stack

    Args:
        lists: List of sorted linked lists

    Returns:
        The head of the merged sorted linked list
    """
    if not lists:
        return None
    if len(lists) == 1:
        return lists[0]

    def merge_two(a: Optional[ListNode], b: Optional[ListNode]) -> Optional[ListNode]:
        """Merge two sorted linked lists."""
        if not a:
            return b
        if not b:
            return a

        if a.val <= b.val:
            a.next = merge_two(a.next, b)
            return a
        else:
            b.next = merge_two(a, b.next)
            return b

    # Divide and conquer: merge pairs iteratively
    # Standard approach: merge adjacent pairs, then pairs of pairs, etc.
    if not lists:
        return None

    while len(lists) > 1:
        new_lists = []

        # Merge pairs of lists
        for i in range(0, len(lists) - 1, 2):
            merged = merge_two(lists[i], lists[i + 1])
            new_lists.append(merged)

        # If odd number of lists, append the last one
        if len(lists) % 2 == 1:
            new_lists.append(lists[-1])

        lists = new_lists

    return lists[0]


# Utility functions for testing
def create_linked_list(values: List[int]) -> Optional[ListNode]:
    """Create a linked list from a list of values."""
    if not values:
        return None
    dummy = ListNode(0)
    current = dummy
    for val in values:
        current.next = ListNode(val)
        current = current.next
    return dummy.next


def linked_list_to_list(node: Optional[ListNode]) -> List[int]:
    """Convert a linked list to a Python list."""
    result = []
    while node:
        result.append(node.val)
        node = node.next
    return result
