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
from typing import List, Optional
import heapq


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next


def merge_k_lists_heap(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using a min-heap.

    Time Complexity: O(N log k) where N is total number of nodes
                     - Each node is processed once and each push/pop on heap is O(log k)
    Space Complexity: O(k) for the heap + O(1) for the result list (excluding output)

    Args:
        lists: List of sorted linked lists

    Returns:
        The merged sorted linked list
    """
    # Min-heap stores (value, list_index, node) tuples
    # list_index is used to break ties when values are equal
    heap = []

    # Initialize heap with first node from each non-empty list
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    # Dummy head to simplify edge cases
    dummy = ListNode(0)
    current = dummy

    # Extract min and add next node from same list
    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        # Add next node from this list to heap
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_lists_divide_conquer(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer (pairwise merging).

    Time Complexity: O(N log k)
                     - Each level processes all N nodes, and there are log k levels
    Space Complexity: O(1) extra space (excluding recursion stack)

    Args:
        lists: List of sorted linked lists

    Returns:
        The merged sorted linked list
    """
    if not lists:
        return None

    while len(lists) > 1:
        merged_lists = []

        # Pair up lists and merge each pair
        for i in range(0, len(lists), 2):
            l1 = lists[i]
            l2 = lists[i + 1] if i + 1 < len(lists) else None
            merged_lists.append(merge_two_lists(l1, l2))

        lists = merged_lists

    return lists[0] if lists else None


def merge_two_lists(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    """
    Merge two sorted linked lists into one sorted list.

    Time Complexity: O(n + m) where n, m are lengths of the two lists
    Space Complexity: O(1)

    Args:
        l1: First sorted linked list
        l2: Second sorted linked list

    Returns:
        Merged sorted linked list
    """
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


# ListNode helper functions for testing
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
