"""
Merge k Sorted Lists - LeetCode Hard

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

Approaches:
1. Brute Force: Collect all values, sort, and rebuild list - O(N log N)
2. Min-Heap: Use a min-heap to always get the smallest element - O(N log k)
3. Divide and Conquer: Merge pairs recursively - O(N log k)
4. Iterative with k-way merge - O(N log k)

We implement the min-heap approach (optimal for most cases).
Time Complexity: O(N log k) where N is total elements, k is number of lists
Space Complexity: O(k) for the heap + O(N) for the result list
"""

from __future__ import annotations
import heapq
from typing import Optional, List


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

    @classmethod
    def from_list(cls, values: List[int]) -> Optional['ListNode']:
        """Create a linked list from a Python list."""
        if not values:
            return None
        dummy = cls(0)
        current = dummy
        for val in values:
            current.next = cls(val)
            current = current.next
        return dummy.next


def merge_k_lists(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using a min-heap.

    Args:
        lists: List of sorted linked lists

    Returns:
        The head of the merged sorted linked list

    Algorithm:
        1. Initialize a min-heap with (value, list_index, node) for each list's head
        2. Repeatedly extract the minimum, add it to result, and push the next node
        3. Continue until heap is empty

    Time Complexity: O(N log k)
        - N = total number of nodes across all lists
        - k = number of lists
        - Each node is pushed/popped from heap once: O(N log k)

    Space Complexity: O(k) for the heap + O(N) for output list
    """
    # Handle edge cases
    if not lists:
        return None

    # Filter out empty lists
    heap = []

    # Initialize heap with first node from each non-empty list
    for i, head in enumerate(lists):
        if head:
            # heapq uses tuples for comparison; we add index to break ties
            heapq.heappush(heap, (head.val, i, head))

    # Dummy head for the result list
    dummy = ListNode(0)
    current = dummy

    # Merge process
    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        # If there's a next node in this list, add it to heap
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_lists_divide_conquer(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer.

    This approach pairs up lists and merges them recursively.

    Time Complexity: O(N log k)
    Space Complexity: O(log k) for recursion stack
    """
    if not lists:
        return None
    if len(lists) == 1:
        return lists[0]

    # Merge two sorted lists helper
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
        current.next = l1 or l2
        return dummy.next

    # Divide and conquer: merge pairs repeatedly
    while len(lists) > 1:
        new_lists = []
        for i in range(0, len(lists) - 1, 2):
            merged = merge_two(lists[i], lists[i + 1])
            new_lists.append(merged)
        # Handle odd case
        if len(lists) % 2 == 1:
            new_lists.append(lists[-1])
        lists = new_lists

    return lists[0]


def merge_k_lists_brute_force(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using brute force approach.

    Collect all values, sort them, and rebuild the list.

    Time Complexity: O(N log N)
    Space Complexity: O(N) for storing all values
    """
    # Collect all values
    values = []
    for head in lists:
        current = head
        while current:
            values.append(current.val)
            current = current.next

    # Sort values
    values.sort()

    # Rebuild linked list
    dummy = ListNode(0)
    current = dummy
    for val in values:
        current.next = ListNode(val)
        current = current.next

    return dummy.next
