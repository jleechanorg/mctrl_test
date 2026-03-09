"""
Merge K Sorted Lists - LeetCode #23 (Hard)

Problem:
You are given an array of k linked-lists lists, each linked-list is sorted in ascending order.
Merge all the linked-lists into one sorted linked-list and return it.

Example 1:
Input: lists = [[1,4,5],[1,3,4],[2,6]]
Output: [1,1,2,3,4,4,5,6]
Explanation: The linked-lists are:
[
  1->4->5,
  1->3->4,
  2->6
]
merging them into one sorted list: 1->1->2->3->4->4->5->6

Example 2:
Input: lists = []
Output: []

Example 3:
Input: lists = [[]]
Output: []

Constraints:
- k == lists.length
- 0 <= k <= 10^4
- 0 <= lists[i].length <= 500
- -10^4 <= lists[i][j] <= 10^4
- lists[i] is sorted in ascending order.
- The sum of lists[i].length will not exceed 10^4.
"""
from __future__ import annotations

from dataclasses import dataclass
from heapq import heappush, heappop
from typing import Optional


@dataclass
class ListNode:
    """Definition for singly-linked list node."""
    val: int
    next: Optional['ListNode'] = None


def merge_k_sorted_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists into one sorted linked list.

    Uses a min-heap to always extract the smallest element among all lists.
    Time: O(N log k) where N is total elements, k is number of lists
    Space: O(k) for the heap

    Args:
        lists: List of sorted linked list heads (can be None)

    Returns:
        Head of the merged sorted linked list
    """
    # Dummy node to simplify head handling
    dummy = ListNode(0)
    current = dummy

    # Min-heap: (value, list_index, node)
    # We include list_index to handle duplicate values correctly
    heap = []

    # Initialize heap with first node from each non-empty list
    for i, head in enumerate(lists):
        if head is not None:
            heappush(heap, (head.val, i, head))

    # Process all nodes
    while heap:
        val, i, node = heappop(heap)
        current.next = node
        current = current.next

        # Add next node from the same list if available
        if node.next is not None:
            heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_sorted_lists_divide_conquer(
    lists: list[Optional[ListNode]]
) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer.

    Recursively pairs and merges lists until one remains.
    Time: O(N log k)
    Space: O(log k) for recursion stack

    Args:
        lists: List of sorted linked list heads

    Returns:
        Head of the merged sorted linked list
    """
    if not lists:
        return None

    # Base case: single list
    if len(lists) == 1:
        return lists[0]

    # Divide: pair up lists and merge each pair
    mid = len(lists) // 2
    left = merge_k_sorted_lists_divide_conquer(lists[:mid])
    right = merge_k_sorted_lists_divide_conquer(lists[mid:])

    # Conquer: merge two sorted lists
    return _merge_two_lists(left, right)


def _merge_two_lists(
    l1: Optional[ListNode],
    l2: Optional[ListNode]
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

    # Attach remaining nodes
    current.next = l1 or l2
    return dummy.next


# Helper functions for testing
def create_linked_list(values: list[int]) -> Optional[ListNode]:
    """Create a linked list from a list of values."""
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
