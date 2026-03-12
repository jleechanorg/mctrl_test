"""
Unit tests for Merge k Sorted Lists solution.
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
        head = ListNode.from_list([1])
        assert head.val == 1
        assert head.next is None

    def test_from_list_multiple(self):
        head = ListNode.from_list([1, 2, 3])
        assert head.to_list() == [1, 2, 3]

    def test_to_list_empty(self):
        head = ListNode(0)
        assert head.to_list() == [0]

    def test_to_list_full(self):
        head = ListNode.from_list([1, 4, 5, 7])
        assert head.to_list() == [1, 4, 5, 7]


class TestMergeTwoLists:
    """Tests for merging two sorted lists."""

    def test_merge_both_empty(self):
        assert merge_two_lists(None, None) is None

    def test_merge_one_empty(self):
        l1 = ListNode.from_list([1, 2, 3])
        result = merge_two_lists(l1, None)
        assert result.to_list() == [1, 2, 3]

    def test_merge_interleaved(self):
        l1 = ListNode.from_list([1, 3, 5])
        l2 = ListNode.from_list([2, 4, 6])
        result = merge_two_lists(l1, l2)
        assert result.to_list() == [1, 2, 3, 4, 5, 6]

    def test_merge_duplicates(self):
        l1 = ListNode.from_list([1, 2, 3])
        l2 = ListNode.from_list([2, 3, 4])
        result = merge_two_lists(l1, l2)
        assert result.to_list() == [1, 2, 2, 3, 3, 4]


class TestMergeKListsHeap:
    """Tests for heap-based merge k sorted lists."""

    def test_example_1(self):
        """Example from LeetCode: [[1,4,5],[1,3,4],[2,6]]"""
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_input(self):
        assert merge_k_lists_heap([]) is None

    def test_list_with_empty_lists(self):
        lists = [ListNode.from_list([]), ListNode.from_list([1])]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1]

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
            ListNode.from_list([-3, -1, 0]),
            ListNode.from_list([-2, 2]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [-3, -2, -1, 0, 2]

    def test_large_k_small_lists(self):
        """Test with many small lists (k=10, each with 0-2 elements)"""
        lists = [
            ListNode.from_list([1]),
            ListNode.from_list([]),
            ListNode.from_list([0]),
            ListNode.from_list([2]),
            ListNode.from_list([]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [0, 1, 2]


class TestMergeKListsDivideConquer:
    """Tests for divide-and-conquer merge k sorted lists."""

    def test_example_1(self):
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_input(self):
        assert merge_k_lists_divide_conquer([]) is None

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


class TestMainMergeFunction:
    """Tests for the default merge_k_lists function (heap-based)."""

    def test_default_is_heap(self):
        """Verify default uses heap approach."""
        lists = [ListNode.from_list([1, 2]), ListNode.from_list([3, 4])]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3, 4]

    def test_equivalence(self):
        """Both approaches should produce same results."""
        lists1 = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6]),
        ]
        lists2 = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6]),
        ]
        result_heap = merge_k_lists_heap(lists1)
        result_dc = merge_k_lists_divide_conquer(lists2)
        assert result_heap.to_list() == result_dc.to_list()
