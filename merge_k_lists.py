"""
Merge k Sorted Lists

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

Time Complexity Analysis:
    - Heap approach: O(N log k) where N is total nodes, k is number of lists
    - Divide and Conquer: O(N log k) - same complexity, better space

Space Complexity:
    - Heap approach: O(k) for the heap
    - Divide and Conquer: O(1) extra space (excluding recursion stack)
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

    def to_list(self) -> list[int]:
        """Convert linked list to Python list for easy verification."""
        result = []
        node = self
        while node:
            result.append(node.val)
            node = node.next
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
    Merge k sorted lists using a min-heap.

    Approach:
    - Push the first node from each list into a min-heap
    - Pop the smallest, add it to result, push next node from same list
    - Repeat until heap is empty

    Time: O(N log k) where N = total nodes, k = number of lists
    Space: O(k) for the heap
    """
    # Handle edge cases
    if not lists:
        return None

    # Initialize heap with (value, list_index, node) tuples
    # Using list_index to break ties and avoid comparison issues
    heap = []

    # Add first node from each non-empty list
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    # Dummy head for result
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


def merge_k_lists_divide_conquer(
    lists: list[Optional[ListNode]]
) -> Optional[ListNode]:
    """
    Merge k sorted lists using divide and conquer.

    Approach:
    - Pair up lists and merge them recursively
    - Each merge operation is O(n) where n is total nodes in both lists
    - Height of recursion tree is O(log k)
    - Total time: O(N log k)

    Time: O(N log k)
    Space: O(log k) for recursion stack (O(1) extra if we ignore recursion)
    """
    if not lists:
        return None
    if len(lists) == 1:
        return lists[0]

    def merge_two(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
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

    # Iteratively merge pairs
    while len(lists) > 1:
        new_lists = []
        for i in range(0, len(lists) - 1, 2):
            merged = merge_two(lists[i], lists[i + 1])
            new_lists.append(merged)
        # If odd number of lists, add the last one
        if len(lists) % 2 == 1:
            new_lists.append(lists[-1])
        lists = new_lists

    return lists[0]


# Expose main function as default (commonly expected interface)
def merge_k_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked-lists into one sorted linked-list.

    This is the main entry point - uses heap-based approach for clarity.
    For better space efficiency, use merge_k_lists_divide_conquer.

    Time: O(N log k)
    Space: O(k)
    """
    return merge_k_lists_heap(lists)
