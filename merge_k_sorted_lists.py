"""
Merge k Sorted Lists - LeetCode Hard Problem

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
    * k == lists.length
    * 0 <= k <= 10^4
    * 0 <= lists[i].length <= 500
    * -10^4 <= lists[i][j] <= 10^4
    * lists[i] is sorted in ascending order.
    * The sum of lists[i].length will not exceed 10^4.
"""
from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Optional


@dataclass
class ListNode:
    """Definition for singly-linked list node."""
    val: int = 0
    next: Optional['ListNode'] = None


def merge_k_lists_heap(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using a min-heap.

    Time Complexity: O(N log k) where N is total number of nodes
                     - Each node is pushed/popped from heap once: O(N log k)
    Space Complexity: O(k) for the heap + O(k) for the dummy node
                     = O(k) auxiliary space

    Args:
        lists: List of sorted linked lists

    Returns:
        The head of the merged sorted linked list

    Example:
        >>> l1 = ListNode(1, ListNode(4, ListNode(5)))
        >>> l2 = ListNode(1, ListNode(3, ListNode(4)))
        >>> l3 = ListNode(2, ListNode(6))
        >>> result = merge_k_lists_heap([l1, l2, l3])
        >>> # Returns merged list: 1->1->2->3->4->4->5->6
    """
    # Initialize a min-heap with (value, list_index, node)
    # list_index is used to break ties when values are equal
    heap: list[tuple[int, int, ListNode]] = []

    # Push the first node from each non-empty list into the heap
    for i, node in enumerate(lists):
        if node:
            # (value, list_index, node)
            heapq.heappush(heap, (node.val, i, node))

    # Dummy head to simplify edge cases
    dummy = ListNode(0)
    current = dummy

    # Extract minimum and add next node from same list
    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        # Push the next node from the same list if it exists
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_lists_divide_conquer(
    lists: list[Optional[ListNode]]
) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer.

    Time Complexity: O(N log k)
                     - Each level processes all N nodes
                     - There are log k levels
    Space Complexity: O(1) if we modify in-place (excluding recursion stack)
                     O(log k) for recursion stack

    This approach pairs up lists and merges them recursively.
    It's more efficient in practice as it avoids heap overhead.

    Args:
        lists: List of sorted linked lists

    Returns:
        The head of the merged sorted linked list

    Example:
        >>> l1 = ListNode(1, ListNode(4, ListNode(5)))
        >>> l2 = ListNode(1, ListNode(3, ListNode(4)))
        >>> l3 = ListNode(2, ListNode(6))
        >>> result = merge_k_lists_divide_conquer([l1, l2, l3])
        >>> # Returns merged list: 1->1->2->3->4->4->5->6
    """
    if not lists:
        return None

    def merge_two_lists(
        l1: Optional[ListNode],
        l2: Optional[ListNode]
    ) -> Optional[ListNode]:
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
        current.next = l1 if l1 else l2
        return dummy.next

    # Repeatedly merge pairs of lists until one remains
    while len(lists) > 1:
        new_lists = []

        # Merge pairs: (0,1), (2,3), (4,5), ...
        for i in range(0, len(lists) - 1, 2):
            merged = merge_two_lists(lists[i], lists[i + 1])
            new_lists.append(merged)

        # If there's an odd list at the end, carry it over
        if len(lists) % 2 == 1:
            new_lists.append(lists[-1])

        lists = new_lists

    return lists[0] if lists else None


def list_to_linked_list(arr: list[int]) -> Optional[ListNode]:
    """Convert a Python list to a linked list."""
    if not arr:
        return None

    dummy = ListNode(0)
    current = dummy
    for val in arr:
        current.next = ListNode(val)
        current = current.next

    return dummy.next


def linked_list_to_list(node: Optional[ListNode]) -> list[int]:
    """Convert a linked list to a Python list."""
    result = []
    while node:
        result.append(node.val)
        node = node.next
    return result


# Primary export - heap-based solution (more intuitive)
merge_k_lists = merge_k_lists_heap


if __name__ == "__main__":
    # Example 1
    l1 = list_to_linked_list([1, 4, 5])
    l2 = list_to_linked_list([1, 3, 4])
    l3 = list_to_linked_list([2, 6])

    result = merge_k_lists([l1, l2, l3])
    print(linked_list_to_list(result))  # [1, 1, 2, 3, 4, 4, 5, 6]

    # Example 2: Empty list
    result = merge_k_lists([])
    print(linked_list_to_list(result))  # []

    # Example 3: List with empty list
    result = merge_k_lists([[]])
    print(linked_list_to_list(result))  # []
