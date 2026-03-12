"""
Merge k Sorted Lists - LeetCode Hard

You are given an array of k linked-lists lists, each linked-list is sorted in ascending order.
Merge all the linked-lists into one sorted linked-list and return it.

Approach: Divide and Conquer
- Recursively divide the list of lists in half until we have single lists
- Merge two sorted lists using a standard merge algorithm
- Time: O(N log k) where N is total number of nodes, k is number of lists
- Space: O(log k) for recursion stack (excluding output)
"""
from __future__ import annotations
from typing import Optional
import heapq


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next


def merge_k_lists_divide_conquer(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer.

    Args:
        lists: List of sorted linked list heads

    Returns:
        Head of merged sorted linked list

    Time Complexity: O(N log k)
    Space Complexity: O(log k) for recursion stack
    """
    if not lists:
        return None
    if len(lists) == 1:
        return lists[0]

    # Recursively divide and merge
    mid = len(lists) // 2
    left = merge_k_lists_divide_conquer(lists[:mid])
    right = merge_k_lists_divide_conquer(lists[mid:])
    return merge_two_lists(left, right)


def merge_two_lists(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    """
    Merge two sorted linked lists into one sorted list.

    Time Complexity: O(n + m) where n, m are lengths of the two lists
    Space Complexity: O(1) excluding output
    """
    dummy = ListNode()
    current = dummy

    while l1 and l2:
        if l1.val <= l2.val:
            current.next = l1
            l1 = l1.next
        else:
            current.next = l2
            l2 = l2.next
        current = current.next

    # Attach remaining nodes
    current.next = l1 or l2
    return dummy.next


def merge_k_lists_heap(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using a min heap.

    Args:
        lists: List of sorted linked list heads

    Returns:
        Head of merged sorted linked list

    Time Complexity: O(N log k)
    Space Complexity: O(k) for heap
    """
    if not lists:
        return None

    # Initialize heap with first node from each list
    heap = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    dummy = ListNode()
    current = dummy

    while heap:
        val, idx, node = heapq.heappop(heap)
        current.next = node
        current = current.next
        if node.next:
            heapq.heappush(heap, (node.next.val, idx, node.next))

    return dummy.next


def list_to_linkedlist(values: list[int]) -> Optional[ListNode]:
    """Convert a Python list to a linked list."""
    if not values:
        return None
    dummy = ListNode()
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
