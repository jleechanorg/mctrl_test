"""
Merge k Sorted Lists - LeetCode #23 (Hard)

You are given an array of k linked-lists, each linked-list is sorted in ascending order.
Merge all the linked-lists into one sorted linked-list and return it.

Approach:
---------
We use a min-heap (priority queue) to efficiently find the smallest element among
all k lists at each step. This gives us O(N log k) time complexity where N is
the total number of nodes and k is the number of lists.

Algorithm:
1. Initialize a min-heap with the first node from each list (if not empty)
2. Pop the smallest node from heap and add it to result
3. Push the next node from that list to the heap
4. Repeat until heap is empty

Time Complexity: O(N log k) - N total nodes, k lists
Space Complexity: O(k) for the heap + O(N) for the result list
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
        """Required for heap comparison."""
        return self.val < other.val


def merge_k_sorted_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists into one sorted linked list.

    Args:
        lists: List of k sorted linked lists

    Returns:
        The head of the merged sorted linked list
    """
    # Min-heap to store (value, list_index, node)
    # We include list_index to avoid comparison issues between nodes with same value
    heap: list[tuple[int, int, ListNode]] = []

    # Initialize heap with first node from each list
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    # Dummy node to simplify head handling
    dummy = ListNode(0)
    current = dummy

    # Process all nodes
    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        # Add next node from this list to heap
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


# --- Alternative approach using divide and conquer ---
def merge_two_lists(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
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

    current.next = l1 or l2
    return dummy.next


def merge_k_sorted_lists_divide_conquer(
    lists: list[Optional[ListNode]],
) -> Optional[ListNode]:
    """
    Merge k sorted lists using divide and conquer approach.

    Time Complexity: O(N log k)
    Space Complexity: O(log k) for recursion stack
    """
    if not lists:
        return None

    while len(lists) > 1:
        merged_lists = []
        for i in range(0, len(lists), 2):
            l1 = lists[i]
            l2 = lists[i + 1] if i + 1 < len(lists) else None
            merged_lists.append(merge_two_lists(l1, l2))
        lists = merged_lists

    return lists[0]


# --- Helper functions for testing ---


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
