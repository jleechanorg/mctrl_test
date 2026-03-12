"""Tests for Merge k Sorted Lists solution."""
from __future__ import annotations

import pytest

from merge_k_sorted_lists import (
    ListNode,
    list_to_linkedlist,
    linkedlist_to_list,
    merge_k_sorted_lists,
    merge_k_sorted_lists_divide_conquer,
)


class TestMergeKSortedLists:
    """Test cases for merge k sorted lists."""

    def test_example_1(self):
        """Example 1 from LeetCode."""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = merge_k_sorted_lists(lists)
        expected = [1, 1, 2, 3, 4, 4, 5, 6]
        assert linkedlist_to_list(result) == expected

    def test_example_1_divide_conquer(self):
        """Example 1 using divide and conquer approach."""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = merge_k_sorted_lists_divide_conquer(lists)
        expected = [1, 1, 2, 3, 4, 4, 5, 6]
        assert linkedlist_to_list(result) == expected

    def test_empty_lists(self):
        """Test with empty list of lists."""
        lists = []
        result = merge_k_sorted_lists(lists)
        assert result is None

    def test_single_empty_list(self):
        """Test with single empty list."""
        lists = [None]
        result = merge_k_sorted_lists(lists)
        assert result is None

    def test_single_list(self):
        """Test with single non-empty list."""
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_sorted_lists(lists)
        expected = [1, 2, 3]
        assert linkedlist_to_list(result) == expected

    def test_two_lists(self):
        """Test with two lists."""
        lists = [list_to_linkedlist([1, 3, 5]), list_to_linkedlist([2, 4, 6])]
        result = merge_k_sorted_lists(lists)
        expected = [1, 2, 3, 4, 5, 6]
        assert linkedlist_to_list(result) == expected

    def test_lists_with_duplicates(self):
        """Test with lists containing duplicate values."""
        lists = [
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1, 1]),
        ]
        result = merge_k_sorted_lists(lists)
        expected = [1, 1, 1, 1, 1, 1, 1, 1, 1]
        assert linkedlist_to_list(result) == expected

    def test_mixed_empty_and_non_empty(self):
        """Test with mix of empty and non-empty lists."""
        lists = [
            list_to_linkedlist([1, 3, 5]),
            None,
            list_to_linkedlist([2, 4, 6]),
            None,
            list_to_linkedlist([7, 8, 9]),
        ]
        result = merge_k_sorted_lists(lists)
        expected = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        assert linkedlist_to_list(result) == expected

    def test_negative_values(self):
        """Test with negative values."""
        lists = [
            list_to_linkedlist([-3, -1, 0]),
            list_to_linkedlist([-5, -2]),
            list_to_linkedlist([2, 5]),
        ]
        result = merge_k_sorted_lists(lists)
        expected = [-5, -3, -2, -1, 0, 2, 5]
        assert linkedlist_to_list(result) == expected

    def test_large_values(self):
        """Test with large integer values."""
        lists = [
            list_to_linkedlist([10**9, 10**9 + 1]),
            list_to_linkedlist([10**8, 10**8 + 1]),
        ]
        result = merge_k_sorted_lists(lists)
        expected = [10**8, 10**8 + 1, 10**9, 10**9 + 1]
        assert linkedlist_to_list(result) == expected


class TestMergeTwoLists:
    """Test cases for merge two lists helper."""

    def test_basic(self):
        """Basic test."""
        l1 = list_to_linkedlist([1, 2, 4])
        l2 = list_to_linkedlist([1, 3, 4])
        from merge_k_sorted_lists import merge_two_lists

        result = merge_two_lists(l1, l2)
        expected = [1, 1, 2, 3, 4, 4]
        assert linkedlist_to_list(result) == expected

    def test_empty_l1(self):
        """Test with empty first list."""
        l1 = None
        l2 = list_to_linkedlist([1, 2, 3])
        from merge_k_sorted_lists import merge_two_lists

        result = merge_two_lists(l1, l2)
        expected = [1, 2, 3]
        assert linkedlist_to_list(result) == expected

    def test_empty_both(self):
        """Test with both empty."""
        from merge_k_sorted_lists import merge_two_lists

        result = merge_two_lists(None, None)
        assert result is None


class TestListConversion:
    """Test helper functions."""

    def test_list_to_linkedlist_empty(self):
        """Test converting empty list."""
        result = list_to_linkedlist([])
        assert result is None

    def test_linkedlist_to_list_empty(self):
        """Test converting empty linked list."""
        result = linkedlist_to_list(None)
        assert result == []

    def test_roundtrip(self):
        """Test roundtrip conversion."""
        original = [1, 2, 3, 4, 5]
        linked = list_to_linkedlist(original)
        result = linkedlist_to_list(linked)
        assert result == original
