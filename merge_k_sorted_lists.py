"""
Merge k Sorted Lists - LeetCode Hard

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
    - lists[i] is sorted in ascending order.
    - The sum of lists[i].length will not exceed 10^4.
"""

from __future__ import annotations
import heapq
from typing import Optional


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

    def __repr__(self) -> str:
        return f"ListNode({self.val})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ListNode):
            return NotImplemented
        return self.val == other.val

    def __lt__(self, other: 'ListNode') -> bool:
        return self.val < other.val


def merge_k_lists_heap(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted lists using a min-heap.

    Time Complexity: O(N log k) where N is total nodes, k is number of lists
    Space Complexity: O(k) for the heap

    Args:
        lists: List of sorted linked lists

    Returns:
        Merged sorted linked list
    """
    # Dummy head to simplify edge cases
    dummy = ListNode(-1)
    current = dummy

    # Min-heap: (value, list_index, node)
    # We include list_index to avoid comparison errors between nodes
    heap: list[tuple[int, int, ListNode]] = []

    # Initialize heap with first node from each list
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    # Extract minimum and add next node from same list
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
    Merge k sorted lists using divide and conquer (pairwise merging).

    Time Complexity: O(N log k) - each level processes all N nodes
    Space Complexity: O(1) extra space (excluding recursion stack)

    Args:
        lists: List of sorted linked lists

    Returns:
        Merged sorted linked list
    """
    if not lists:
        return None

    # Convert to mutable list
    lists = lists[:]

    # Repeatedly merge pairs until one list remains
    while len(lists) > 1:
        new_lists: list[Optional[ListNode]] = []

        # Merge pairs
        for i in range(0, len(lists) - 1, 2):
            merged = merge_two_lists(lists[i], lists[i + 1])
            new_lists.append(merged)

        # Handle odd list at the end
        if len(lists) % 2 == 1:
            new_lists.append(lists[-1])

        lists = new_lists

    return lists[0]


def merge_two_lists(
    l1: Optional[ListNode], l2: Optional[ListNode]
) -> Optional[ListNode]:
    """
    Merge two sorted linked lists into one sorted list.

    Time Complexity: O(n + m)
    Space Complexity: O(1)

    Args:
        l1: First sorted linked list
        l2: Second sorted linked list

    Returns:
        Merged sorted linked list
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


def list_to_linkedlist(values: list[int]) -> Optional[ListNode]:
    """Convert a Python list to a linked list."""
    if not values:
        return None

    dummy = ListNode(-1)
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


# Export primary solution
Solution = merge_k_lists_heap  # Heap approach is more intuitive
