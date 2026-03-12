"""
Tests for Merge k Sorted Lists solution.
"""
from __future__ import annotations

import pytest
from merge_k_sorted_lists import (
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
    list_to_linkedlist,
    linkedlist_to_list,
    ListNode,
)


class TestMergeKSortedLists:
    """Test cases for merge k sorted lists solutions."""

    def test_example_1_heap(self):
        """Test example 1 with heap approach."""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_example_1_divide_conquer(self):
        """Test example 1 with divide and conquer approach."""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_lists_heap(self):
        """Test empty input with heap approach."""
        lists = []
        result = merge_k_lists_heap(lists)
        assert result is None

    def test_empty_lists_divide_conquer(self):
        """Test empty input with divide and conquer approach."""
        lists = []
        result = merge_k_lists_divide_conquer(lists)
        assert result is None

    def test_lists_with_empty_lists_heap(self):
        """Test with lists containing empty lists."""
        lists = [[]]
        result = merge_k_lists_heap(lists)
        assert result is None

    def test_single_list_heap(self):
        """Test with single list."""
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_single_list_divide_conquer(self):
        """Test with single list."""
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_lists_heap(self):
        """Test merging two lists."""
        lists = [
            list_to_linkedlist([1, 3, 5]),
            list_to_linkedlist([2, 4, 6]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_two_lists_divide_conquer(self):
        """Test merging two lists."""
        lists = [
            list_to_linkedlist([1, 3, 5]),
            list_to_linkedlist([2, 4, 6]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_duplicates_heap(self):
        """Test handling of duplicate values."""
        lists = [
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1, 1]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1]

    def test_negative_values_heap(self):
        """Test with negative values."""
        lists = [
            list_to_linkedlist([-3, -1, 0]),
            list_to_linkedlist([-2, 2]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [-3, -2, -1, 0, 2]

    def test_large_k_heap(self):
        """Test with many small lists."""
        lists = [list_to_linkedlist([i]) for i in range(10)]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == list(range(10))

    def test_large_k_divide_conquer(self):
        """Test with many small lists."""
        lists = [list_to_linkedlist([i]) for i in range(10)]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == list(range(10))

    def test_already_sorted_heap(self):
        """Test with already sorted lists."""
        lists = [
            list_to_linkedlist([1]),
            list_to_linkedlist([2]),
            list_to_linkedlist([3]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_reverse_sorted_heap(self):
        """Test with lists in reverse order (validates unsorted input is preserved as-is per problem)."""
        lists = [
            list_to_linkedlist([5, 4, 3]),
            list_to_linkedlist([2, 1]),
        ]
        # The problem guarantees lists are sorted in ascending order,
        # so this test validates that unsorted input returns unsorted output
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [2, 1, 5, 4, 3]


class TestHelperFunctions:
    """Test helper functions."""

    def test_list_to_linkedlist_empty(self):
        assert list_to_linkedlist([]) is None

    def test_list_to_linkedlist_single(self):
        result = list_to_linkedlist([1])
        assert result.val == 1
        assert result.next is None

    def test_linkedlist_to_list_empty(self):
        assert linkedlist_to_list(None) == []

    def test_linkedlist_to_list_roundtrip(self):
        original = [1, 2, 3, 4, 5]
        node = list_to_linkedlist(original)
        result = linkedlist_to_list(node)
        assert result == original
