"""
LeetCode Hard: Merge k Sorted Lists

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
"""

from __future__ import annotations
from typing import Optional, List
import heapq


class ListNode:
    """Definition for singly-linked list node."""
    def __init__(self, val: int = 0, next: Optional[ListNode] = None):
        self.val = val
        self.next = next

    def __lt__(self, other: 'ListNode') -> bool:
        return self.val < other.val


class Solution:
    """
    Merge k sorted linked lists using a min-heap.

    Time Complexity: O(N log k) where N is total nodes, k is number of lists
    Space Complexity: O(k) for the heap
    """

    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
        """
        Merge k sorted linked lists into one sorted linked list.

        Args:
            lists: List of sorted linked list heads

        Returns:
            Head of merged sorted linked list
        """
        # Min-heap to store (value, list_index, node)
        heap: List[tuple] = []

        # Initialize heap with first node from each non-empty list
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


def list_to_linkedlist(arr: List[int]) -> Optional[ListNode]:
    """Convert Python list to linked list."""
    if not arr:
        return None
    dummy = ListNode(0)
    current = dummy
    for val in arr:
        current.next = ListNode(val)
        current = current.next
    return dummy.next


def linkedlist_to_list(node: Optional[ListNode]) -> List[int]:
    """Convert linked list to Python list."""
    result = []
    while node:
        result.append(node.val)
        node = node.next
    return result


def test_merge_k_lists():
    """Test cases for mergeKLists."""
    solution = Solution()

    # Test case 1
    lists = [
        list_to_linkedlist([1, 4, 5]),
        list_to_linkedlist([1, 3, 4]),
        list_to_linkedlist([2, 6])
    ]
    result = solution.mergeKLists(lists)
    expected = [1, 1, 2, 3, 4, 4, 5, 6]
    assert linkedlist_to_list(result) == expected, f"Test 1 failed: {linkedlist_to_list(result)}"
    print(f"Test 1 passed: {expected}")

    # Test case 2: Empty list
    lists = []
    result = solution.mergeKLists(lists)
    assert linkedlist_to_list(result) == [], "Test 2 failed"
    print("Test 2 passed: []")

    # Test case 3: List with empty lists
    lists = [[]]
    result = solution.mergeKLists([list_to_linkedlist(l) for l in lists])
    assert linkedlist_to_list(result) == [], "Test 3 failed"
    print("Test 3 passed: []")

    # Test case 4: Single list
    lists = [list_to_linkedlist([1, 2, 3])]
    result = solution.mergeKLists(lists)
    assert linkedlist_to_list(result) == [1, 2, 3], "Test 4 failed"
    print("Test 4 passed: [1, 2, 3]")

    # Test case 5: Two lists
    lists = [
        list_to_linkedlist([1, 3, 5]),
        list_to_linkedlist([2, 4, 6])
    ]
    result = solution.mergeKLists(lists)
    expected = [1, 2, 3, 4, 5, 6]
    assert linkedlist_to_list(result) == expected, f"Test 5 failed: {linkedlist_to_list(result)}"
    print(f"Test 5 passed: {expected}")

    # Test case 6: Negative numbers
    lists = [
        list_to_linkedlist([-5, -3, 0]),
        list_to_linkedlist([-2, -1, 1])
    ]
    result = solution.mergeKLists(lists)
    expected = [-5, -3, -2, -1, 0, 1]
    assert linkedlist_to_list(result) == expected, f"Test 6 failed: {linkedlist_to_list(result)}"
    print(f"Test 6 passed: {expected}")

    print("\nAll tests passed!")


if __name__ == "__main__":
    test_merge_k_lists()
