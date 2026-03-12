"""
Tests for Merge k Sorted Lists solution.
"""
from __future__ import annotations

import pytest

from merge_k_sorted_lists import (
    ListNode,
    list_to_linkedlist,
    linkedlist_to_list,
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
)


class TestMergeKListsHeap:
    """Tests for heap-based solution."""

    def test_example_1(self):
        lists = [list_to_linkedlist([1, 4, 5]), list_to_linkedlist([1, 3, 4]), list_to_linkedlist([2, 6])]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_list(self):
        lists = []
        result = merge_k_lists_heap(lists)
        assert result is None

    def test_list_with_empty_list(self):
        lists = [[]]
        result = merge_k_lists_heap(lists)
        assert result is None

    def test_single_list(self):
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_lists(self):
        lists = [list_to_linkedlist([1, 2, 3]), list_to_linkedlist([4, 5, 6])]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_interleaved_lists(self):
        lists = [list_to_linkedlist([1, 3, 5]), list_to_linkedlist([2, 4, 6])]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_duplicates(self):
        lists = [list_to_linkedlist([1, 1, 1]), list_to_linkedlist([1, 1, 1])]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1]

    def test_negative_numbers(self):
        lists = [list_to_linkedlist([-3, -1, 0]), list_to_linkedlist([-2, 2])]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [-3, -2, -1, 0, 2]

    def test_large_k(self):
        # Many small lists
        lists = [list_to_linkedlist([i]) for i in range(10)]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == list(range(10))

    def test_mixed_empty_and_non_empty(self):
        lists = [list_to_linkedlist([1, 2]), None, list_to_linkedlist([3, 4]), None]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4]


class TestMergeKListsDivideConquer:
    """Tests for divide-and-conquer solution."""

    def test_example_1(self):
        lists = [list_to_linkedlist([1, 4, 5]), list_to_linkedlist([1, 3, 4]), list_to_linkedlist([2, 6])]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_list(self):
        lists = []
        result = merge_k_lists_divide_conquer(lists)
        assert result is None

    def test_single_list(self):
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_lists(self):
        lists = [list_to_linkedlist([1, 2, 3]), list_to_linkedlist([4, 5, 6])]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_interleaved_lists(self):
        lists = [list_to_linkedlist([1, 3, 5]), list_to_linkedlist([2, 4, 6])]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_duplicates(self):
        lists = [list_to_linkedlist([1, 1, 1]), list_to_linkedlist([1, 1, 1])]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1]

    def test_odd_number_of_lists(self):
        lists = [list_to_linkedlist([1]), list_to_linkedlist([2]), list_to_linkedlist([3])]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_list_to_linkedlist_empty(self):
        assert list_to_linkedlist([]) is None

    def test_linkedlist_to_list_empty(self):
        assert linkedlist_to_list(None) == []

    def test_roundtrip(self):
        original = [1, 2, 3, 4, 5]
        linked = list_to_linkedlist(original)
        result = linkedlist_to_list(linked)
        assert result == original
