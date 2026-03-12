"""
Merge k Sorted Lists - LeetCode Hard Problem

You are given an array of k linked-lists, each linked-list is sorted in ascending order.

Merge all the linked-lists into one sorted linked-list and return it.

Approach: Divide and Conquer
- Time Complexity: O(N log k) where N is total nodes, k is number of lists
- Space Complexity: O(log k) for recursion stack (or O(1) if we optimize)

The divide and conquer approach:
1. Merge pairs of lists recursively
2. Base case: 0 or 1 list
3. Merge two sorted lists in O(n) time
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

    def to_list(self) -> list[int]:
        """Convert linked list to Python list for easy verification."""
        result = []
        current = self
        while current:
            result.append(current.val)
            current = current.next
        return result

    @staticmethod
    def from_list(values: list[int]) -> Optional['ListNode']:
        """Create linked list from Python list."""
        if not values:
            return None
        dummy = ListNode(0)
        current = dummy
        for val in values:
            current.next = ListNode(val)
            current = current.next
        return dummy.next


def merge_two_lists(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    """
    Merge two sorted linked lists into one sorted list.

    Args:
        l1: First sorted linked list
        l2: Second sorted linked list

    Returns:
        Merged sorted linked list

    Time: O(n + m) where n, m are lengths of the two lists
    Space: O(1) - only modifies pointers
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


def merge_k_lists_divide_conquer(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted lists using divide and conquer.

    Approach:
    - Recursively merge pairs of lists
    - Each level reduces problem size by half
    - Final merge produces sorted result

    Time: O(N log k)
    Space: O(log k) for recursion stack
    """
    if not lists:
        return None
    if len(lists) == 1:
        return lists[0]

    mid = len(lists) // 2
    left = merge_k_lists_divide_conquer(lists[:mid])
    right = merge_k_lists_divide_conquer(lists[mid:])

    return merge_two_lists(left, right)


def merge_k_lists_heap(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted lists using a min-heap.

    Approach:
    - Use heap to always get smallest element
    - Push first node from each list with (value, list_index, node)
    - Heap automatically maintains order

    Time: O(N log k)
    Space: O(k) for heap

    Note: This is slightly slower due to heap overhead but demonstrates
    an alternative approach.
    """
    if not lists:
        return None

    # Min-heap: (value, list_index, node)
    heap = []

    # Initialize heap with first node from each list
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst.val, i, lst))

    dummy = ListNode(0)
    current = dummy

    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        # Push next node from same list
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


# Aliases for convenience
merge_k_lists = merge_k_lists_divide_conquer


def merge_k_lists_brute_force(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Brute force approach: collect all values, sort, rebuild list.

    Time: O(N log N) - dominated by sorting
    Space: O(N) for storing all values

    Simple but not optimal - included for comparison.
    """
    if not lists:
        return None

    # Collect all values
    values = []
    for lst in lists:
        while lst:
            values.append(lst.val)
            lst = lst.next

    if not values:
        return None

    # Sort
    values.sort()

    # Rebuild linked list
    dummy = ListNode(0)
    current = dummy
    for val in values:
        current.next = ListNode(val)
        current = current.next

    return dummy.next
