from __future__ import annotations

from heapq import heappush, heappop
from typing import Optional


class ListNode:
    """Definition for singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional["ListNode"] = None):
        self.val = val
        self.next = next

    def __repr__(self) -> str:
        return f"ListNode({self.val})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ListNode):
            return NotImplemented
        return self.to_list() == other.to_list()

    def to_list(self) -> list[int]:
        """Convert linked list to Python list for easy comparison."""
        result = []
        node = self
        while node:
            result.append(node.val)
            node = node.next
        return result


def merge_k_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists and return it as one sorted list.

    Uses a min-heap to efficiently get the smallest element across all lists.
    Time complexity: O(N log k) where N is total nodes, k is number of lists
    Space complexity: O(k) for the heap

    Args:
        lists: List of sorted linked lists

    Returns:
        The merged sorted linked list
    """
    # Dummy node to simplify edge cases
    dummy = ListNode(0)
    current = dummy

    # Min-heap: (value, list_index, node)
    # list_index breaks ties when values are equal
    heap: list[tuple[int, int, ListNode]] = []

    # Initialize heap with first node from each non-empty list
    for i, head in enumerate(lists):
        if head:
            heappush(heap, (head.val, i, head))

    # Process nodes from heap until empty
    while heap:
        val, i, node = heappop(heap)
        current.next = node
        current = current.next

        # If there's a next node in this list, add it to heap
        if node.next:
            heappush(heap, (node.next.val, i, node.next))

    return dummy.next


def list_to_linked(arr: list[int]) -> Optional[ListNode]:
    """Convert a Python list to a linked list."""
    if not arr:
        return None
    dummy = ListNode(0)
    current = dummy
    for val in arr:
        current.next = ListNode(val)
        current = current.next
    return dummy.next
