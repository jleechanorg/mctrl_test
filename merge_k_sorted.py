"""
Merge k Sorted Lists - LeetCode Hard Problem

You are given an array of k linked-lists lists, each linked-list is sorted in ascending order.
Merge all the linked-lists into one sorted linked-list and return it.

Approach: Use a min-heap (priority queue) to efficiently get the smallest element across all lists.
Time Complexity: O(N log k) where N is total number of nodes, k is number of lists
Space Complexity: O(k) for the heap
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
        """Enable comparison for heapq."""
        return self.val < other.val


def merge_k_sorted_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists into one sorted linked list.

    Args:
        lists: List of sorted linked list heads (can be None)

    Returns:
        Head of merged sorted linked list

    Example:
        >>> lists = [ListNode(1, ListNode(4, ListNode(5))),
        ...          ListNode(1, ListNode(3, ListNode(4))),
        ...          ListNode(2, ListNode(6))]
        >>> head = merge_k_sorted_lists(lists)
        >>> # Returns: 1 -> 1 -> 2 -> 3 -> 4 -> 4 -> 5 -> 6
    """
    # Initialize min-heap with first node from each non-empty list
    heap: list[ListNode] = []

    for i, head in enumerate(lists):
        if head is not None:
            # Store (value, index, node) - index breaks ties deterministically
            heapq.heappush(heap, (head.val, i, head))

    # Dummy head for result list
    dummy = ListNode(-1)
    current = dummy

    # Extract min, add to result, push next node from same list
    while heap:
        val, idx, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        if node.next is not None:
            heapq.heappush(heap, (node.next.val, idx, node.next))

    return dummy.next


def merge_k_sorted_lists_divide_conquer(
    lists: list[Optional[ListNode]],
) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer approach.

    Repeatedly merge pairs of lists until one remains.
    Time Complexity: O(N log k)
    Space Complexity: O(log k) for recursion stack (excluding output)
    """
    if not lists:
        return None

    def merge_two(a: Optional[ListNode], b: Optional[ListNode]) -> Optional[ListNode]:
        """Merge two sorted linked lists."""
        dummy = ListNode(-1)
        current = dummy

        while a and b:
            if a.val <= b.val:
                current.next = a
                a = a.next
            else:
                current.next = b
                b = b.next
            current = current.next

        current.next = a or b
        return dummy.next

    # Handle edge case: empty lists in input
    non_empty = [lst for lst in lists if lst is not None]
    if not non_empty:
        return None

    # Repeatedly merge pairs until one list remains
    while len(non_empty) > 1:
        new_lists = []
        for i in range(0, len(non_empty), 2):
            l1 = non_empty[i]
            l2 = non_empty[i + 1] if i + 1 < len(non_empty) else None
            new_lists.append(merge_two(l1, l2))
        non_empty = new_lists

    return non_empty[0]


# Array-based implementation for testing
def merge_k_sorted_arrays(arrays: list[list[int]]) -> list[int]:
    """
    Merge k sorted arrays into one sorted array.

    Args:
        arrays: List of sorted arrays

    Returns:
        Merged sorted array
    """
    result = []
    heap: list[tuple[int, int, int]] = []  # (value, array_index, element_index)

    for i, arr in enumerate(arrays):
        if arr:
            heapq.heappush(heap, (arr[0], i, 0))

    while heap:
        val, arr_idx, elem_idx = heapq.heappop(heap)
        result.append(val)

        if elem_idx + 1 < len(arrays[arr_idx]):
            heapq.heappush(heap, (arrays[arr_idx][elem_idx + 1], arr_idx, elem_idx + 1))

    return result
