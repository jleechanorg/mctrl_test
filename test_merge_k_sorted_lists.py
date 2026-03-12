"""
Tests for Merge k Sorted Lists solution.
"""
from __future__ import annotations

import pytest

from merge_k_sorted_lists import (
    ListNode,
    list_to_linkedlist,
    linkedlist_to_list,
    merge_k_lists,
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
)


class TestMergeKSortedLists:
    """Test cases for merge k sorted lists."""

    def test_example_1(self):
        """Test example 1 from LeetCode."""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_example_2(self):
        """Test with empty list of lists."""
        lists = []
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == []

    def test_example_3(self):
        """Test with list containing single empty list."""
        lists = [None]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == []

    def test_single_list(self):
        """Test with single non-empty list."""
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_lists(self):
        """Test with two lists."""
        lists = [
            list_to_linkedlist([1, 3, 5]),
            list_to_linkedlist([2, 4, 6]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_lists_with_duplicates(self):
        """Test with duplicate values across lists."""
        lists = [
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1, 1]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1]

    def test_negative_values(self):
        """Test with negative values."""
        lists = [
            list_to_linkedlist([-3, -1, 0]),
            list_to_linkedlist([-2, 2]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [-3, -2, -1, 0, 2]

    def test_mixed_length_lists(self):
        """Test with lists of varying lengths."""
        lists = [
            list_to_linkedlist([1]),
            list_to_linkedlist([2, 3, 4, 5]),
            list_to_linkedlist([6, 7, 8, 9, 10]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_all_empty_lists(self):
        """Test with multiple empty lists."""
        lists = [None, None, None]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == []

    def test_large_values(self):
        """Test with large values."""
        lists = [
            list_to_linkedlist([10000, 10001]),
            list_to_linkedlist([-10000, -9999]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [-10000, -9999, 10000, 10001]


class TestBothApproaches:
    """Test that both heap and divide-conquer approaches work correctly."""

    def _make_lists(self, data):
        """Create fresh linked lists from test data."""
        return [list_to_linkedlist(d) if d else None for d in data]

    def test_example_1(self):
        """Test example 1 - both approaches equal."""
        data = [[1, 4, 5], [1, 3, 4], [2, 6]]
        heap_result = merge_k_lists_heap(self._make_lists(data))
        dc_result = merge_k_lists_divide_conquer(self._make_lists(data))
        assert linkedlist_to_list(heap_result) == linkedlist_to_list(dc_result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_single_list(self):
        """Test single list."""
        data = [[1, 2, 3]]
        heap_result = merge_k_lists_heap(self._make_lists(data))
        dc_result = merge_k_lists_divide_conquer(self._make_lists(data))
        assert linkedlist_to_list(heap_result) == linkedlist_to_list(dc_result) == [1, 2, 3]

    def test_two_lists(self):
        """Test two lists."""
        data = [[1, 3, 5], [2, 4, 6]]
        heap_result = merge_k_lists_heap(self._make_lists(data))
        dc_result = merge_k_lists_divide_conquer(self._make_lists(data))
        assert linkedlist_to_list(heap_result) == linkedlist_to_list(dc_result) == [1, 2, 3, 4, 5, 6]

    def test_empty(self):
        """Test empty input."""
        data = []
        heap_result = merge_k_lists_heap(self._make_lists(data))
        dc_result = merge_k_lists_divide_conquer(self._make_lists(data))
        assert linkedlist_to_list(heap_result) == linkedlist_to_list(dc_result) == []

    def test_single_none(self):
        """Test single None input."""
        data = [None]
        heap_result = merge_k_lists_heap(self._make_lists(data))
        dc_result = merge_k_lists_divide_conquer(self._make_lists(data))
        assert linkedlist_to_list(heap_result) == linkedlist_to_list(dc_result) == []


class TestHelperFunctions:
    """Test helper functions."""

    def test_list_to_linkedlist_empty(self):
        """Test converting empty list."""
        assert list_to_linkedlist([]) is None

    def test_list_to_linkedlist_single(self):
        """Test converting single element list."""
        node = list_to_linkedlist([5])
        assert node.val == 5
        assert node.next is None

    def test_linkedlist_to_list_empty(self):
        """Test converting empty linked list."""
        assert linkedlist_to_list(None) == []

    def test_roundtrip(self):
        """Test list -> linkedlist -> list roundtrip."""
        original = [1, 2, 3, 4, 5]
        linked = list_to_linkedlist(original)
        result = linkedlist_to_list(linked)
        assert result == original
