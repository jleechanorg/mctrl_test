"""Tests for Merge k Sorted Lists solution."""

from __future__ import annotations

import pytest

from merge_k_sorted_lists import (
    ListNode,
    list_to_linkedlist,
    linkedlist_to_list,
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
)


class TestMergeKSortedLists:
    """Test cases for merge k sorted lists algorithms."""

    def test_example1(self):
        """Example from LeetCode."""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6])
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_example1_divide_conquer(self):
        """Example from LeetCode using divide-conquer."""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6])
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_lists(self):
        """Test with empty list of lists."""
        lists = []
        result = merge_k_lists_heap(lists)
        assert result is None

    def test_empty_lists_divide_conquer(self):
        """Test with empty list of lists (divide-conquer)."""
        lists = []
        result = merge_k_lists_divide_conquer(lists)
        assert result is None

    def test_lists_with_empty_linked_lists(self):
        """Test with some empty linked lists."""
        lists = [
            list_to_linkedlist([1, 3, 5]),
            list_to_linkedlist([]),
            list_to_linkedlist([2, 4, 6])
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_single_list(self):
        """Test with a single non-empty linked list."""
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_single_element_lists(self):
        """Test with multiple single-element lists."""
        lists = [
            list_to_linkedlist([1]),
            list_to_linkedlist([3]),
            list_to_linkedlist([2]),
            list_to_linkedlist([4])
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4]

    def test_already_sorted(self):
        """Test with already sorted across lists."""
        lists = [
            list_to_linkedlist([1]),
            list_to_linkedlist([2]),
            list_to_linkedlist([3]),
            list_to_linkedlist([4])
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4]

    def test_reverse_order(self):
        """Test with lists in reverse sorted order."""
        lists = [
            list_to_linkedlist([7, 8, 9]),
            list_to_linkedlist([4, 5, 6]),
            list_to_linkedlist([1, 2, 3])
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_duplicates(self):
        """Test with duplicate values across lists."""
        lists = [
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1]),
            list_to_linkedlist([1])
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1]

    def test_negative_numbers(self):
        """Test with negative numbers."""
        lists = [
            list_to_linkedlist([-3, -2, -1]),
            list_to_linkedlist([0, 1, 2]),
            list_to_linkedlist([-1, 0])
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [-3, -2, -1, -1, 0, 0, 1, 2]

    def test_large_values(self):
        """Test with large values."""
        lists = [
            list_to_linkedlist([10**9, 10**9 + 1]),
            list_to_linkedlist([10**9 - 1, 10**9]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [10**9 - 1, 10**9, 10**9, 10**9 + 1]

    def test_all_none(self):
        """Test with all lists being None."""
        lists = [None, None, None]
        result = merge_k_lists_heap(lists)
        assert result is None

    def test_odd_number_of_lists(self):
        """Test with odd number of lists."""
        lists = [
            list_to_linkedlist([1]),
            list_to_linkedlist([2]),
            list_to_linkedlist([3])
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_divide_conquer_empty_linked_lists(self):
        """Test with some empty linked lists (divide-conquer)."""
        lists = [
            list_to_linkedlist([1, 3, 5]),
            list_to_linkedlist([]),
            list_to_linkedlist([2, 4, 6])
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_divide_conquer_all_none(self):
        """Test with all lists being None (divide-conquer)."""
        lists = [None, None, None]
        result = merge_k_lists_divide_conquer(lists)
        assert result is None

    def test_both_algorithms_equivalent(self):
        """Test that both algorithms produce same result."""
        # Test heap method
        lists_heap = [
            list_to_linkedlist([1, 5, 9]),
            list_to_linkedlist([2, 6]),
            list_to_linkedlist([3, 4, 7, 8])
        ]
        result_heap = merge_k_lists_heap(lists_heap)

        # Test divide-conquer method
        lists_dc = [
            list_to_linkedlist([1, 5, 9]),
            list_to_linkedlist([2, 6]),
            list_to_linkedlist([3, 4, 7, 8])
        ]
        result_dc = merge_k_lists_divide_conquer(lists_dc)

        assert linkedlist_to_list(result_heap) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
        assert linkedlist_to_list(result_dc) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
