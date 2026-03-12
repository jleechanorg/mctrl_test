"""
Merge k Sorted Lists - LeetCode #23 (Hard)

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
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List
import heapq


@dataclass
class ListNode:
    """Definition for singly-linked list node."""
    val: int = 0
    next: Optional['ListNode'] = None


def merge_k_lists_heap(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using a min-heap.

    Time Complexity: O(N log k) where N is total number of nodes
    Space Complexity: O(k) for the heap

    Args:
        lists: List of sorted linked list heads

    Returns:
        Head of the merged sorted linked list
    """
    # Initialize a min-heap with (value, list_index, node)
    # We include list_index to break ties when values are equal
    heap = []

    # Add the first node from each non-empty list to the heap
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    # Dummy head to simplify edge cases
    dummy = ListNode(0)
    current = dummy

    # Extract min, add to result, push next node from same list
    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        # Push next node from the same list if it exists
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_lists_divide_conquer(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer.

    Time Complexity: O(N log k)
    Space Complexity: O(log k) for recursion stack

    This approach pairs up lists and merges them recursively,
    reducing the problem size by half each iteration.

    Args:
        lists: List of sorted linked list heads

    Returns:
        Head of the merged sorted linked list
    """
    if not lists:
        return None
    if len(lists) == 1:
        return lists[0]

    # Helper function to merge two sorted lists
    def merge_two(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
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

    # Iteratively merge pairs until one list remains
    while len(lists) > 1:
        merged_lists = []

        # Process pairs
        for i in range(0, len(lists) - 1, 2):
            merged = merge_two(lists[i], lists[i + 1])
            merged_lists.append(merged)

        # Handle odd case - last list if odd number
        if len(lists) % 2 == 1:
            merged_lists.append(lists[-1])

        lists = merged_lists

    return lists[0]


def merge_two_lists(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    """
    Merge two sorted linked lists into one sorted list.

    Time Complexity: O(n + m)
    Space Complexity: O(1)

    Args:
        l1: First sorted linked list
        l2: Second sorted linked list

    Returns:
        Head of the merged sorted list
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

    current.next = l1 or l2
    return dummy.next


def list_to_linkedlist(values: List[int]) -> Optional[ListNode]:
    """Convert a Python list to a linked list."""
    if not values:
        return None

    dummy = ListNode(0)
    current = dummy
    for val in values:
        current.next = ListNode(val)
        current = current.next
    return dummy.next


def linkedlist_to_list(node: Optional[ListNode]) -> List[int]:
    """Convert a linked list to a Python list."""
    result = []
    while node:
        result.append(node.val)
        node = node.next
    return result


# Main solution function - uses heap approach by default
def merge_k_lists(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Main function to merge k sorted linked lists.
    Uses heap approach for better practical performance.
    """
    return merge_k_lists_heap(lists)
