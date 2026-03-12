"""
Merge k Sorted Lists

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

Time Complexity Analysis:
    - Approach 1 (Merge one by one): O(k * n) where n is average length
    - Approach 2 (Divide and Conquer): O(N log k) where N is total elements
    - Approach 3 (Heap/Priority Queue): O(N log k)

Space Complexity:
    - Approach 1: O(1) extra space
    - Approach 2: O(log k) recursion stack
    - Approach 3: O(k) for the heap
"""
from __future__ import annotations

from heapq import heappush, heappop
from typing import Optional


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional[ListNode] = None):
        self.val = val
        self.next = next

    def __repr__(self) -> str:
        return f"ListNode({self.val})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ListNode):
            return False
        return self.val == other.val and self.next == other.next

    def to_list(self) -> list[int]:
        """Convert linked list to Python list for easy comparison."""
        result = []
        current = self
        while current:
            result.append(current.val)
            current = current.next
        return result

    @classmethod
    def from_list(cls, values: list[int]) -> Optional[ListNode]:
        """Create linked list from Python list."""
        if not values:
            return None
        dummy = cls()
        current = dummy
        for val in values:
            current.next = cls(val)
            current = current.next
        return dummy.next


def merge_k_lists_heap(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted lists using a min-heap.

    Uses heapq to always get the smallest element among all list heads.
    Time: O(N log k) where N = total elements, k = number of lists
    Space: O(k) for the heap

    Args:
        lists: List of sorted linked lists

    Returns:
        Merged sorted linked list
    """
    # Min-heap stores (value, list_index, node)
    # list_index breaks ties when values are equal
    min_heap: list[tuple[int, int, ListNode]] = []

    # Initialize heap with first node from each non-empty list
    for i, head in enumerate(lists):
        if head:
            heappush(min_heap, (head.val, i, head))

    # Dummy head for result
    dummy = ListNode(0)
    current = dummy

    # Extract min and add next node from same list
    while min_heap:
        val, i, node = heappop(min_heap)
        current.next = node
        current = current.next

        # Add next node from this list to heap
        if node.next:
            heappush(min_heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_lists_divide_conquer(
    lists: list[Optional[ListNode]],
) -> Optional[ListNode]:
    """
    Merge k sorted lists using divide and conquer.

    Recursively merge pairs of lists until one remains.
    Time: O(N log k)
    Space: O(log k) for recursion stack

    Args:
        lists: List of sorted linked lists

    Returns:
        Merged sorted linked list
    """
    if not lists:
        return None
    if len(lists) == 1:
        return lists[0]

    mid = len(lists) // 2
    left = merge_k_lists_divide_conquer(lists[:mid])
    right = merge_k_lists_divide_conquer(lists[mid:])

    return merge_two_lists(left, right)


def merge_two_lists(
    l1: Optional[ListNode], l2: Optional[ListNode]
) -> Optional[ListNode]:
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


def merge_k_lists_naive(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted lists by merging one by one.

    Simple approach: keep merging with the result.
    Time: O(k * N) - less efficient
    Space: O(1)

    Args:
        lists: List of sorted linked lists

    Returns:
        Merged sorted linked list
    """
    result = None
    for linked_list in lists:
        result = merge_two_lists(result, linked_list)
    return result
