"""
LeetCode 23 - Merge k Sorted Lists

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


# Definition for singly-linked list node
class ListNode:
    """Definition for a node in a singly-linked list."""

    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

    def __repr__(self) -> str:
        return f"ListNode({self.val})"

    def __lt__(self, other: 'ListNode') -> bool:
        """Enable comparison for heapq."""
        return self.val < other.val


def merge_k_lists_heap(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using a min-heap.

    Time Complexity: O(N log k) where N is total nodes, k is number of lists
    Space Complexity: O(k) for the heap

    Args:
        lists: List of sorted linked list heads

    Returns:
        Head of the merged sorted linked list
    """
    # Dummy head for easier manipulation
    dummy = ListNode(-1)
    current = dummy

    # Initialize heap with first node from each list
    # heap elements are (value, list_index, node) to handle duplicates
    heap = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    # Extract min, add to result, push next from same list
    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_lists_divide_conquer(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer.

    Time Complexity: O(N log k) - each level processes all N nodes, log k levels
    Space Complexity: O(log k) for recursion stack (or O(1) if done iteratively)

    Args:
        lists: List of sorted linked list heads

    Returns:
        Head of the merged sorted linked list
    """
    if not lists:
        return None
    if len(lists) == 1:
        return lists[0]

    # Merge pairs iteratively
    while len(lists) > 1:
        new_lists = []

        for i in range(0, len(lists), 2):
            if i + 1 < len(lists):
                merged = merge_two_lists(lists[i], lists[i + 1])
                new_lists.append(merged)
            else:
                new_lists.append(lists[i])

        lists = new_lists

    return lists[0]


def merge_two_lists(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    """
    Merge two sorted linked lists into one sorted list.

    Time Complexity: O(n + m) where n, m are lengths of the two lists
    Space Complexity: O(1)

    Args:
        l1: Head of first sorted linked list
        l2: Head of second sorted linked list

    Returns:
        Head of the merged sorted linked list
    """
    dummy = ListNode(-1)
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


# Helper functions for testing
def list_to_linkedlist(values: List[int]) -> Optional[ListNode]:
    """Convert a Python list to a linked list."""
    if not values:
        return None

    dummy = ListNode(-1)
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


# Public API matching LeetCode signature
class Solution:
    """
    Solution class for LeetCode 23 - Merge k Sorted Lists.

    Provides multiple approaches:
    - mergeKLists: Uses heap-based approach (default)
    """

    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
        """
        Merge k sorted linked lists into one sorted linked list.

        Uses a min-heap approach for O(N log k) time complexity.

        Args:
            lists: List of sorted linked list heads

        Returns:
            Head of the merged sorted linked list
        """
        return merge_k_lists_heap(lists)
