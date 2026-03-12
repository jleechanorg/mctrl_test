"""
Merge k Sorted Lists - LeetCode #23 (Hard)

You are given an array of k linked-lists lists, each linked-list is sorted in ascending order.
Merge all the linked-lists into one sorted linked-list and return it.

This module provides multiple solution approaches:
1. Divide and Conquer - O(N log k) time, O(1) space (excluding output)
2. Heap-based - O(N log k) time, O(k) space
3. Two-pointer merge - O(Nk) time, O(1) space

Author: Claude
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
        return self.to_list() == other.to_list()

    def to_list(self) -> list[int]:
        """Convert linked list to Python list for easy comparison."""
        result = []
        node = self
        while node:
            result.append(node.val)
            node = node.next
        return result

    @classmethod
    def from_list(cls, values: list[int]) -> Optional['ListNode']:
        """Create a linked list from a Python list."""
        if not values:
            return None
        dummy = cls()
        current = dummy
        for val in values:
            current.next = cls(val)
            current = current.next
        return dummy.next


def merge_two_lists(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    """
    Merge two sorted linked lists into one sorted list.

    Time Complexity: O(n + m) where n, m are lengths of the two lists
    Space Complexity: O(1)
    """
    dummy = ListNode()
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
    current.next = l1 if l1 else l2

    return dummy.next


def merge_k_lists_divide_and_conquer(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted lists using divide and conquer approach.

    Strategy:
    - Pair up k lists and merge each pair
    - Repeat until only one list remains

    Time Complexity: O(N log k) where N is total number of nodes
    Space Complexity: O(1) excluding the output list
    """
    if not lists:
        return None
    if len(lists) == 1:
        return lists[0]

    while len(lists) > 1:
        merged_lists = []

        for i in range(0, len(lists) - 1, 2):
            merged = merge_two_lists(lists[i], lists[i + 1])
            merged_lists.append(merged)

        # If odd number of lists, add the last one
        if len(lists) % 2 == 1:
            merged_lists.append(lists[-1])

        lists = merged_lists

    return lists[0]


def merge_k_lists_heap(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted lists using a min-heap.

    Strategy:
    - Push first node from each list into min-heap
    - Extract minimum, push next node from that list
    - Continue until heap is empty

    Time Complexity: O(N log k) where N is total number of nodes
    Space Complexity: O(k) for the heap
    """
    # Custom comparator for heapq (heapq is min-heap by default)
    class NodeWrapper:
        __slots__ = ['val', 'node']
        def __init__(self, node: ListNode):
            self.val = node.val
            self.node = node
        def __lt__(self, other: 'NodeWrapper') -> bool:
            return self.val < other.val

    dummy = ListNode()
    current = dummy
    heap = []

    # Initialize heap with first node from each list
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, NodeWrapper(lst))

    # Extract minimum and add next node from same list
    while heap:
        wrapper = heapq.heappop(heap)
        current.next = wrapper.node
        current = current.next

        if wrapper.node.next:
            heapq.heappush(heap, NodeWrapper(wrapper.node.next))

    return dummy.next


# Expose main function - choose the most efficient approach
def merge_k_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked-lists into one sorted linked-list.

    This is the main exported function that uses divide-and-conquer
    for optimal time complexity.

    Args:
        lists: List of sorted linked-lists (may contain None)

    Returns:
        The merged sorted linked-list

    Time Complexity: O(N log k) where N = total nodes, k = number of lists
    Space Complexity: O(1) excluding output

    Example:
        >>> lists = [ListNode.from_list([1,4,5]), ListNode.from_list([1,3,4]), ListNode.from_list([2,6])]
        >>> result = merge_k_lists(lists)
        >>> result.to_list()
        [1, 1, 2, 3, 4, 4, 5, 6]
    """
    return merge_k_lists_divide_and_conquer(lists)


if __name__ == "__main__":
    # Quick test
    lists = [
        ListNode.from_list([1, 4, 5]),
        ListNode.from_list([1, 3, 4]),
        ListNode.from_list([2, 6])
    ]
    result = merge_k_lists(lists)
    print(f"Result: {result.to_list()}")  # [1, 1, 2, 3, 4, 4, 5, 6]
