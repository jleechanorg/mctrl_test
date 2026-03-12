"""
Merge k Sorted Lists - LeetCode Hard

You are given an array of k linked-lists, each linked-list is sorted in ascending order.
Merge all the linked-lists into one sorted linked-list and return it.

Example 1:
    Input: lists = [[1,4,5],[1,3,4],[2,6]]
    Output: [1,1,2,3,4,4,5,6]

Example 2:
    Input: lists = []
    Output: []

Example 3:
    Input: lists = [[]]
    Output: []

Constraints:
    k == lists.length
    0 <= k <= 10^4
    0 <= lists[i].length <= 500
    -10^4 <= lists[i][j] <= 10^4
    lists[i] is sorted in ascending order.
    The sum of lists[i].length will not exceed 10^4.
"""
from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Optional


@dataclass
class ListNode:
    """Definition for singly-linked list node."""
    val: int = 0
    next: Optional['ListNode'] = None


def merge_k_lists_heap(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using a min-heap.

    Time Complexity: O(N log k) where N is total nodes, k is number of lists
    Space Complexity: O(k) for the heap

    Args:
        lists: List of sorted linked list heads

    Returns:
        Head of the merged sorted linked list
    """
    # Min-heap stores (value, list_index, node) tuples
    # list_index ensures nodes with same value are distinguishable
    heap: list[tuple[int, int, ListNode]] = []

    # Initialize heap with first node from each non-empty list
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    # Dummy head for result list
    dummy = ListNode(0)
    current = dummy

    # Extract minimum, add to result, push next node from same list
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

    Time Complexity: O(N log k)
    Space Complexity: O(log k) for recursion stack

    Args:
        lists: List of sorted linked list heads

    Returns:
        Head of the merged sorted linked list
    """
    if not lists:
        return None

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

    # Base case: single list
    if len(lists) == 1:
        return lists[0]

    # Divide
    mid = len(lists) // 2
    left = merge_k_lists_divide_conquer(lists[:mid])
    right = merge_k_lists_divide_conquer(lists[mid:])

    # Conquer: merge two halves
    return merge_two(left, right)


# Alias for primary solution
merge_k_lists = merge_k_lists_divide_conquer


# ============ Helper Functions for Testing ============

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
    # Example 1
    lists = [
        list_to_linkedlist([1, 4, 5]),
        list_to_linkedlist([1, 3, 4]),
        list_to_linkedlist([2, 6])
    ]
    result = merge_k_lists(lists)
    print(linkedlist_to_list(result))  # [1, 1, 2, 3, 4, 4, 5, 6]

    # Example 2
    lists = []
    result = merge_k_lists(lists)
    print(linkedlist_to_list(result))  # []

    # Example 3
    lists = [None]
    result = merge_k_lists(lists)
    print(linkedlist_to_list(result))  # []
