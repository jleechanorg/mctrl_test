from dataclasses import dataclass
from typing import Optional


@dataclass
class ListNode:
    val: int
    next: Optional["ListNode"] = None


def reverse_k_group(head: Optional[ListNode], k: int) -> Optional[ListNode]:
    """LeetCode 25: Reverse nodes in k-group in-place."""
    if head is None or k <= 1:
        return head

    dummy = ListNode(0, head)
    group_prev = dummy

    while True:
        kth = group_prev
        for _ in range(k):
            kth = kth.next
            if kth is None:
                return dummy.next

        group_next = kth.next

        prev = group_next
        curr = group_prev.next
        while curr is not group_next:
            nxt = curr.next
            curr.next = prev
            prev = curr
            curr = nxt

        old_group_start = group_prev.next
        group_prev.next = kth
        group_prev = old_group_start
