"""
Tests for Merge k Sorted Lists solution.
"""
from __future__ import annotations

import pytest
from merge_k_lists import (
    ListNode,
    merge_k_lists,
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
)


class TestListNode:
    """Tests for ListNode utility methods."""

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

    def test_to_list_empty(self):
        assert ListNode(0) is not None  # Just check node can be created

    def test_to_list_multiple(self):
        node = ListNode.from_list([1, 2, 3])
        assert node.to_list() == [1, 2, 3]


class TestMergeKListsHeap:
    """Tests for heap-based solution."""

    def test_example1(self):
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

    def test_already_sorted(self):
        lists = [
            ListNode.from_list([1, 2, 3]),
            ListNode.from_list([4, 5, 6]),
            ListNode.from_list([7, 8, 9]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_with_negative_numbers(self):
        lists = [
            ListNode.from_list([-3, -1, 0]),
            ListNode.from_list([-2, 2]),
            ListNode.from_list([1, 3]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [-3, -2, -1, 0, 1, 2, 3]

    def test_with_duplicates(self):
        lists = [
            ListNode.from_list([1, 1, 1]),
            ListNode.from_list([1, 1]),
            ListNode.from_list([1]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 1, 1, 1, 1, 1]

    def test_large_values(self):
        lists = [
            ListNode.from_list([10000]),
            ListNode.from_list([-10000]),
            ListNode.from_list([0]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [-10000, 0, 10000]

    def test_many_small_lists(self):
        # k = 4 lists with 1 element each
        lists = [
            ListNode.from_list([1]),
            ListNode.from_list([2]),
            ListNode.from_list([3]),
            ListNode.from_list([4]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 2, 3, 4]


class TestMergeKListsDivideConquer:
    """Tests for divide-and-conquer solution."""

    def test_example1(self):
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


class TestMainMergeKLists:
    """Tests for main merge_k_lists function (uses heap approach)."""

    def test_main_function_uses_heap(self):
        """Test that main function returns correct results."""
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_input(self):
        result = merge_k_lists([])
        assert result is None
