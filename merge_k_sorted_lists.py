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

Solution Approaches:
1. Brute Force: Collect all values, sort, rebuild list - O(N log N)
2. Merge One by One: Merge lists sequentially - O(N * k)
3. Divide and Conquer: Pairwise merging - O(N log k)
4. Heap/Min-Heap: Use min-heap to always pick smallest - O(N log k)

We implement the Divide and Conquer approach for optimal time complexity.
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
        """Convert linked list to Python list for easy comparison."""
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


def merge_two_lists(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    """
    Merge two sorted linked lists into one sorted list.

    Time Complexity: O(n + m) where n and m are lengths of the two lists
    Space Complexity: O(1) - only pointer manipulation
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


def merge_k_lists_divide_conquer(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted lists using divide and conquer (pairwise merging).

    Time Complexity: O(N log k) where N is total elements, k is number of lists
    Space Complexity: O(log k) for recursion stack

    Strategy:
    - If empty list, return None
    - If only one list, return it
    - Split lists in half, recursively merge each half, then merge the two results
    """
    if not lists:
        return None

    # Base case: only one list
    if len(lists) == 1:
        return lists[0]

    # Divide: split into two halves
    mid = len(lists) // 2
    left = merge_k_lists_divide_conquer(lists[:mid])
    right = merge_k_lists_divide_conquer(lists[mid:])

    # Conquer: merge the two results
    return merge_two_lists(left, right)


def merge_k_lists_heap(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted lists using a min-heap.

    Time Complexity: O(N log k) where N is total elements, k is number of lists
    Space Complexity: O(k) for the heap

    Strategy:
    - Push first node from each list into min-heap (with value, list index, node)
    - Always pop the smallest, add to result, push next node from same list
    - Continue until heap is empty
    """
    # Handle empty input
    if not lists:
        return None

    # Initialize heap with first node from each non-empty list
    heap = []
    for i, node in enumerate(lists):
        if node:
            # heapq is min-heap; use (val, list_index, node) tuple
            heapq.heappush(heap, (node.val, i, node))

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


# Export main solution - using divide and conquer as primary
merge_k_lists = merge_k_lists_divide_conquer


if __name__ == "__main__":
    # Example usage
    lists = [
        ListNode.from_list([1, 4, 5]),
        ListNode.from_list([1, 3, 4]),
        ListNode.from_list([2, 6])
    ]
    result = merge_k_lists(lists)
    print(result.to_list() if result else [])  # [1, 1, 2, 3, 4, 4, 5, 6]

    # Test with empty lists
    empty_result = merge_k_lists([])
    print(empty_result.to_list() if empty_result else [])  # []

    # Test with single list
    single_result = merge_k_lists([ListNode.from_list([1, 2, 3])])
    print(single_result.to_list() if single_result else [])  # [1, 2, 3]
