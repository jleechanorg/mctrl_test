"""
Merge k Sorted Lists - LeetCode Hard

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
        node = self
        while node:
            result.append(node.val)
            node = node.next
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


def merge_k_lists_heap(nums: List[List[int]]) -> List[int]:
    """
    Merge k sorted arrays using a min-heap.

    Time Complexity: O(N log k) where N is total elements, k is number of lists
    Space Complexity: O(k) for the heap

    Args:
        nums: List of sorted lists (using arrays for simplicity)

    Returns:
        Merged sorted list
    """
    if not nums:
        return []

    # Filter out empty lists
    heap = []

    # Add first element from each non-empty list to heap
    for i, lst in enumerate(nums):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))

    result = []

    while heap:
        val, list_idx, elem_idx = heapq.heappop(heap)
        result.append(val)

        # If there are more elements in this list, add next element
        if elem_idx + 1 < len(nums[list_idx]):
            next_val = nums[list_idx][elem_idx + 1]
            heapq.heappush(heap, (next_val, list_idx, elem_idx + 1))

    return result


def merge_k_lists_linkedlists(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked-lists using a min-heap with O(k) space.

    Time Complexity: O(N log k) where N is total elements, k is number of lists
    Space Complexity: O(k) for the heap + O(1) for result list

    This is the classic heap-based solution that works directly with linked lists.

    Args:
        lists: List of sorted linked-list heads

    Returns:
        Head of merged sorted linked list
    """
    if not lists:
        return None

    # Filter out empty lists and add to heap
    heap = []
    for i, node in enumerate(lists):
        if node:
            # Push (value, list_index, node) to break ties
            heapq.heappush(heap, (node.val, i, node))

    dummy = ListNode(0)
    current = dummy

    while heap:
        val, _, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        # Add next node from the same list
        if node.next:
            heapq.heappush(heap, (node.next.val, id(node.next), node.next))

    return dummy.next


def merge_k_lists_divide_conquer(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked-lists using divide and conquer.

    Time Complexity: O(N log k)
    Space Complexity: O(log k) for recursion stack

    This approach pairs up lists and merges them recursively, which is
    more cache-friendly and avoids heap overhead.

    Args:
        lists: List of sorted linked-list heads

    Returns:
        Head of merged sorted linked list
    """
    if not lists:
        return None

    def merge_two(a: Optional[ListNode], b: Optional[ListNode]) -> Optional[ListNode]:
        """Merge two sorted linked lists."""
        if not a:
            return b
        if not b:
            return a

        dummy = ListNode(0)
        current = dummy

        while a and b:
            if a.val <= b.val:
                current.next = a
                a = a.next
            else:
                current.next = b
                b = b.next
            current = current.next

        current.next = a or b
        return dummy.next

    # Repeatedly merge pairs until one list remains
    n = len(lists)

    # Work on a copy to not modify original
    working = lists[:]

    while n > 1:
        new_n = 0
        i = 0
        while i < n:
            # Merge pairs with interval distance
            if i + 1 < n:
                merged = merge_two(working[i], working[i + 1])
                working[new_n] = merged
                new_n += 1
                i += 2
            else:
                # Odd one out, just carry it forward
                working[new_n] = working[i]
                new_n += 1
                i += 1
        n = new_n

    return working[0]


# ==================== For LeetCode submission ====================

class Solution:
    """LeetCode solution class for merge-k-sorted-lists."""

    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
        """
        Merge k sorted linked-lists into one sorted list.

        Uses heap-based approach with O(N log k) time complexity.

        Args:
            lists: List of sorted linked-list heads

        Returns:
            Head of merged sorted linked list
        """
        return merge_k_lists_linkedlists(lists)


if __name__ == "__main__":
    # Test with sample input
    lists = [
        ListNode.from_list([1, 4, 5]),
        ListNode.from_list([1, 3, 4]),
        ListNode.from_list([2, 6])
    ]

    result = merge_k_lists_linkedlists(lists)
    print("Result:", result.to_list() if result else [])

    # Test with divide and conquer
    lists2 = [
        ListNode.from_list([1, 4, 5]),
        ListNode.from_list([1, 3, 4]),
        ListNode.from_list([2, 6])
    ]
    result2 = merge_k_lists_divide_conquer(lists2)
    print("Result (divide conquer):", result2.to_list() if result2 else [])

    # Test with empty lists
    result3 = merge_k_lists_linkedlists([])
    print("Empty result:", result3.to_list() if result3 else [])

    # Test with arrays (heap-based)
    arrays = [[1, 4, 5], [1, 3, 4], [2, 6]]
    result4 = merge_k_lists_heap(arrays)
    print("Array result:", result4)
