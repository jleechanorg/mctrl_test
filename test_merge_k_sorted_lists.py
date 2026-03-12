"""
Test suite for Merge k Sorted Lists solution.
"""

from __future__ import annotations

import pytest
from merge_k_sorted_lists import (
    ListNode,
    merge_k_lists,
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
    merge_two_lists,
)


class TestListNode:
    """Tests for ListNode helper class."""

    def test_from_list_empty(self):
        assert ListNode.from_list([]) is None

    def test_from_list_single(self):
        node = ListNode.from_list([1])
        assert node.val == 1
        assert node.next is None

    def test_from_list_multiple(self):
        node = ListNode.from_list([1, 2, 3])
        assert node.val == 1
        assert node.next.val == 2
        assert node.next.next.val == 3
        assert node.next.next.next is None

    def test_to_list_empty(self):
        # ListNode with val=0 and no next should give [0]
        assert ListNode(0).to_list() == [0]

    def test_to_list_multiple(self):
        node = ListNode.from_list([1, 2, 3])
        assert node.to_list() == [1, 2, 3]


class TestMergeTwoLists:
    """Tests for merging two sorted lists."""

    def test_merge_two_normal(self):
        l1 = ListNode.from_list([1, 2, 4])
        l2 = ListNode.from_list([1, 3, 4])
        result = merge_two_lists(l1, l2)
        assert result.to_list() == [1, 1, 2, 3, 4, 4]

    def test_merge_two_one_empty(self):
        l1 = ListNode.from_list([1, 2, 3])
        l2 = None
        result = merge_two_lists(l1, l2)
        assert result.to_list() == [1, 2, 3]

    def test_merge_two_both_empty(self):
        result = merge_two_lists(None, None)
        assert result is None

    def test_merge_two_different_lengths(self):
        l1 = ListNode.from_list([1, 3, 5, 7])
        l2 = ListNode.from_list([2, 4])
        result = merge_two_lists(l1, l2)
        assert result.to_list() == [1, 2, 3, 4, 5, 7]


class TestMergeKListsHeap:
    """Tests for heap-based k-way merge."""

    def test_example_1(self):
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_lists(self):
        lists = []
        result = merge_k_lists_heap(lists)
        assert result is None

    def test_single_empty_list(self):
        lists = [[]]
        result = merge_k_lists_heap([ListNode.from_list(l) for l in lists])
        assert result is None

    def test_single_list(self):
        lists = [ListNode.from_list([1, 2, 3])]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 2, 3]

    def test_two_lists(self):
        lists = [
            ListNode.from_list([1, 3, 5]),
            ListNode.from_list([2, 4, 6]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6]

    def test_all_same_values(self):
        lists = [
            ListNode.from_list([1, 1, 1]),
            ListNode.from_list([1, 1]),
            ListNode.from_list([1]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 1, 1, 1, 1, 1]

    def test_negative_values(self):
        lists = [
            ListNode.from_list([-3, -1, 2]),
            ListNode.from_list([-2, 0, 3]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [-3, -2, -1, 0, 2, 3]

    def test_already_sorted(self):
        lists = [
            ListNode.from_list([1, 2, 3]),
            ListNode.from_list([4, 5, 6]),
            ListNode.from_list([7, 8, 9]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_mixed_values(self):
        # Each list is sorted in ascending order, but lists have different ranges
        lists = [
            ListNode.from_list([1, 3, 5]),
            ListNode.from_list([2, 4, 6]),
            ListNode.from_list([0, 7, 8]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [0, 1, 2, 3, 4, 5, 6, 7, 8]

    def test_large_k(self):
        # k = 10 lists, each with 2 elements - sorted merged output
        lists = [ListNode.from_list([i, i + 10]) for i in range(10)]
        result = merge_k_lists_heap(lists)
        # All values from 0-19 sorted
        assert result.to_list() == list(range(20))

    def test_one_element_per_list(self):
        lists = [ListNode.from_list([i]) for i in range(5, 0, -1)]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 2, 3, 4, 5]


class TestMergeKListsDivideConquer:
    """Tests for divide-and-conquer k-way merge."""

    def test_example_1(self):
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_lists(self):
        lists = []
        result = merge_k_lists_divide_conquer(lists)
        assert result is None

    def test_single_list(self):
        lists = [ListNode.from_list([1, 2, 3])]
        result = merge_k_lists_divide_conquer(lists)
        assert result.to_list() == [1, 2, 3]

    def test_two_lists(self):
        lists = [
            ListNode.from_list([1, 3, 5]),
            ListNode.from_list([2, 4, 6]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6]


class TestMergeKListsDefault:
    """Tests for default merge_k_lists (exposed as main function)."""

    def test_uses_heap_approach(self):
        """Verify default function produces correct results."""
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
