from __future__ import annotations

import heapq
from typing import Optional


class ListNode:
    """Singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional["ListNode"] = None):
        self.val = val
        self.next = next


def merge_k_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    """Merge k sorted linked lists into one sorted linked list.

    Uses a min-heap of size k for O(N log k) time, O(k) space.
    """
    heap: list[tuple[int, int, ListNode]] = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    dummy = ListNode()
    tail = dummy

    while heap:
        val, idx, node = heapq.heappop(heap)
        tail.next = node
        tail = tail.next
        if node.next:
            heapq.heappush(heap, (node.next.val, idx, node.next))

    return dummy.next


# --------------- helpers ---------------

def build_list(vals: list[int]) -> Optional[ListNode]:
    """Create a linked list from a Python list."""
    dummy = ListNode()
    cur = dummy
    for v in vals:
        cur.next = ListNode(v)
        cur = cur.next
    return dummy.next


def to_list(head: Optional[ListNode]) -> list[int]:
    """Flatten a linked list to a Python list."""
    out: list[int] = []
    while head:
        out.append(head.val)
        head = head.next
    return out
