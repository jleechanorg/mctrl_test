from __future__ import annotations

from heapq import heappush, heappop
from typing import Optional


class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

    def __repr__(self):
        return f"ListNode({self.val})"

    def __eq__(self, other):
        if not isinstance(other, ListNode):
            return False
        return self.to_list() == other.to_list()

    def to_list(self) -> list[int]:
        result = []
        node = self
        while node:
            result.append(node.val)
            node = node.next
        return result

    @classmethod
    def from_list(cls, values: list[int]) -> Optional['ListNode']:
        if not values:
            return None
        dummy = cls(0)
        current = dummy
        for val in values:
            current.next = cls(val)
            current = current.next
        return dummy.next


def merge_k_sorted_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Merge k sorted linked lists into one sorted linked list.

    Uses a min-heap for O(N log k) time complexity where N is total nodes
    and k is the number of lists.

    Args:
        lists: List of sorted linked list heads (may contain None values)

    Returns:
        Head of the merged sorted linked list
    """
    # Min-heap stores (value, list_index, node) tuples
    # list_index breaks ties to avoid comparison issues
    heap: list[tuple[int, int, ListNode]] = []

    # Initialize heap with first node from each non-empty list
    for idx, head in enumerate(lists):
        if head:
            heappush(heap, (head.val, idx, head))

    dummy = ListNode(0)
    current = dummy

    while heap:
        val, idx, node = heappop(heap)
        current.next = node
        current = current.next

        # If there's a next node in this list, add it to heap
        if node.next:
            heappush(heap, (node.next.val, idx, node.next))

    return dummy.next


def merge_k_sorted_lists_divide_conquer(
    lists: list[Optional[ListNode]]
) -> Optional[ListNode]:
    """
    Merge k sorted linked lists using divide and conquer approach.

    Time complexity: O(N log k)
    Space complexity: O(log k) for recursion stack
    """
    if not lists:
        return None

    # Filter out None values
    non_empty = [lst for lst in lists if lst]
    if not non_empty:
        return None

    while len(non_empty) > 1:
        next_level: list[Optional[ListNode]] = []

        for i in range(0, len(non_empty), 2):
            if i + 1 < len(non_empty):
                merged = _merge_two_lists(non_empty[i], non_empty[i + 1])
                next_level.append(merged)
            else:
                next_level.append(non_empty[i])

        non_empty = next_level

    return non_empty[0]


def _merge_two_lists(
    l1: Optional[ListNode], l2: Optional[ListNode]
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

    current.next = l1 or l2
    return dummy.next
