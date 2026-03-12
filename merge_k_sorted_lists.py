"""LeetCode 23: Merge k Sorted Lists (Hard)

Merge k sorted linked lists into one sorted linked list.
Uses a min-heap for O(N log k) time complexity.
"""

import heapq
from typing import List, Optional


class ListNode:
    def __init__(self, val: int = 0, next: Optional["ListNode"] = None):
        self.val = val
        self.next = next

    def __lt__(self, other: "ListNode") -> bool:
        return self.val < other.val

    def __repr__(self) -> str:
        vals = []
        node = self
        while node:
            vals.append(str(node.val))
            node = node.next
        return " -> ".join(vals)


def merge_k_lists(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """Merge k sorted linked lists using a min-heap.

    Time:  O(N log k) where N is total number of nodes, k is number of lists
    Space: O(k) for the heap
    """
    heap: list[ListNode] = []
    for head in lists:
        if head:
            heapq.heappush(heap, head)

    dummy = ListNode(0)
    current = dummy

    while heap:
        node = heapq.heappop(heap)
        current.next = node
        current = current.next
        if node.next:
            heapq.heappush(heap, node.next)

    return dummy.next
