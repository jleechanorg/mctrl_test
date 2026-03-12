"""
Merge k Sorted Lists - LeetCode #23 (Hard)

You are given an array of k linked-lists, each linked-list is sorted in ascending order.
Merge all the linked-lists into one sorted linked-list and return it.

Approach: Use a min-heap to always get the smallest element among all lists.
- Push the first node from each list into the heap (with value, list index, node)
- Repeatedly pop the smallest, add it to result, and push the next node from that list
- Continue until heap is empty

Time Complexity: O(N log k) where N = total nodes, k = number of lists
Space Complexity: O(k) for the heap + O(N) for the result list
"""
from __future__ import annotations

import heapq
from typing import Optional


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional[ListNode] = None):
        self.val = val
        self.next = next

    def __lt__(self, other: "ListNode") -> bool:
        """Enable comparison for heapq based on node values."""
        return self.val < other.val


def merge_k_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists into one sorted linked list.

    Args:
        lists: List of sorted linked list heads (can be None/empty)

    Returns:
        Head of the merged sorted linked list

    Example:
        >>> l1 = ListNode(1, ListNode(4, ListNode(5)))
        >>> l2 = ListNode(1, ListNode(3, ListNode(4)))
        >>> l3 = ListNode(2, ListNode(6))
        >>> merged = merge_k_lists([l1, l2, l3])
        >>> # Result: 1 -> 1 -> 2 -> 3 -> 4 -> 4 -> 5 -> 6
    """
    # Handle edge cases: empty list or list with only None elements
    if not lists:
        return None

    # Filter out None lists and create heap with first node from each list
    heap: list[tuple[int, int, ListNode]] = []  # (value, list_index, node)

    for i, head in enumerate(lists):
        if head:
            # Use (val, index, node) tuple for heap - index breaks ties
            heapq.heappush(heap, (head.val, i, head))

    # Dummy head to simplify result construction
    dummy = ListNode(0)
    current = dummy

    while heap:
        val, i, node = heapq.heappop(heap)
        current.next = node
        current = current.next

        # Push next node from the same list if it exists
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def list_to_linkedlist(values: list[int]) -> Optional[ListNode]:
    """Convert a Python list to a linked list."""
    if not values:
        return None

    dummy = ListNode(0)
    current = dummy
    for val in values:
        current.next = ListNode(val)
        current = current.next

    return dummy.next


def linkedlist_to_list(head: Optional[ListNode]) -> list[int]:
    """Convert a linked list to a Python list for easy comparison."""
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result


def count_nodes(head: Optional[ListNode]) -> int:
    """
    Count the number of nodes in a linked list.

    Args:
        head: Head of the linked list

    Returns:
        Number of nodes in the list (0 for empty/None list)

    Example:
        >>> head = list_to_linkedlist([1, 2, 3])
        >>> count_nodes(head)
        3
    """
    count = 0
    while head:
        count += 1
        head = head.next
    return count


if __name__ == "__main__":
    # Example usage
    l1 = list_to_linkedlist([1, 4, 5])
    l2 = list_to_linkedlist([1, 3, 4])
    l3 = list_to_linkedlist([2, 6])

    merged = merge_k_lists([l1, l2, l3])
    print("Merged list:", linkedlist_to_list(merged))
