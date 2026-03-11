"""LeetCode #23 - Merge k Sorted Lists (Hard)

You are given an array of k linked-lists lists, each linked-list is sorted
in ascending order. Merge all the linked-lists into one sorted linked-list
and return it.

Time complexity: O(N log k) where N is total number of nodes.
"""
from __future__ import annotations

import heapq


class ListNode:
    def __init__(self, val: int = 0, next_node: ListNode | None = None) -> None:
        self.val = val
        self.next = next_node

    def __repr__(self) -> str:
        vals = []
        node: ListNode | None = self
        while node:
            vals.append(str(node.val))
            node = node.next
        return " -> ".join(vals)


def list_to_linked(values: list[int]) -> ListNode | None:
    """Helper: convert a Python list to a linked list."""
    dummy = ListNode(0)
    curr = dummy
    for v in values:
        curr.next = ListNode(v)
        curr = curr.next
    return dummy.next


def linked_to_list(head: ListNode | None) -> list[int]:
    """Helper: convert a linked list to a Python list."""
    result: list[int] = []
    while head:
        result.append(head.val)
        head = head.next
    return result


def merge_k_lists(lists: list[ListNode | None]) -> ListNode | None:
    heap: list[tuple[int, int, ListNode]] = []
    for idx, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, idx, node))

    dummy = ListNode(0)
    curr = dummy
    counter = len(lists)  # unique tiebreaker

    while heap:
        val, _, node = heapq.heappop(heap)
        curr.next = ListNode(val)
        curr = curr.next
        if node.next:
            counter += 1
            heapq.heappush(heap, (node.next.val, counter, node.next))

    return dummy.next
