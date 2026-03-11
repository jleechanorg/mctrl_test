"""
LeetCode 23 - Merge k Sorted Lists

You are given an array of k linked-lists lists, each linked-list is sorted in ascending order.
Merge all the linked-lists into one sorted linked-list and return it.

https://leetcode.com/problems/merge-k-sorted-lists/
"""

from __future__ import annotations
from typing import Optional
import heapq


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

    def __lt__(self, other: 'ListNode') -> bool:
        return self.val < other.val


def merge_k_sorted_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists into one sorted linked list.

    Uses a min-heap to efficiently select the smallest element across all lists.

    Args:
        lists: List of sorted linked list heads (may be None)

    Returns:
        Head of the merged sorted linked list

    Time Complexity: O(N log k) where N is total nodes, k is number of lists
    Space Complexity: O(k) for the heap
    """
    # Dummy node to simplify edge cases
    dummy = ListNode()
    current = dummy

    # Initialize heap with first node from each non-empty list
    heap = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    # Process nodes in order
    while heap:
        val, _, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        if node.next:
            heapq.heappush(heap, (node.next.val, id(node.next), node.next))

    return dummy.next


def merge_k_sorted_lists_divide_conquer(
    lists: list[Optional[ListNode]]
) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer approach.

    Repeatedly merges pairs of lists until one remains.

    Args:
        lists: List of sorted linked list heads (may be None)

    Returns:
        Head of the merged sorted linked list

    Time Complexity: O(N log k)
    Space Complexity: O(1) excluding recursion stack
    """
    if not lists:
        return None
    if len(lists) == 1:
        return lists[0]

    # Merge pairs iteratively
    while len(lists) > 1:
        new_lists = []
        for i in range(0, len(lists) - 1, 2):
            merged = merge_two_lists(lists[i], lists[i + 1])
            new_lists.append(merged)
        # Handle odd case
        if len(lists) % 2 == 1:
            new_lists.append(lists[-1])
        lists = new_lists

    return lists[0]


def merge_two_lists(
    l1: Optional[ListNode], l2: Optional[ListNode]
) -> Optional[ListNode]:
    """Merge two sorted linked lists."""
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

    current.next = l1 or l2
    return dummy.next


def list_to_linkedlist(arr: list[int]) -> Optional[ListNode]:
    """Convert list to linked list."""
    if not arr:
        return None
    dummy = ListNode()
    current = dummy
    for val in arr:
        current.next = ListNode(val)
        current = current.next
    return dummy.next


def linkedlist_to_list(node: Optional[ListNode]) -> list[int]:
    """Convert linked list to list."""
    result = []
    while node:
        result.append(node.val)
        node = node.next
    return result


if __name__ == "__main__":
    # Example usage
    lists = [
        list_to_linkedlist([1, 4, 5]),
        list_to_linkedlist([1, 3, 4]),
        list_to_linkedlist([2, 6]),
    ]
    result = merge_k_sorted_lists(lists)
    print(linkedlist_to_list(result))  # [1, 1, 2, 3, 4, 4, 5, 6]
