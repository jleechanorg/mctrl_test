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
- The sum of lists[i].length will not exceed 10^4

Time Complexity: O(N log k) where N is total number of nodes, k is number of lists
Space Complexity: O(k) for the heap (or O(k) for the result if counting output)
"""

from __future__ import annotations
import heapq
from typing import Optional, List


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional[ListNode] = None):
        self.val = val
        self.next = next


def merge_k_lists(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using a min-heap.

    Algorithm:
    1. Initialize a min-heap
    2. Push the first node from each list into the heap (along with list index to break ties)
    3. Pop from heap, add to result, push the next node from that list
    4. Continue until heap is empty

    Args:
        lists: List of sorted linked lists

    Returns:
        The merged sorted linked list
    """
    # Dummy head to simplify edge cases
    dummy = ListNode(0)
    current = dummy

    # Min-heap: (value, list_index, node)
    # list_index is used to break ties when values are equal
    heap: List[tuple[int, int, ListNode]] = []

    # Push the first node from each non-empty list into the heap
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    # Process nodes from heap until empty
    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        # Push next node from the same list
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def list_to_linkedlist(arr: List[int]) -> Optional[ListNode]:
    """Convert a Python list to a linked list."""
    if not arr:
        return None
    dummy = ListNode(0)
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


if __name__ == "__main__":
    # Test Case 1: Multiple lists with interleaved elements
    lists = [
        list_to_linkedlist([1, 4, 5]),
        list_to_linkedlist([1, 3, 4]),
        list_to_linkedlist([2, 6]),
    ]
    result = merge_k_lists(lists)
    print(f"Test 1: {linkedlist_to_list(result)}")
    assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6], "Test 1 failed"

    # Test Case 2: Empty list of lists
    lists = []
    result = merge_k_lists(lists)
    print(f"Test 2: {linkedlist_to_list(result)}")
    assert linkedlist_to_list(result) == [], "Test 2 failed"

    # Test Case 3: List containing empty lists
    lists = [list_to_linkedlist([])]
    result = merge_k_lists(lists)
    print(f"Test 3: {linkedlist_to_list(result)}")
    assert linkedlist_to_list(result) == [], "Test 3 failed"

    # Test Case 4: Single list
    lists = [list_to_linkedlist([1, 2, 3])]
    result = merge_k_lists(lists)
    print(f"Test 4: {linkedlist_to_list(result)}")
    assert linkedlist_to_list(result) == [1, 2, 3], "Test 4 failed"

    # Test Case 5: Lists with negative numbers
    lists = [
        list_to_linkedlist([-5, -3, 0, 4]),
        list_to_linkedlist([-2, -1, 5]),
        list_to_linkedlist([-10, -1]),
    ]
    result = merge_k_lists(lists)
    print(f"Test 5: {linkedlist_to_list(result)}")
    assert linkedlist_to_list(result) == [-10, -5, -3, -2, -1, -1, 0, 4, 5], "Test 5 failed"

    print("All tests passed!")
