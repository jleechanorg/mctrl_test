"""
Merge k Sorted Lists - LeetCode Hard

You are given an array of k linked-lists lists, each linked-list is sorted in ascending order.
Merge all the linked-lists into one sorted linked-list and return it.

Approach: Divide and Conquer
- Recursively divide the list of lists in half until we have single lists
- Merge two sorted lists using a simple O(n) merge
- Time Complexity: O(N log k) where N is total nodes, k is number of lists
- Space Complexity: O(log k) for recursion stack (excluding output)

Alternative approaches:
1. Merge one by one: O(N*k) time
2. Heap/Priority Queue: O(N log k) time, O(k) space
"""

from __future__ import annotations
from typing import Optional
from dataclasses import dataclass


@dataclass
class ListNode:
    """Definition for singly-linked list node."""
    val: int
    next: Optional['ListNode'] = None


def merge_two_lists(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    """Merge two sorted linked lists into one sorted list.

    Args:
        l1: Head of first sorted linked list
        l2: Head of second sorted linked list

    Returns:
        Head of merged sorted linked list

    Time Complexity: O(n + m) where n, m are lengths of the two lists
    Space Complexity: O(1) excluding the output list
    """
    dummy = ListNode(-1)
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
    current.next = l1 if l1 else l2

    return dummy.next


def merge_k_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """Merge k sorted linked lists using divide and conquer.

    Args:
        lists: List of heads of k sorted linked lists

    Returns:
        Head of merged sorted linked list

    Time Complexity: O(N log k) where N is total number of nodes, k is number of lists
    Space Complexity: O(log k) for recursion stack
    """
    if not lists:
        return None

    if len(lists) == 1:
        return lists[0]

    mid = len(lists) // 2
    left = merge_k_lists(lists[:mid])
    right = merge_k_lists(lists[mid:])

    return merge_two_lists(left, right)


# Helper functions for testing
def create_linked_list(values: list[int]) -> Optional[ListNode]:
    """Create a linked list from a list of values."""
    if not values:
        return None

    dummy = ListNode(-1)
    current = dummy
    for val in values:
        current.next = ListNode(val)
        current = current.next

    return dummy.next


def linked_list_to_list(node: Optional[ListNode]) -> list[int]:
    """Convert a linked list to a Python list for easy comparison."""
    result = []
    while node:
        result.append(node.val)
        node = node.next
    return result
