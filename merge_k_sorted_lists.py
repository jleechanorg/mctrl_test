"""
Merge k Sorted Lists - LeetCode #23 (Hard)

This module implements an efficient solution to merge k sorted linked lists
into one sorted linked list.

Approach: Min-Heap Based Merge
- Use a min-heap to always get the smallest element among all list heads
- Time: O(N log k) where N is total nodes, k is number of lists
- Space: O(k) for the heap

Alternative Approaches:
1. Brute Force: Collect all values, sort, rebuild - O(N log N)
2. Merge One by One: Merge lists pairwise - O(N log k)
3. Divide and Conquer: Recursively merge halves - O(N log k)
"""

from __future__ import annotations
import heapq
from typing import Optional


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

    def __repr__(self) -> str:
        return f"ListNode({self.val})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ListNode):
            return NotImplemented
        return self.val == other.val

    def __lt__(self, other: 'ListNode') -> bool:
        """For heap comparison - compare by value."""
        return self.val < other.val


def merge_k_sorted_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists into one sorted linked list.

    Args:
        lists: List of heads of k sorted linked lists (can be None)

    Returns:
        Head of the merged sorted linked list

    Example:
        >>> list1 = ListNode(1, ListNode(4, ListNode(5)))
        >>> list2 = ListNode(1, ListNode(3, ListNode(4)))
        >>> list3 = ListNode(2, ListNode(6))
        >>> merged = merge_k_sorted_lists([list1, list2, list3])
        >>> # Result: 1 -> 1 -> 2 -> 3 -> 4 -> 4 -> 5 -> 6
    """
    # Dummy head to simplify edge cases
    dummy = ListNode(-1)
    current = dummy

    # Min-heap: (value, list_index, node)
    # list_index ensures stable ordering when values are equal
    heap: list[tuple[int, int, ListNode]] = []

    # Initialize heap with the first node from each non-empty list
    for i, head in enumerate(lists):
        if head is not None:
            # Push (value, list_index, node) - tuple comparison is lexicographic
            heapq.heappush(heap, (head.val, i, head))

    # Extract minimum, add to result, push next from same list
    while heap:
        val, list_idx, node = heapq.heappop(heap)

        # Add to merged list
        current.next = node
        current = current.next

        # Push next node from same list if exists
        if node.next is not None:
            heapq.heappush(heap, (node.next.val, list_idx, node.next))

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
    # Example test
    list1 = list_to_linkedlist([1, 4, 5])
    list2 = list_to_linkedlist([1, 3, 4])
    list3 = list_to_linkedlist([2, 6])

    merged = merge_k_sorted_lists([list1, list2, list3])
    print("Merged:", linkedlist_to_list(merged))
