"""
Merge k Sorted Lists - LeetCode #23 (Hard)

You are given an array of k linked-lists, each linked-list is sorted in ascending order.
Merge all the linked-lists into one sorted linked-list and return it.

Approach: Use a min-heap to efficiently find the smallest element among k lists.
Time Complexity: O(N log k) where N is total number of nodes
Space Complexity: O(k) for the heap
"""
from __future__ import annotations

import heapq
from typing import Optional


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional[ListNode] = None):
        self.val = val
        self.next = next

    def __lt__(self, other: "ListNode") -> bool:
        """Enable comparison for heapq."""
        return self.val < other.val


def merge_k_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists into one sorted linked list.

    Args:
        lists: List of k sorted linked lists

    Returns:
        Head of the merged sorted linked list

    Example:
        >>> list1 = ListNode(1, ListNode(4, ListNode(5)))
        >>> list2 = ListNode(1, ListNode(3, ListNode(4)))
        >>> list3 = ListNode(2, ListNode(6))
        >>> merged = merge_k_lists([list1, list2, list3])
        >>> # Result: 1->1->2->3->4->4->5->6
    """
    # Initialize min-heap with first node from each non-empty list
    heap: list[ListNode] = []
    for lst in lists:
        if lst:
            heapq.heappush(heap, lst)

    # Dummy head to simplify edge cases
    dummy = ListNode(0)
    current = dummy

    # Extract minimum, add next node from same list
    while heap:
        node = heapq.heappop(heap)
        current.next = node
        current = current.next
        if node.next:
            heapq.heappush(heap, node.next)

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


def linkedlist_to_list(head: Optional[ListNode]) -> list[int]:
    """Convert a linked list to a Python list."""
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result


if __name__ == "__main__":
    # Example usage
    list1 = list_to_linkedlist([1, 4, 5])
    list2 = list_to_linkedlist([1, 3, 4])
    list3 = list_to_linkedlist([2, 6])

    merged = merge_k_lists([list1, list2, list3])
    print(linkedlist_to_list(merged))  # [1, 1, 2, 3, 4, 4, 5, 6]
