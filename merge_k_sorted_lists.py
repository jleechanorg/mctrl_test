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

Time Complexity Analysis:
    - Approach 1 (Heap): O(N log k) where N is total elements, k is number of lists
    - Approach 2 (Divide and Conquer): O(N log k)

Space Complexity:
    - Approach 1 (Heap): O(k) for the heap
    - Approach 2 (Divide and Conquer): O(1) extra space (excluding recursion stack)
"""

from __future__ import annotations
import heapq
from typing import Optional, List


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

    def __lt__(self, other: 'ListNode') -> bool:
        """Enable heap comparison based on node values."""
        return self.val < other.val

    def __repr__(self) -> str:
        return f"ListNode({self.val})"

    @staticmethod
    def from_list(values: List[int]) -> Optional['ListNode']:
        """Create a linked list from a list of values."""
        if not values:
            return None
        dummy = ListNode(0)
        current = dummy
        for val in values:
            current.next = ListNode(val)
            current = current.next
        return dummy.next

    def to_list(self) -> List[int]:
        """Convert linked list to Python list for easy verification."""
        result = []
        current = self
        while current:
            result.append(current.val)
            current = current.next
        return result


def merge_k_lists_heap(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using a min-heap.

    Algorithm:
        1. Initialize a min-heap with the first node from each non-empty list
        2. Extract the minimum element from heap and add next node from same list
        3. Repeat until heap is empty

    Time Complexity: O(N log k) - each of N elements is pushed/popped once, each O(log k)
    Space Complexity: O(k) - heap stores at most k elements
    """
    # Min-heap: (value, list_index, node)
    heap = []

    # Initialize heap with first node from each list
    for i, head in enumerate(lists):
        if head:
            heapq.heappush(heap, (head.val, i, head))

    dummy = ListNode(0)
    current = dummy

    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        # Push next node from same list if exists
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_lists_divide_conquer(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer.

    Algorithm:
        1. If 0 or 1 list, return directly
        2. Divide lists into two halves
        3. Recursively merge each half
        4. Merge the two results

    Time Complexity: O(N log k) - each level processes N elements, log k levels
    Space Complexity: O(1) extra space (excluding recursion stack)
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
    """
    Merge two sorted linked lists into one sorted list.

    Time Complexity: O(n + m) where n, m are list lengths
    Space Complexity: O(1)
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

    # Attach remaining nodes
    current.next = l1 or l2
    return dummy.next


# Expose main function as default (using heap approach as primary)
merge_k_lists = merge_k_lists_heap
