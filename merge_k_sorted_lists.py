"""
Merge k Sorted Lists - LeetCode #23 (Hard)

You are given an array of k linked-lists, each linked-list is sorted in ascending order.

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
                 merging them into one sorted list:
                 1->1->2->3->4->4->5->6

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

Time Complexities:
    - Approach 1 (Merge one by one): O(k * n) where n is avg list length
    - Approach 2 (Heap/Priority Queue): O(N log k) - N is total nodes
    - Approach 3 (Divide and Conquer): O(N log k)

Space Complexities:
    - Approach 1: O(1) extra space
    - Approach 2: O(k) for heap
    - Approach 3: O(log k) for recursion stack
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
        """Enable comparison for heapq."""
        return self.val < other.val

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"ListNode({self.val})"


def merge_k_lists_heap(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted lists using a min-heap.

    Time Complexity: O(N log k) where N is total number of nodes
    Space Complexity: O(k) for the heap

    Args:
        lists: List of sorted linked list heads (can be None)

    Returns:
        Head of the merged sorted linked list
    """
    # Initialize dummy node for result list
    dummy = ListNode(0)
    current = dummy

    # Add all non-empty list heads to heap
    # Heap stores (value, list_index, node) to handle duplicate values
    heap = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    # Extract minimum, add to result, push next node from same list
    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_lists_divide_conquer(
    lists: list[Optional[ListNode]],
) -> Optional[ListNode]:
    """
    Merge k sorted lists using divide and conquer.

    Time Complexity: O(N log k)
    Space Complexity: O(log k) for recursion stack

    Args:
        lists: List of sorted linked list heads (can be None)

    Returns:
        Head of the merged sorted linked list
    """
    if not lists:
        return None

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

    # Base case: single list
    if len(lists) == 1:
        return lists[0]

    # Divide: split into two halves
    mid = len(lists) // 2
    left = merge_k_lists_divide_conquer(lists[:mid])
    right = merge_k_lists_divide_conquer(lists[mid:])

    # Conquer: merge the two halves
    return merge_two(left, right)


def merge_k_lists_naive(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted lists by merging one by one (simple approach).

    Time Complexity: O(k * N) where N is total nodes
    Space Complexity: O(1)

    Args:
        lists: List of sorted linked list heads (can be None)

    Returns:
        Head of the merged sorted linked list
    """
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

        current.next = a or b
        return dummy.next

    result = None
    for node in lists:
        result = merge_two(result, node)

    return result


# Alias for the primary solution (using heap - most efficient)
merge_k_lists = merge_k_lists_heap


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
