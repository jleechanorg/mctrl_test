"""
Merge k Sorted Lists - LeetCode #23 (Hard)

You are given an array of k linked-lists, each linked-list is sorted in ascending order.

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
    - Approach 1 (Merge one by one): O(k * n) where k = number of lists, n = total elements
    - Approach 2 (Divide and Conquer): O(n log k) - optimal
    - Approach 3 (Heap/Priority Queue): O(n log k)

Space Complexity:
    - Approach 1: O(1) extra space
    - Approach 2: O(log k) recursion stack
    - Approach 3: O(k) for heap

We implement the Heap approach as it's intuitive and optimal.
"""
from __future__ import annotations

import heapq
from typing import List, Optional


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional[ListNode] = None):
        self.val = val
        self.next = next

    def __repr__(self) -> str:
        return f"ListNode({self.val})"

    def __lt__(self, other: "ListNode") -> bool:
        """Required for heapq comparison."""
        return self.val < other.val


def merge_k_lists_heap(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using a min-heap.

    Args:
        lists: List of sorted linked list heads (can be None or empty)

    Returns:
        Head of the merged sorted linked list

    Time Complexity: O(n log k) where n = total elements, k = number of lists
    Space Complexity: O(k) for the heap
    """
    # Create a dummy head to simplify edge cases
    dummy = ListNode(-1)
    current = dummy

    # Initialize min-heap with first node from each list
    # heapq is a min-heap, stores (value, list_index, node)
    # list_index breaks ties when values are equal
    heap = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    # Extract minimum and add next node from same list
    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_lists_divide_conquer(
    lists: List[Optional[ListNode]]
) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer.

    Args:
        lists: List of sorted linked list heads (can be None or empty)

    Returns:
        Head of the merged sorted linked list

    Time Complexity: O(n log k) - optimal
    Space Complexity: O(log k) for recursion stack
    """
    if not lists:
        return None
    if len(lists) == 1:
        return lists[0]

    # Helper to merge two sorted lists
    def merge_two(a: Optional[ListNode], b: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode(-1)
        curr = dummy
        while a and b:
            if a.val <= b.val:
                curr.next = a
                a = a.next
            else:
                curr.next = b
                b = b.next
            curr = curr.next
        curr.next = a or b
        return dummy.next

    # Divide and conquer: repeatedly merge pairs
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


# Helper functions for testing
def list_to_linkedlist(values: List[int]) -> Optional[ListNode]:
    """Convert a Python list to a linked list."""
    if not values:
        return None
    dummy = ListNode(-1)
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


# Main solution to expose
merge_k_lists = merge_k_lists_heap


if __name__ == "__main__":
    # Example 1
    lists = [
        list_to_linkedlist([1, 4, 5]),
        list_to_linkedlist([1, 3, 4]),
        list_to_linkedlist([2, 6]),
    ]
    result = merge_k_lists(lists)
    print(linkedlist_to_list(result))  # [1, 1, 2, 3, 4, 4, 5, 6]

    # Example 2
    lists = []
    result = merge_k_lists(lists)
    print(linkedlist_to_list(result))  # []

    # Example 3
    lists = [None]
    result = merge_k_lists(lists)
    print(linkedlist_to_list(result))  # []
