"""
LeetCode 23: Merge k Sorted Lists

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
                  merging them into one sorted list:
                  1->1->2->3->4->4->5->6

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
    - Using heap: O(N log k) where N is total number of nodes, k is number of lists
    - Alternative divide-and-conquer: O(N log k)
    - Both achieve optimal time complexity

Space Complexity:
    - Heap approach: O(k) for the heap
    - Divide-and-conquer: O(1) extra space (excluding recursion stack)
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

    def __lt__(self, other: 'ListNode') -> bool:
        """Required for heapq to compare ListNode objects."""
        return self.val < other.val


def merge_k_lists_heap(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using a min-heap.

    This approach uses a min-heap to always get the smallest element
    among the current heads of all k lists in O(log k) time.

    Args:
        lists: List of sorted linked lists

    Returns:
        The merged sorted linked list

    Time Complexity: O(N log k) where N is total nodes, k is number of lists
    Space Complexity: O(k) for the heap
    """
    # Initialize a dummy head for the result list
    dummy = ListNode(0)
    current = dummy

    # Create a min-heap with (value, list_index, node) tuples
    # We include list_index to handle duplicate values correctly
    heap = []

    # Push the first node from each non-empty list into the heap
    for i, node in enumerate(lists):
        if node:
            # Use (val, index, node) to ensure proper comparison
            heapq.heappush(heap, (node.val, i, node))

    # Extract minimum, add to result, push next node from same list
    while heap:
        val, idx, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        # Push the next node from this list if it exists
        if node.next:
            heapq.heappush(heap, (node.next.val, idx, node.next))

    return dummy.next


def merge_k_lists_divide_conquer(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer.

    This approach repeatedly pairs and merges lists, similar to merge sort.
    At each level, we merge pairs of lists - each merge takes O(n) time
    and we do this log(k) times.

    Args:
        lists: List of sorted linked lists

    Returns:
        The merged sorted linked list

    Time Complexity: O(N log k)
    Space Complexity: O(log k) for recursion stack
    """
    if not lists:
        return None

    # Filter out empty lists (both None and empty linked lists)
    non_empty = [lst for lst in lists if lst is not None]
    if not non_empty:
        return None
    if len(non_empty) == 1:
        return non_empty[0]

    # Merge pairs iteratively
    while len(non_empty) > 1:
        merged_lists = []

        # Merge pairs of lists
        for i in range(0, len(non_empty) - 1, 2):
            merged = merge_two_lists(non_empty[i], non_empty[i + 1])
            merged_lists.append(merged)

        # If odd number of lists, add the last one
        if len(non_empty) % 2 == 1:
            merged_lists.append(non_empty[-1])

        non_empty = merged_lists

    return non_empty[0]


def merge_two_lists(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    """
    Merge two sorted linked lists into one sorted linked list.

    Time Complexity: O(n + m) where n, m are lengths of the two lists
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
