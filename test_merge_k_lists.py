"""Tests for Merge k Sorted Lists solution."""
from __future__ import annotations

import pytest
from merge_k_lists import (
    merge_k_lists,
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
    ListNode,
    list_to_linkedlist,
    linkedlist_to_list,
)


class TestMergeKLists:
    """Test cases for merge_k_lists function."""

    def test_example_1(self):
        """Test Example 1 from LeetCode."""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_example_2(self):
        """Test Example 2 - empty list of lists."""
        lists = []
        result = merge_k_lists(lists)
        assert result is None

    def test_example_3(self):
        """Test Example 3 - list containing empty list."""
        lists = [[]]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == []

    def test_single_list(self):
        """Test with a single non-empty list."""
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

    def test_all_empty_lists(self):
        """Test with multiple empty lists."""
        lists = [[], [], []]
        result = merge_k_lists(lists)
        assert result is None

    def test_mixed_empty_and_non_empty(self):
        """Test with mix of empty and non-empty lists."""
        lists = [
            list_to_linkedlist([1, 3]),
            [],
            list_to_linkedlist([2, 4]),
            [],
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4]

    def test_negative_numbers(self):
        """Test with negative numbers."""
        lists = [
            list_to_linkedlist([-3, -1, 0]),
            list_to_linkedlist([-2, 2]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [-3, -2, -1, 0, 2]

    def test_duplicate_values(self):
        """Test with duplicate values across lists."""
        lists = [
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1]),
            list_to_linkedlist([1]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1]

    def test_single_element_lists(self):
        """Test with single element in each list."""
        lists = [
            list_to_linkedlist([5]),
            list_to_linkedlist([2]),
            list_to_linkedlist([8]),
            list_to_linkedlist([1]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 5, 8]

    def test_already_sorted_single_list(self):
        """Test with lists that are already merged."""
        lists = [
            list_to_linkedlist([1]),
            list_to_linkedlist([2]),
            list_to_linkedlist([3]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_large_values(self):
        """Test with large values."""
        lists = [
            list_to_linkedlist([10000]),
            list_to_linkedlist([-10000]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [-10000, 10000]

    def test_heap_vs_divide_conquer(self):
        """Verify both implementations produce same results."""
        # Create fresh lists for each to avoid mutation issues
        lists_heap = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        lists_dc = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        heap_result = merge_k_lists_heap(lists_heap)
        dc_result = merge_k_lists_divide_conquer(lists_dc)

        assert linkedlist_to_list(heap_result) == linkedlist_to_list(dc_result)


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

    def test_linkedlist_to_list_single(self):
        """Test converting single node linked list."""
        node = ListNode(5)
        assert linkedlist_to_list(node) == [5]

    def test_roundtrip_conversion(self):
        """Test that conversion is reversible."""
        original = [1, 2, 3, 4, 5]
        linked = list_to_linkedlist(original)
        result = linkedlist_to_list(linked)
        assert result == original
