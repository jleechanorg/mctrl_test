"""
Merge k Sorted Lists - LeetCode Hard Problem

You are given an array of k linked-lists, each linked-list is sorted in ascending order.

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

Time Complexities:
    - Heap approach: O(N log k) where N = total elements, k = number of lists
    - Divide and conquer: O(N log k)

Space Complexity:
    - Heap approach: O(k) for the heap
    - Divide and conquer: O(log k) for recursion stack
"""
from __future__ import annotations

from heapq import heappush, heappop
from typing import Optional


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


def merge_k_lists_heap(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using a min-heap.

    Uses heapq to always get the smallest element among all list heads.
    Time: O(N log k), Space: O(k)

    Args:
        lists: List of sorted linked list heads (may be None)

    Returns:
        Head of merged sorted linked list
    """
    # Min-heap stores (value, list_index, node) tuples
    # list_index breaks ties when values are equal
    heap: list[tuple[int, int, ListNode]] = []

    # Initialize heap with first element from each non-empty list
    for i, head in enumerate(lists):
        if head:
            heappush(heap, (head.val, i, head))

    # Dummy node to simplify edge cases
    dummy = ListNode(0)
    current = dummy

    # Extract min and add next element from same list
    while heap:
        val, i, node = heappop(heap)
        current.next = node
        current = current.next

        # Add next node from same list to heap
        if node.next:
            heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_lists_divide_conquer(
    lists: list[Optional[ListNode]],
) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer.

    Recursively merge pairs of lists until one remains.
    Time: O(N log k), Space: O(log k) for recursion

    Args:
        lists: List of sorted linked list heads (may be None)

    Returns:
        Head of merged sorted linked list
    """
    if not lists:
        return None
    if len(lists) == 1:
        return lists[0]

    # Merge two sorted linked lists
    def merge_two(a: Optional[ListNode], b: Optional[ListNode]) -> Optional[ListNode]:
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

    # Divide and conquer: merge pairs
    while len(lists) > 1:
        new_lists: list[Optional[ListNode]] = []
        for i in range(0, len(lists) - 1, 2):
            merged = merge_two(lists[i], lists[i + 1])
            new_lists.append(merged)
        # Handle odd case - last list remains unpaired
        if len(lists) % 2 == 1:
            new_lists.append(lists[-1])
        lists = new_lists

    return lists[0]


# Primary export - using heap approach as it's more intuitive
merge_k_lists = merge_k_lists_heap
