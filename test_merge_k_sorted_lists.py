"""
Tests for Merge k Sorted Lists solution.
"""

import pytest
from merge_k_sorted_lists import (
    ListNode,
    merge_k_lists,
    list_to_linkedlist,
    linkedlist_to_list,
    merge_two_lists,
)


class TestMergeTwoLists:
    """Tests for merging two sorted lists."""

    def test_merge_two_basic(self):
        l1 = list_to_linkedlist([1, 2, 4])
        l2 = list_to_linkedlist([1, 3, 4])
        result = merge_two_lists(l1, l2)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4]

    def test_merge_two_empty(self):
        l1 = list_to_linkedlist([])
        l2 = list_to_linkedlist([1])
        result = merge_two_lists(l1, l2)
        assert linkedlist_to_list(result) == [1]

    def test_merge_two_one_empty(self):
        l1 = list_to_linkedlist([1, 2, 3])
        l2 = None
        result = merge_two_lists(l1, l2)
        assert linkedlist_to_list(result) == [1, 2, 3]


class TestMergeKSortedLists:
    """Tests for merging k sorted lists."""

    def test_example_1(self):
        """Example from LeetCode."""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_input(self):
        """Empty list of lists."""
        lists = []
        result = merge_k_lists(lists)
        assert result is None

    def test_empty_lists(self):
        """List containing empty lists."""
        lists = [list_to_linkedlist([])]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == []

    def test_single_list(self):
        """Single non-empty list."""
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_lists(self):
        """Two sorted lists."""
        lists = [
            list_to_linkedlist([1, 3, 5]),
            list_to_linkedlist([2, 4, 6]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_all_empty_lists(self):
        """Multiple empty lists."""
        lists = [list_to_linkedlist([]), list_to_linkedlist([])]
        result = merge_k_lists(lists)
        assert result is None

    def test_with_negatives(self):
        """Lists with negative values."""
        lists = [
            list_to_linkedlist([-3, -1, 2]),
            list_to_linkedlist([-2, 0, 4]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [-3, -2, -1, 0, 2, 4]

    def test_duplicates_across_lists(self):
        """Multiple duplicate values across lists."""
        lists = [
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1]),
            list_to_linkedlist([1]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1]

    def test_large_gap_values(self):
        """Values spanning large range."""
        lists = [
            list_to_linkedlist([-10000, 0]),
            list_to_linkedlist([5000, 10000]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [-10000, 0, 5000, 10000]


class TestListConversion:
    """Test helper functions."""

    def test_list_to_linkedlist_empty(self):
        result = list_to_linkedlist([])
        assert result is None

    def test_linkedlist_to_list_empty(self):
        result = linkedlist_to_list(None)
        assert result == []

    def test_roundtrip(self):
        arr = [1, 2, 3, 4, 5]
        ll = list_to_linkedlist(arr)
        result = linkedlist_to_list(ll)
        assert result == arr
