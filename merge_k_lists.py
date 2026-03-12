"""
Merge k Sorted Lists (LeetCode #23)

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

Time Complexity: O(N log k) where N is total number of nodes, k is number of lists
Space Complexity: O(k) for the heap

Approach:
    Use a min-heap to always get the smallest element among all lists.
    For each node, we push (value, list_index, node) into the heap and pop the smallest.
    We then advance that list and push the next node.
"""
from __future__ import annotations

import heapq
from typing import Optional


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional["ListNode"] = None):
        self.val = val
        self.next = next

    def __lt__(self, other: "ListNode") -> bool:
        """Enable comparison for heapq."""
        return self.val < other.val


def merge_k_sorted_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists into one sorted linked list.

    Args:
        lists: List of sorted linked lists (may contain None)

    Returns:
        The head of the merged sorted linked list

    Example:
        >>> l1 = ListNode(1, ListNode(4, ListNode(5)))
        >>> l2 = ListNode(1, ListNode(3, ListNode(4)))
        >>> l3 = ListNode(2, ListNode(6))
        >>> result = merge_k_sorted_lists([l1, l2, l3])
        >>> values = []
        >>> while result:
        ...     values.append(result.val)
        ...     result = result.next
        >>> values
        [1, 1, 2, 3, 4, 4, 5, 6]
    """
    # Initialize min-heap with (value, list_index, node)
    heap: list[tuple[int, int, ListNode]] = []

    # Add first node from each non-empty list to heap
    for i, head in enumerate(lists):
        if head:
            heapq.heappush(heap, (head.val, i, head))

    # Dummy head for result list
    dummy = ListNode(0)
    current = dummy

    # Process heap until empty
    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        # Push next node from same list if exists
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def list_to_linked(arr: list[int]) -> Optional[ListNode]:
    """Convert a Python list to a linked list."""
    if not arr:
        return None
    dummy = ListNode(0)
    current = dummy
    for val in arr:
        current.next = ListNode(val)
        current = current.next
    return dummy.next


def linked_to_list(head: Optional[ListNode]) -> list[int]:
    """Convert a linked list to a Python list."""
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result


if __name__ == "__main__":
    # Test example 1
    l1 = list_to_linked([1, 4, 5])
    l2 = list_to_linked([1, 3, 4])
    l3 = list_to_linked([2, 6])
    result = merge_k_sorted_lists([l1, l2, l3])
    print(f"Example 1: {linked_to_list(result)}")  # [1, 1, 2, 3, 4, 4, 5, 6]

    # Test example 2
    result = merge_k_sorted_lists([])
    print(f"Example 2: {linked_to_list(result)}")  # []

    # Test example 3
    result = merge_k_sorted_lists([[]])
    print(f"Example 3: {linked_to_list(result)}")  # []
