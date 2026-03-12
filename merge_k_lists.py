"""
Merge k Sorted Lists - LeetCode Hard

You are given an array of k linked-lists lists, each linked-list is sorted in ascending order.
Merge all the linked-lists into one sorted linked-list and return it.

Approaches:
1. Merge with Divide and Conquer - O(N log k) time, O(1) space
2. Heap/Priority Queue - O(N log k) time, O(k) space

where N = total number of nodes, k = number of lists
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import heapq


@dataclass
class ListNode:
    """Definition for singly-linked list node."""
    val: int
    next: Optional[ListNode] = None


class Solution:
    """
    Solution class for Merge k Sorted Lists.
    Implements both divide-and-conquer and heap-based approaches.
    """

    def mergeKLists(self, lists: list[Optional[ListNode]]) -> Optional[ListNode]:
        """
        Merge k sorted linked lists using divide and conquer.

        Time Complexity: O(N log k) where N = total nodes, k = number of lists
        Space Complexity: O(1) excluding the output list

        Args:
            lists: List of sorted linked list heads

        Returns:
            Head of the merged sorted linked list
        """
        if not lists:
            return None

        # Filter out None lists
        lists = [l for l in lists if l]
        if not lists:
            return None

        # Merge pairs iteratively
        while len(lists) > 1:
            merged_lists = []
            for i in range(0, len(lists), 2):
                if i + 1 < len(lists):
                    # Merge two lists
                    merged_lists.append(self._mergeTwoLists(lists[i], lists[i + 1]))
                else:
                    # Single list remaining
                    merged_lists.append(lists[i])
            lists = merged_lists

        return lists[0]

    def _mergeTwoLists(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        """Merge two sorted linked lists."""
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

    def mergeKListsHeap(self, lists: list[Optional[ListNode]]) -> Optional[ListNode]:
        """
        Merge k sorted linked lists using a min-heap.

        Time Complexity: O(N log k) where N = total nodes, k = number of lists
        Space Complexity: O(k) for the heap

        Args:
            lists: List of sorted linked list heads

        Returns:
            Head of the merged sorted linked list
        """
        # Min-heap: (value, list_index, node)
        heap: list[tuple[int, int, ListNode]] = []

        # Initialize heap with first node from each non-empty list
        for i, head in enumerate(lists):
            if head:
                heapq.heappush(heap, (head.val, i, head))

        dummy = ListNode(0)
        current = dummy

        while heap:
            val, i, node = heapq.heappop(heap)
            current.next = node
            current = current.next

            # Add next node from same list
            if node.next:
                heapq.heappush(heap, (node.next.val, i, node.next))

        return dummy.next


# Helper functions for testing
def create_linked_list(values: list[int]) -> Optional[ListNode]:
    """Create a linked list from a list of values."""
    if not values:
        return None

    dummy = ListNode(0)
    current = dummy
    for val in values:
        current.next = ListNode(val)
        current = current.next
    return dummy.next


def linked_list_to_list(head: Optional[ListNode]) -> list[int]:
    """Convert a linked list to a Python list."""
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result
