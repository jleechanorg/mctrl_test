"""
Merge k Sorted Lists - LeetCode Hard

You are given an array of k linked-lists lists, each linked-list is sorted in ascending order.
Merge all the linked-lists into one sorted linked-list and return it.

Example 1:
Input: lists = [[1,4,5],[1,3,4],[2,6]]
Output: [1,1,2,3,4,4,5,6]
Explanation: The linked-lists are:
[
  1->4->5,
  1->3->4,
  2->6
]
merging them into one sorted list: 1->1->2->3->4->4->5->6

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


def merge_k_sorted_lists(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using a min-heap.

    Time Complexity: O(N log k) where N is total nodes, k is number of lists
    Space Complexity: O(k) for the heap + O(1) for result (excluding output)

    Approach:
    - Use a min-heap to always get the smallest element among all list heads
    - Push (value, list_index, node) tuples to handle duplicates
    - Extract min, add to result, push next node from that list
    """
    # Dummy head for simplified edge handling
    dummy = ListNode(0)
    current = dummy
    heap = []

    # Initialize heap with first node from each non-empty list
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    # Process nodes from heap
    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = ListNode(val)
        current = current.next

        # Add next node from same list to heap
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_sorted_lists_divide_conquer(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer (pairwise merging).

    Time Complexity: O(N log k)
    Space Complexity: O(log k) for recursion stack

    Approach:
    - Pair up lists and merge them recursively
    - Base case: return single list or None
    - Merge two sorted lists repeatedly until one remains
    """
    if not lists:
        return None
    if len(lists) == 1:
        return lists[0]

    # Divide
    mid = len(lists) // 2
    left = merge_k_sorted_lists_divide_conquer(lists[:mid])
    right = merge_k_sorted_lists_divide_conquer(lists[mid:])

    # Conquer: merge two sorted lists
    return _merge_two_lists(left, right)


def _merge_two_lists(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    """Helper: merge two sorted linked lists."""
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


# Convenience functions for testing with lists
def list_to_linkedlist(arr: List[int]) -> Optional[ListNode]:
    """Convert Python list to linked list."""
    if not arr:
        return None
    dummy = ListNode(0)
    current = dummy
    for val in arr:
        current.next = ListNode(val)
        current = current.next
    return dummy.next


def linkedlist_to_list(node: Optional[ListNode]) -> List[int]:
    """Convert linked list to Python list."""
    result = []
    while node:
        result.append(node.val)
        node = node.next
    return result
