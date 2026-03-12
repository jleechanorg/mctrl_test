"""
LeetCode Hard Problem: Merge k Sorted Lists

You are given an array of k linked-lists lists, each linked-list is sorted in ascending order.
Merge all the linked-lists into one sorted linked-list and return it.

Example 1:
Input: lists = [[1,4,5],[1,3,4],[2,6]]
Output: [1,1,2,3,4,4,5,6]
Explanation: The linked-lists are:
[
  1->4->5,
  1->3->4,
  2->6
]
merging them into one sorted list: 1->1->2->3->4->4->5->6

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
- Divide and conquer: O(N log k)

Space Complexity:
- Heap approach: O(k) for the heap
- Divide and conquer: O(log k) for recursion stack
"""

from __future__ import annotations
from typing import Optional
import heapq


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

    def __lt__(self, other: 'ListNode') -> bool:
        """Enable comparison for heapq."""
        return self.val < other.val

    def __repr__(self) -> str:
        """String representation of the linked list."""
        values = []
        node = self
        while node:
            values.append(str(node.val))
            node = node.next
        return "->".join(values) if values else "Empty"


def merge_k_lists_heap(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using a min-heap.

    Algorithm:
    1. Initialize a min-heap with the first node from each non-empty list
    2. Pop the smallest node, add it to result, push the next node from same list
    3. Repeat until heap is empty

    Time: O(N log k) where N = total nodes, k = number of lists
    Space: O(k) for the heap

    Args:
        lists: List of sorted linked lists

    Returns:
        The merged sorted linked list
    """
    # Dummy head to simplify edge cases
    dummy = ListNode(0)
    current = dummy

    # Min-heap: (value, list_index, node)
    # list_index breaks ties when values are equal
    heap = []

    # Initialize heap with first node from each list
    for i, head in enumerate(lists):
        if head:
            heapq.heappush(heap, (head.val, i, head))

    # Merge process
    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        # Push next node from the same list
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_lists_divide_conquer(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer.

    Algorithm:
    1. Repeatedly merge pairs of lists until one list remains
    2. Uses the merge_two_lists helper

    Time: O(N log k)
    Space: O(log k) for recursion stack

    Args:
        lists: List of sorted linked lists

    Returns:
        The merged sorted linked list
    """
    if not lists:
        return None
    if len(lists) == 1:
        return lists[0]

    def merge_two_lists(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
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

        current.next = l1 if l1 else l2
        return dummy.next

    # Repeatedly merge pairs
    while len(lists) > 1:
        new_lists = []
        for i in range(0, len(lists) - 1, 2):
            merged = merge_two_lists(lists[i], lists[i + 1])
            new_lists.append(merged)
        # Handle odd number of lists
        if len(lists) % 2 == 1:
            new_lists.append(lists[-1])
        lists = new_lists

    return lists[0]


# Expose main function as default (for testing consistency)
merge_k_lists = merge_k_lists_heap


def list_to_linkedlist(values: list[int]) -> Optional[ListNode]:
    """Convert a Python list to a linked list."""
    if not values:
        return None

    dummy = ListNode(0)
    current = dummy
    for val in values:
        current.next = ListNode(val)
        current = current.next
    return dummy.next


def linkedlist_to_list(head: Optional[ListNode]) -> list[int]:
    """Convert a linked list to a Python list."""
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result


if __name__ == "__main__":
    # Test example 1
    lists = [
        list_to_linkedlist([1, 4, 5]),
        list_to_linkedlist([1, 3, 4]),
        list_to_linkedlist([2, 6]),
    ]
    result = merge_k_lists(lists)
    print("Example 1:", linkedlist_to_list(result))

    # Test example 2 (empty list)
    lists = []
    result = merge_k_lists(lists)
    print("Example 2:", linkedlist_to_list(result))

    # Test example 3 (list with empty list)
    lists = [[]]
    result = merge_k_lists(lists)
    print("Example 3:", linkedlist_to_list(result))
