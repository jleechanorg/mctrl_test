"""Tests for LeetCode 23: Merge k Sorted Lists."""

import pytest
from merge_k_sorted_lists import ListNode, merge_k_lists


def build_list(vals):
    """Helper: build a linked list from a Python list."""
    dummy = ListNode(0)
    curr = dummy
    for v in vals:
        curr.next = ListNode(v)
        curr = curr.next
    return dummy.next


def to_list(head):
    """Helper: convert linked list to Python list."""
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result


class TestMergeKLists:
    def test_example_case(self):
        # [[1,4,5],[1,3,4],[2,6]]
        lists = [build_list([1, 4, 5]), build_list([1, 3, 4]), build_list([2, 6])]
        assert to_list(merge_k_lists(lists)) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_input(self):
        assert merge_k_lists([]) is None

    def test_all_none_lists(self):
        assert merge_k_lists([None, None]) is None

    def test_single_list(self):
        lists = [build_list([1, 2, 3])]
        assert to_list(merge_k_lists(lists)) == [1, 2, 3]

    def test_single_element_lists(self):
        lists = [build_list([5]), build_list([1]), build_list([3])]
        assert to_list(merge_k_lists(lists)) == [1, 3, 5]

    def test_duplicates(self):
        lists = [build_list([1, 1, 1]), build_list([1, 1])]
        assert to_list(merge_k_lists(lists)) == [1, 1, 1, 1, 1]

    def test_negative_values(self):
        lists = [build_list([-3, -1, 2]), build_list([-2, 0, 4])]
        assert to_list(merge_k_lists(lists)) == [-3, -2, -1, 0, 2, 4]

    def test_mixed_lengths(self):
        lists = [build_list([1]), build_list([2, 3, 4, 5, 6]), build_list([3, 7])]
        assert to_list(merge_k_lists(lists)) == [1, 2, 3, 3, 4, 5, 6, 7]

    def test_some_none_lists(self):
        lists = [None, build_list([1, 3]), None, build_list([2, 4])]
        assert to_list(merge_k_lists(lists)) == [1, 2, 3, 4]

    def test_large_k(self):
        lists = [build_list([i]) for i in range(100, 0, -1)]
        result = to_list(merge_k_lists(lists))
        assert result == list(range(1, 101))


class TestListNode:
    def test_repr(self):
        node = build_list([1, 2, 3])
        assert repr(node) == "1 -> 2 -> 3"

    def test_comparison(self):
        a = ListNode(1)
        b = ListNode(2)
        assert a < b
