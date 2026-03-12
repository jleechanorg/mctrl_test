"""
Merge k Sorted Lists - LeetCode Hard Problem

Merge k sorted linked lists and return it as one sorted list.

Approach: Use a min-heap (priority queue) to efficiently merge k sorted lists.
- Push the first node from each list into the heap
- Pop the smallest, add it to result, push the next node from that list
- Repeat until heap is empty

Time Complexity: O(N log k) where N = total nodes, k = number of lists
Space Complexity: O(k) for the heap + O(N) for result list
"""
from __future__ import annotations

import heapq
from typing import Optional


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional[ListNode] = None):
        self.val = val
        self.next = next

    def __lt__(self, other: "ListNode") -> bool:
        """Enable comparison for heapq."""
        return self.val < other.val

    @classmethod
    def from_list(cls, values: list[int]) -> Optional[ListNode]:
        """Create a linked list from a list of values."""
        if not values:
            return None
        head = cls(values[0])
        current = head
        for val in values[1:]:
            current.next = cls(val)
            current = current.next
        return head

    def to_list(self) -> list[int]:
        """Convert linked list to Python list."""
        result = []
        current = self
        while current:
            result.append(current.val)
            current = current.next
        return result


def merge_k_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists into one sorted list.

    Args:
        lists: List of sorted linked list heads (can contain None)

    Returns:
        Head of the merged sorted linked list

    Example:
        >>> l1 = ListNode.from_list([1, 4, 5])
        >>> l2 = ListNode.from_list([1, 3, 4])
        >>> l3 = ListNode.from_list([2, 6])
        >>> merged = merge_k_lists([l1, l2, l3])
        >>> merged.to_list()
        [1, 1, 2, 3, 4, 4, 5, 6]
    """
    # Initialize min-heap with first node from each non-empty list
    heap: list[ListNode] = []

    for lst in lists:
        if lst:
            heapq.heappush(heap, lst)

    # Dummy head to simplify edge cases
    dummy = ListNode(0)
    current = dummy

    # Merge: always take the smallest from heap
    while heap:
        smallest = heapq.heappop(heap)
        current.next = smallest
        current = current.next

        # Push next node from the same list
        if smallest.next:
            heapq.heappush(heap, smallest.next)

    return dummy.next


def merge_k_lists_naive(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Naive approach: collect all values, sort, and rebuild list.
    Useful for verification but less efficient.

    Time Complexity: O(N log N)
    Space Complexity: O(N)
    """
    all_values: list[int] = []

    for lst in lists:
        current = lst
        while current:
            all_values.append(current.val)
            current = current.next

    # Sort and rebuild
    all_values.sort()
    return ListNode.from_list(all_values)
