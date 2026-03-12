"""
Merge k Sorted Lists - LeetCode Hard Problem

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
"""
from __future__ import annotations
from typing import Optional, List
import heapq


class ListNode:
    """Definition for singly-linked list node."""
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

    def __repr__(self):
        return f"ListNode({self.val})"

    def __lt__(self, other: 'ListNode'):
        """Required for heap comparison."""
        return self.val < other.val


def merge_k_lists_heap(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted lists using a min-heap.

    Time Complexity: O(N log k) where N is total nodes, k is number of lists
    Space Complexity: O(k) for the heap

    Args:
        lists: List of sorted linked list heads

    Returns:
        Head of the merged sorted linked list
    """
    # Dummy head to simplify edge cases
    dummy = ListNode(-1)
    current = dummy

    # Min-heap: (value, list_index, node)
    # list_index ensures proper comparison when values are equal
    heap = []

    # Initialize heap with first node from each list
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    # Extract min, add to result, push next node from same list
    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_lists_divide_conquer(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted lists using divide and conquer (pairwise merging).

    Time Complexity: O(N log k)
    Space Complexity: O(log k) for recursion stack

    Args:
        lists: List of sorted linked list heads

    Returns:
        Head of the merged sorted linked list
    """
    if not lists:
        return None

    # Base case: only one list
    if len(lists) == 1:
        return lists[0]

    # Merge two sorted lists helper
    def merge_two(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
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

        current.next = l1 or l2
        return dummy.next

    # Repeatedly merge pairs until one list remains
    while len(lists) > 1:
        new_lists = []

        for i in range(0, len(lists) - 1, 2):
            merged = merge_two(lists[i], lists[i + 1])
            new_lists.append(merged)

        # Handle odd number of lists
        if len(lists) % 2 == 1:
            new_lists.append(lists[-1])

        lists = new_lists

    return lists[0]


# ============== Helper functions for testing ==============

def list_to_linkedlist(arr: List[int]) -> Optional[ListNode]:
    """Convert a Python list to a linked list."""
    if not arr:
        return None

    dummy = ListNode(-1)
    current = dummy

    for val in arr:
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


# ============== Main solution to expose ==============

def merge_k_sorted_lists(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Main entry point - uses heap-based approach.

    Merge k sorted linked-lists into one sorted linked-list.

    Args:
        lists: List of sorted linked list heads

    Returns:
        Head of the merged sorted linked list
    """
    return merge_k_lists_heap(lists)


if __name__ == "__main__":
    # Example 1
    lists = [
        list_to_linkedlist([1, 4, 5]),
        list_to_linkedlist([1, 3, 4]),
        list_to_linkedlist([2, 6])
    ]
    result = merge_k_sorted_lists(lists)
    print(linkedlist_to_list(result))  # [1, 1, 2, 3, 4, 4, 5, 6]

    # Example 2: Empty list
    lists = []
    result = merge_k_sorted_lists(lists)
    print(linkedlist_to_list(result))  # []

    # Example 3: List with empty list
    lists = [list_to_linkedlist([])]
    result = merge_k_sorted_lists(lists)
    print(linkedlist_to_list(result))  # []
