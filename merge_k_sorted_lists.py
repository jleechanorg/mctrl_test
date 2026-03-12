"""
Merge k Sorted Lists - LeetCode #23 (Hard)

You are given an array of k linked-lists, each linked-list is sorted in ascending order.
Merge all the linked-lists into one sorted linked-list and return it.

This module provides an optimized solution using a heap (priority queue).
"""

from __future__ import annotations
import heapq
from typing import Optional, List


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

    def __repr__(self) -> str:
        return f"ListNode({self.val})"

    def __lt__(self, other: 'ListNode') -> bool:
        """Enable heap comparison based on node values."""
        return self.val < other.val


def merge_k_lists(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists into one sorted linked list.

    Uses a min-heap to efficiently get the smallest element across all lists.
    Time Complexity: O(N log k) where N is total nodes, k is number of lists
    Space Complexity: O(k) for the heap + O(1) for result (excluding output)

    Args:
        lists: List of sorted linked list heads (can include None)

    Returns:
        Head of the merged sorted linked list
    """
    # Handle edge case: empty list of lists
    if not lists:
        return None

    # Initialize min-heap with first node from each non-empty list
    # Heap stores (value, list_index, node) tuples to handle duplicate values
    heap = []
    for i, head in enumerate(lists):
        if head:
            heapq.heappush(heap, (head.val, i, head))

    # Dummy head to simplify edge cases
    dummy = ListNode(0)
    current = dummy

    # Extract min, add to result, push next node from same list
    while heap:
        val, idx, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        # Push next node from this list if available
        if node.next:
            heapq.heappush(heap, (node.next.val, idx, node.next))

    return dummy.next


def merge_k_lists_divide_conquer(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Alternative solution using divide and conquer approach.

    Time Complexity: O(N log k) - each node is processed log k times
    Space Complexity: O(log k) for recursion stack

    Args:
        lists: List of sorted linked list heads

    Returns:
        Head of the merged sorted linked list
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

    mid = len(lists) // 2
    left = merge_k_lists_divide_conquer(lists[:mid])
    right = merge_k_lists_divide_conquer(lists[mid:])
    return merge_two(left, right)


# Helper functions for testing
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


if __name__ == "__main__":
    # Example usage
    list1 = list_to_linkedlist([1, 4, 7, 10])
    list2 = list_to_linkedlist([2, 5, 8, 11])
    list3 = list_to_linkedlist([3, 6, 9, 12])

    merged = merge_k_lists([list1, list2, list3])
    print("Merged list:", linkedlist_to_list(merged))
