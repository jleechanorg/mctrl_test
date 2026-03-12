"""
Merge k Sorted Lists - LeetCode Hard

Given an array of k linked-lists, each linked-list is sorted in ascending order.
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
    - Approach 1 (Merge one by one): O(k * n) where n is avg list length
    - Approach 2 (Divide and Conquer): O(N log k) where N is total elements
    - Approach 3 (Heap): O(N log k) where N is total elements

Space Complexity:
    - Approach 1: O(1) extra space
    - Approach 2: O(log k) for recursion stack
    - Approach 3: O(k) for heap
"""

from __future__ import annotations
from typing import Optional, List
import heapq


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

    def __repr__(self) -> str:
        return f"ListNode({self.val})"

    def to_list(self) -> List[int]:
        """Convert linked list to Python list for easy testing."""
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


def merge_k_lists_divide_conquer(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted lists using divide and conquer approach.

    Time Complexity: O(N log k) where N is total number of elements
    Space Complexity: O(log k) for recursion stack

    Strategy:
    - Pair up k lists and merge each pair recursively
    - Continue until we have only one list
    """
    if not lists:
        return None

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

        # Attach remaining nodes
        current.next = l1 or l2
        return dummy.next

    # Iteratively merge pairs of lists
    while len(lists) > 1:
        merged_lists = []
        for i in range(0, len(lists), 2):
            if i + 1 < len(lists):
                merged_lists.append(merge_two_lists(lists[i], lists[i + 1]))
            else:
                merged_lists.append(lists[i])
        lists = merged_lists

    return lists[0] if lists else None


def merge_k_lists_heap(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted lists using a min-heap.

    Time Complexity: O(N log k) where N is total number of elements
    Space Complexity: O(k) for the heap

    Strategy:
    - Use a min-heap to always get the smallest element
    - Push first element from each list into the heap
    - Pop smallest, push next from same list, repeat
    """
    if not lists:
        return None

    # Initialize heap with (value, list_index, node)
    heap = []
    for i, lst in enumerate(lists):
        if lst:
            # heapq is a min-heap, we use (val, list_idx, node) tuple
            heapq.heappush(heap, (lst.val, i, lst))

    dummy = ListNode(0)
    current = dummy

    while heap:
        val, list_idx, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        if node.next:
            heapq.heappush(heap, (node.next.val, list_idx, node.next))

    return dummy.next


# Alias for the main solution - using divide and conquer (most elegant)
merge_k_lists = merge_k_lists_divide_conquer


if __name__ == "__main__":
    # Test example 1
    lists = [
        ListNode.from_list([1, 4, 5]),
        ListNode.from_list([1, 3, 4]),
        ListNode.from_list([2, 6])
    ]
    result = merge_k_lists(lists)
    print(f"Example 1: {result.to_list()}")  # [1, 1, 2, 3, 4, 4, 5, 6]

    # Test example 2 (empty input)
    result = merge_k_lists([])
    print(f"Example 2: {result.to_list() if result else []}")  # []

    # Test example 3 (list with empty list)
    result = merge_k_lists([None])
    print(f"Example 3: {result.to_list() if result else []}")  # []
