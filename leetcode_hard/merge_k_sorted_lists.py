import heapq
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ListNode:
    val: int
    next: Optional["ListNode"] = None


def merge_k_lists(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """LeetCode 23: Merge k sorted linked lists using a min-heap."""
    heap = []
    for idx, node in enumerate(lists):
        if node is not None:
            heapq.heappush(heap, (node.val, idx, node))

    dummy = ListNode(0)
    tail = dummy

    while heap:
        _, idx, node = heapq.heappop(heap)
        tail.next = node
        tail = tail.next
        if node.next is not None:
            heapq.heappush(heap, (node.next.val, idx, node.next))

    tail.next = None
    return dummy.next
