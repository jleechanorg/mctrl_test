"""
Merge k Sorted Lists - LeetCode Hard

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
- Approach 1 (Merge one by one): O(k * n) where n is avg length
- Approach 2 (Heap/Priority Queue): O(N log k) where N is total elements
- Approach 3 (Divide and Conquer): O(N log k)

Space Complexity:
- Heap approach: O(k) for the heap
- Divide and Conquer: O(1) extra space (excluding recursion stack)
"""

from __future__ import annotations
from typing import List, Optional
import heapq


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

    def __repr__(self) -> str:
        return f"ListNode({self.val})"

    def to_list(self) -> List[int]:
        """Convert linked list to Python list for easy verification."""
        result = []
        current = self
        while current:
            result.append(current.val)
            current = current.next
        return result

    @staticmethod
    def from_list(values: List[int]) -> Optional['ListNode']:
        """Create linked list from Python list."""
        if not values:
            return None
        dummy = ListNode(0)
        current = dummy
        for val in values:
            current.next = ListNode(val)
            current = current.next
        return dummy.next


def merge_k_lists_heap(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using a min-heap.

    This approach uses a min-heap to always get the smallest element
    among the current heads of all k lists in O(log k) time.

    Time Complexity: O(N log k) where N is total number of nodes
    Space Complexity: O(k) for the heap

    Args:
        lists: List of k sorted linked lists

    Returns:
        The head of the merged sorted linked list
    """
    # Handle edge cases
    if not lists:
        return None

    # Filter out None/empty lists and create min-heap
    # Heap elements: (value, list_index, node)
    heap = []
    for i, head in enumerate(lists):
        if head:
            heapq.heappush(heap, (head.val, i, head))

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


def merge_k_lists_divide_conquer(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer.

    This approach recursively merges pairs of lists until one remains.
    Similar to merge sort's merge step.

    Time Complexity: O(N log k)
    Space Complexity: O(log k) for recursion stack

    Args:
        lists: List of k sorted linked lists

    Returns:
        The head of the merged sorted linked list
    """
    if not lists:
        return None
    if len(lists) == 1:
        return lists[0]

    # Merge two sorted linked lists
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

    # Divide and conquer: merge pairs
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


# For backwards compatibility - default to heap approach
merge_k_lists = merge_k_lists_heap
