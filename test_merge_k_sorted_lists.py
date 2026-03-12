"""
Tests for Merge k Sorted Lists solution.
"""
from __future__ import annotations

import pytest

from merge_k_sorted_lists import (
    ListNode,
    linkedlist_to_list,
    list_to_linkedlist,
    merge_k_sorted_lists,
    merge_k_sorted_lists_divide_conquer,
    merge_k_sorted_lists_heap,
)


class TestMergeKSortedLists:
    """Test cases for merge k sorted lists."""

    def test_empty_list(self):
        """Test with empty input list."""
        result = merge_k_sorted_lists([])
        assert result is None

    def test_single_empty_list(self):
        """Test with single empty list."""
        result = merge_k_sorted_lists([None])
        assert result is None

    def test_single_list(self):
        """Test with single non-empty list."""
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_lists(self):
        """Test merging two sorted lists."""
        lists = [
            list_to_linkedlist([1, 4, 7]),
            list_to_linkedlist([2, 5, 8]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 4, 5, 7, 8]

    def test_three_lists(self):
        """Test merging three sorted lists."""
        lists = [
            list_to_linkedlist([1, 3, 5]),
            list_to_linkedlist([2, 4, 6]),
            list_to_linkedlist([0, 7, 8]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [0, 1, 2, 3, 4, 5, 6, 7, 8]

    def test_lists_with_different_lengths(self):
        """Test with lists of varying lengths."""
        lists = [
            list_to_linkedlist([1]),
            list_to_linkedlist([2, 3, 4, 5]),
            list_to_linkedlist([6, 7, 8, 9, 10]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == list(range(1, 11))

    def test_lists_with_duplicates(self):
        """Test with duplicate values across lists."""
        lists = [
            list_to_linkedlist([1, 1, 3]),
            list_to_linkedlist([1, 2, 2]),
            list_to_linkedlist([2, 3]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [1, 1, 1, 2, 2, 2, 3, 3]

    def test_negative_numbers(self):
        """Test with negative numbers."""
        lists = [
            list_to_linkedlist([-3, -1, 0]),
            list_to_linkedlist([-2, 2]),
            list_to_linkedlist([-1, 1, 3]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [-3, -2, -1, -1, 0, 1, 2, 3]

    def test_single_element_each(self):
        """Test with single element in each list."""
        lists = [
            list_to_linkedlist([3]),
            list_to_linkedlist([1]),
            list_to_linkedlist([2]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_mixed_empty_and_non_empty(self):
        """Test with mix of empty and non-empty lists."""
        lists = [
            list_to_linkedlist([1, 2]),
            None,
            list_to_linkedlist([3, 4]),
            None,
            list_to_linkedlist([5, 6]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_large_values(self):
        """Test with large integer values."""
        lists = [
            list_to_linkedlist([10**9, 10**9 + 1]),
            list_to_linkedlist([10**9 - 1]),
            list_to_linkedlist([10**9 + 2]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [
            10**9 - 1,
            10**9,
            10**9 + 1,
            10**9 + 2,
        ]


class TestMergeKSortedListsHeap:
    """Test cases specifically for heap-based solution."""

    def test_heap_equivalent_to_default(self):
        """Verify heap implementation matches default."""
        lists1 = [
            list_to_linkedlist([1, 4, 7]),
            list_to_linkedlist([2, 5, 8]),
            list_to_linkedlist([3, 6, 9]),
        ]
        lists2 = [
            list_to_linkedlist([1, 4, 7]),
            list_to_linkedlist([2, 5, 8]),
            list_to_linkedlist([3, 6, 9]),
        ]
        heap_result = merge_k_sorted_lists_heap(lists1)
        default_result = merge_k_sorted_lists(lists2)
        assert linkedlist_to_list(heap_result) == linkedlist_to_list(default_result)


class TestMergeKSortedListsDivideConquer:
    """Test cases for divide-and-conquer solution."""

    def test_divide_conquer_equivalent_to_heap(self):
        """Verify divide-conquer matches heap implementation."""
        lists1 = [
            list_to_linkedlist([1, 4, 7]),
            list_to_linkedlist([2, 5, 8]),
            list_to_linkedlist([3, 6, 9]),
        ]
        lists2 = [
            list_to_linkedlist([1, 4, 7]),
            list_to_linkedlist([2, 5, 8]),
            list_to_linkedlist([3, 6, 9]),
        ]
        dc_result = merge_k_sorted_lists_divide_conquer(lists1)
        heap_result = merge_k_sorted_lists_heap(lists2)
        assert linkedlist_to_list(dc_result) == linkedlist_to_list(heap_result)

    def test_divide_conquer_empty(self):
        """Test divide-conquer with empty input."""
        result = merge_k_sorted_lists_divide_conquer([])
        assert result is None

    def test_divide_conquer_single_list(self):
        """Test divide-conquer with single list."""
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_sorted_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]


class TestListNodeHelpers:
    """Test helper functions."""

    def test_list_to_linkedlist(self):
        """Test converting list to linked list."""
        values = [1, 2, 3, 4, 5]
        head = list_to_linkedlist(values)
        result = linkedlist_to_list(head)
        assert result == values

    def test_list_to_linkedlist_empty(self):
        """Test converting empty list."""
        head = list_to_linkedlist([])
        assert head is None

    def test_linkedlist_to_list(self):
        """Test converting linked list to list."""
        head = list_to_linkedlist([1, 2, 3])
        result = linkedlist_to_list(head)
        assert result == [1, 2, 3]

    def test_linkedlist_to_list_empty(self):
        """Test converting empty linked list."""
        result = linkedlist_to_list(None)
        assert result == []
