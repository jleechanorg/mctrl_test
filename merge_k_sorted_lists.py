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
    - lists[i] is sorted in ascending order.
    - The sum of lists[i].length will not exceed 10^4.

Time Complexity Analysis:
    - Approach 1 (Merge one by one): O(k * n) where n is average length
    - Approach 2 (Divide and Conquer): O(N log k) where N is total elements
    - Approach 3 (Heap/Priority Queue): O(N log k)

Space Complexity:
    - Approach 1: O(1) extra space
    - Approach 2: O(log k) for recursion stack
    - Approach 3: O(k) for heap

We implement the Heap-based approach as it's optimal and elegant.
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

    @classmethod
    def from_list(cls, values: list[int]) -> Optional['ListNode']:
        """Create a linked list from a list of values."""
        if not values:
            return None
        dummy = cls(0)
        current = dummy
        for val in values:
            current.next = cls(val)
            current = current.next
        return dummy.next

    def to_list(self) -> list[int]:
        """Convert linked list to Python list for easy comparison."""
        result = []
        current = self
        while current:
            result.append(current.val)
            current = current.next
        return result


def merge_k_lists_heap(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using a min-heap.

    Algorithm:
    1. Initialize a min-heap
    2. Push the first node from each list (value, list_index, node)
    3. Pop the smallest, add to result, push next node from same list
    4. Repeat until heap is empty

    Args:
        lists: List of sorted linked list heads (can be None/empty)

    Returns:
        Head of merged sorted linked list

    Time Complexity: O(N log k) where N = total elements, k = number of lists
    Space Complexity: O(k) for the heap
    """
    # Min-heap stores tuples: (value, list_index, node)
    # list_index is used to break ties and ensure deterministic ordering
    heap: list[tuple[int, int, ListNode]] = []

    # Initialize heap with first node from each non-empty list
    for i, head in enumerate(lists):
        if head:
            # Push (value, list_index, node) to heap
            heappush(heap, (head.val, i, head))

    # Dummy node to simplify result list construction
    dummy = ListNode(0)
    current = dummy

    # Extract min and add next node from same list
    while heap:
        val, list_idx, node = heappop(heap)
        current.next = node
        current = current.next

        # Push next node from same list if exists
        if node.next:
            heappush(heap, (node.next.val, list_idx, node.next))

    return dummy.next


def merge_k_lists_divide_conquer(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer.

    Algorithm:
    1. If only one list, return it
    2. Split lists into two halves
    3. Recursively merge each half
    4. Merge the two results

    Time Complexity: O(N log k)
    Space Complexity: O(log k) for recursion stack
    """
    if not lists:
        return None

    if len(lists) == 1:
        return lists[0]

    mid = len(lists) // 2
    left = merge_k_lists_divide_conquer(lists[:mid])
    right = merge_k_lists_divide_conquer(lists[mid:])

    return merge_two_lists(left, right)


def merge_two_lists(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    """Merge two sorted linked lists into one sorted list."""
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


# Export the main solution
merge_k_lists = merge_k_lists_heap
