"""
Merge k Sorted Lists - LeetCode Hard Problem

You are given an array of k linked-lists, each linked-list is sorted in ascending order.
Merge all the linked-lists into one sorted linked-list and return it.

Approach:
- Use a min-heap (priority queue) to always get the smallest element among all lists
- Time: O(N log k) where N is total number of nodes, k is number of lists
- Space: O(k) for the heap

Alternative approach (divide and conquer):
- Pairwise merging: O(N log k) time, O(1) extra space
"""
from __future__ import annotations

import heapq
from typing import Optional


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

    def __lt__(self, other: 'ListNode') -> bool:
        """Enable comparison for heapq."""
        return self.val < other.val


def merge_k_lists_heap(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using a min-heap.

    Args:
        lists: List of head nodes of sorted linked lists

    Returns:
        Head of the merged sorted linked list

    Time Complexity: O(N log k) where N = total nodes, k = number of lists
    Space Complexity: O(k) for the heap
    """
    # Dummy node to simplify edge cases
    dummy = ListNode()
    current = dummy

    # Min-heap: (value, list_index, node)
    # list_index ensures stable ordering when values are equal
    heap: list[tuple[int, int, ListNode]] = []

    # Initialize heap with first node from each non-empty list
    for i, head in enumerate(lists):
        if head:
            heapq.heappush(heap, (head.val, i, head))

    # Extract min, add to result, push next from same list
    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def merge_k_lists_divide_conquer(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer (pairwise merging).

    Args:
        lists: List of head nodes of sorted linked lists

    Returns:
        Head of the merged sorted linked list

    Time Complexity: O(N log k)
    Space Complexity: O(log k) for recursion stack (or O(1) with iteration)
    """
    if not lists:
        return None

    def merge_two(a: Optional[ListNode], b: Optional[ListNode]) -> Optional[ListNode]:
        """Merge two sorted linked lists."""
        if not a:
            return b
        if not b:
            return a

        dummy = ListNode()
        current = dummy

        while a and b:
            if a.val <= b.val:
                current.next = a
                a = a.next
            else:
                current.next = b
                b = b.next
            current = current.next

        current.next = a if a else b
        return dummy.next

    # Repeatedly merge adjacent pairs until one list remains
    while len(lists) > 1:
        merged = []
        for i in range(0, len(lists), 2):
            l1 = lists[i]
            l2 = lists[i + 1] if i + 1 < len(lists) else None
            merged.append(merge_two(l1, l2))
        lists = merged

    return lists[0] if lists else None


# Convenience function to create linked list from list
def create_linked_list(values: list[int]) -> Optional[ListNode]:
    """Create a linked list from a list of values."""
    if not values:
        return None
    dummy = ListNode()
    current = dummy
    for val in values:
        current.next = ListNode(val)
        current = current.next
    return dummy.next


# Convenience function to convert linked list to list
def linked_list_to_list(node: Optional[ListNode]) -> list[int]:
    """Convert a linked list to a Python list."""
    result = []
    while node:
        result.append(node.val)
        node = node.next
    return result


if __name__ == "__main__":
    # Example usage
    list1 = create_linked_list([1, 4, 5])
    list2 = create_linked_list([1, 3, 4])
    list3 = create_linked_list([2, 6])

    lists = [list1, list2, list3]
    merged = merge_k_lists_heap(lists)
    print("Heap result:", linked_list_to_list(merged))

    lists = [create_linked_list([1, 4, 5]), create_linked_list([1, 3, 4]), create_linked_list([2, 6])]
    merged = merge_k_lists_divide_conquer(lists)
    print("Divide-conquer result:", linked_list_to_list(merged))
