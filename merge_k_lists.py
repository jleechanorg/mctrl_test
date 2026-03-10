"""
Merge k Sorted Lists - LeetCode Hard Problem

You are given an array of k linked-lists, each linked-list is sorted in ascending order.
Merge all the linked-lists into one sorted linked-list and return it.

Approach: Use a min-heap (priority queue) to efficiently find the smallest element
across all k lists at each step.

Time Complexity: O(N log k) where N is total number of nodes, k is number of lists
Space Complexity: O(k) for the heap + O(k) for the dummy node
"""
from __future__ import annotations

from typing import Optional
import heapq


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

    def __repr__(self) -> str:
        return f"ListNode({self.val})"

    def __lt__(self, other: 'ListNode') -> bool:
        """Required for heap comparison - compare by value."""
        return self.val < other.val


def merge_k_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists into one sorted linked list.

    Args:
        lists: List of k sorted linked lists (can contain None values)

    Returns:
        The head of the merged sorted linked list

    Example:
        >>> list1 = ListNode(1, ListNode(4, ListNode(5)))
        >>> list2 = ListNode(1, ListNode(3, ListNode(4)))
        >>> list3 = ListNode(2, ListNode(6))
        >>> result = merge_k_lists([list1, list2, list3])
        >>> # Result: 1 -> 1 -> 2 -> 3 -> 4 -> 4 -> 5 -> 6
    """
    # Min-heap to store (value, list_index, node)
    # list_index is used as tiebreaker when values are equal
    min_heap: list[tuple[int, int, ListNode]] = []

    # Initialize heap with first node from each non-empty list
    for i, head in enumerate(lists):
        if head:
            heapq.heappush(min_heap, (head.val, i, head))

    # Dummy node to simplify list construction
    dummy = ListNode(0)
    current = dummy

    # Extract min and add next node from same list
    while min_heap:
        val, list_idx, node = heapq.heappop(min_heap)
        current.next = node
        current = current.next

        # Add next node from this list to heap
        if node.next:
            heapq.heappush(min_heap, (node.next.val, list_idx, node.next))

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
    # Test example from LeetCode
    list1 = list_to_linkedlist([1, 4, 5])
    list2 = list_to_linkedlist([1, 3, 4])
    list3 = list_to_linkedlist([2, 6])

    merged = merge_k_lists([list1, list2, list3])
    print("Merged list:", linkedlist_to_list(merged))
    # Expected: [1, 1, 2, 3, 4, 4, 5, 6]
