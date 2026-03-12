"""
Merge k Sorted Lists (LeetCode #23)

You are given an array of k linked-lists lists, each linked-list is sorted in ascending order.
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
    - k == lists.length
    - 0 <= k <= 10^4
    - 0 <= lists[i].length <= 500
    - -10^4 <= lists[i][j] <= 10^4
    - lists[i] is sorted in ascending order.
    - The sum of lists[i].length will not exceed 10^4.
"""
from __future__ import annotations

import heapq
from typing import List, Optional


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional[ListNode] = None):
        self.val = val
        self.next = next

    def __lt__(self, other: "ListNode") -> bool:
        """Enable comparison for heapq."""
        return self.val < other.val


def merge_k_lists_heap(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
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
    # list_index breaks ties when values are equal
    heap: List[tuple] = []

    # Initialize heap with first node from each list
    for i, head in enumerate(lists):
        if head:
            heapq.heappush(heap, (head.val, i, head))

    dummy = ListNode(0)
    current = dummy

    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        # Push next node from same list
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_lists_divide_conquer(
    lists: List[Optional[ListNode]]
) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer (pairwise merging).

    Time Complexity: O(N log k) - each level processes all N nodes, log k levels
    Space Complexity: O(1) extra space (excluding recursion stack)

    Args:
        lists: List of sorted linked list heads

    Returns:
        Head of the merged sorted linked list
    """
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
        # Handle odd case - last list if odd number of lists
        if len(lists) % 2 == 1:
            new_lists.append(lists[-1])
        lists = new_lists

    return lists[0]


def merge_two_lists(
    l1: Optional[ListNode], l2: Optional[ListNode]
) -> Optional[ListNode]:
    """Merge two sorted linked lists into one sorted list."""
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


def list_to_linkedlist(values: List[int]) -> Optional[ListNode]:
    """Convert a Python list to a linked list."""
    if not values:
        return None

    dummy = ListNode(0)
    current = dummy
    for val in values:
        current.next = ListNode(val)
        current = current.next
    return dummy.next


def linkedlist_to_list(head: Optional[ListNode]) -> List[int]:
    """Convert a linked list to a Python list."""
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result
