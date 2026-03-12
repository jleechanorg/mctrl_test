"""
Merge k Sorted Lists - LeetCode Hard Problem

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
from typing import Optional, List
import heapq


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

    def __lt__(self, other: 'ListNode') -> bool:
        """Enable comparison for heapq."""
        return self.val < other.val


def merge_k_lists_heap(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted lists using a min-heap.

    Time Complexity: O(N log k) where N is total number of nodes,
                     k is number of lists
    Space Complexity: O(k) for the heap

    Args:
        lists: List of sorted linked lists

    Returns:
        Head of the merged sorted linked list
    """
    # Create a min-heap with (value, list_index, node)
    # We use list_index to break ties and avoid comparison issues
    heap = []

    # Initialize heap with first node from each list
    for i, head in enumerate(lists):
        if head:
            heapq.heappush(heap, (head.val, i, head))

    # Dummy head for result list
    dummy = ListNode(0)
    current = dummy

    # Extract minimum and add next node from same list
    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        # Add next node from the same list
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_lists_divide_conquer(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted lists using divide and conquer.

    Time Complexity: O(N log k)
    Space Complexity: O(log k) for recursion stack

    Args:
        lists: List of sorted linked lists

    Returns:
        Head of the merged sorted linked list
    """
    if not lists:
        return None

    def merge_two(a: Optional[ListNode], b: Optional[ListNode]) -> Optional[ListNode]:
        """Merge two sorted linked lists."""
        dummy = ListNode(0)
        current = dummy

        while a and b:
            if a.val <= b.val:
                current.next = a
                a = a.next
            else:
                current.next = b
                b = b.next
            current = current.next

        current.next = a if a else b

        return dummy.next

    # Repeatedly merge pairs of lists
    while len(lists) > 1:
        new_lists = []

        for i in range(0, len(lists), 2):
            if i + 1 < len(lists):
                new_lists.append(merge_two(lists[i], lists[i + 1]))
            else:
                new_lists.append(lists[i])

        lists = new_lists

    return lists[0] if lists else None


# Wrapper function using heap approach (preferred)
def merge_k_lists(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists into one sorted linked list.

    Uses min-heap approach for optimal time complexity.

    Time Complexity: O(N log k)
    Space Complexity: O(k)

    Args:
        lists: List of k sorted linked-lists (may be empty or contain None)

    Returns:
        The head of the merged sorted linked-list
    """
    return merge_k_lists_heap(lists)


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


def linkedlist_to_list(node: Optional[ListNode]) -> List[int]:
    """Convert a linked list to a Python list."""
    result = []
    while node:
        result.append(node.val)
        node = node.next
    return result
