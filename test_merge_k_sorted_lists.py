"""
Unit tests for Merge k Sorted Lists solution.
"""

import pytest
from merge_k_sorted_lists import (
    merge_k_lists,
    merge_k_lists_divide_conquer,
    list_to_linkedlist,
    linkedlist_to_list,
)


class TestMergeKSortedLists:
    """Test suite for merge_k_lists function."""

    def test_merge_three_sorted_lists(self):
        """Test merging three sorted linked lists."""
        list1 = list_to_linkedlist([1, 4, 7, 10])
        list2 = list_to_linkedlist([2, 5, 8, 11])
        list3 = list_to_linkedlist([3, 6, 9, 12])

        result = merge_k_lists([list1, list2, list3])
        expected = list(range(1, 13))
        assert linkedlist_to_list(result) == expected

    def test_empty_list_of_lists(self):
        """Test with empty list of lists."""
        result = merge_k_lists([])
        assert result is None

    def test_single_list(self):
        """Test with a single linked list."""
        list1 = list_to_linkedlist([1, 2, 3, 4, 5])
        result = merge_k_lists([list1])
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5]

    def test_one_empty_list(self):
        """Test when one of the lists is empty."""
        list1 = list_to_linkedlist([1, 3, 5])
        list2 = list_to_linkedlist([])

        result = merge_k_lists([list1, list2])
        assert linkedlist_to_list(result) == [1, 3, 5]

    def test_all_empty_lists(self):
        """Test when all lists are empty."""
        result = merge_k_lists([list_to_linkedlist([]), list_to_linkedlist([])])
        assert result is None

    def test_single_element_lists(self):
        """Test with single-element lists."""
        list1 = list_to_linkedlist([1])
        list2 = list_to_linkedlist([2])
        list3 = list_to_linkedlist([3])

        result = merge_k_lists([list1, list2, list3])
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_lists_with_duplicates(self):
        """Test with duplicate values across lists."""
        list1 = list_to_linkedlist([1, 1, 3])
        list2 = list_to_linkedlist([1, 2, 3])

        result = merge_k_lists([list1, list2])
        assert linkedlist_to_list(result) == [1, 1, 1, 2, 3, 3]

    def test_already_sorted_single_list(self):
        """Test when all elements in a single list."""
        list1 = list_to_linkedlist([1, 2, 3, 4, 5])
        result = merge_k_lists([list1])
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5]

    def test_reverse_sorted_input(self):
        """Test with lists in reverse order (but internally sorted)."""
        list1 = list_to_linkedlist([10, 20, 30])
        list2 = list_to_linkedlist([5, 15, 25])

        result = merge_k_lists([list1, list2])
        assert linkedlist_to_list(result) == [5, 10, 15, 20, 25, 30]

    def test_large_gap_between_values(self):
        """Test with large gaps between values."""
        list1 = list_to_linkedlist([1, 1000])
        list2 = list_to_linkedlist([500, 1500])

        result = merge_k_lists([list1, list2])
        assert linkedlist_to_list(result) == [1, 500, 1000, 1500]

    def test_none_in_lists(self):
        """Test when None is in the list of lists."""
        list1 = list_to_linkedlist([1, 2, 3])
        result = merge_k_lists([list1, None, None])
        assert linkedlist_to_list(result) == [1, 2, 3]


class TestMergeKSortedListsDivideConquer:
    """Test suite for divide and conquer solution."""

    def test_merge_three_sorted_lists(self):
        """Test merging three sorted linked lists."""
        list1 = list_to_linkedlist([1, 4, 7, 10])
        list2 = list_to_linkedlist([2, 5, 8, 11])
        list3 = list_to_linkedlist([3, 6, 9, 12])

        result = merge_k_lists_divide_conquer([list1, list2, list3])
        expected = list(range(1, 13))
        assert linkedlist_to_list(result) == expected

    def test_empty_list_of_lists(self):
        """Test with empty list of lists."""
        result = merge_k_lists_divide_conquer([])
        assert result is None

    def test_single_list(self):
        """Test with a single linked list."""
        list1 = list_to_linkedlist([1, 2, 3, 4, 5])
        result = merge_k_lists_divide_conquer([list1])
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5]


class TestHelperFunctions:
    """Test helper conversion functions."""

    def test_list_to_linkedlist_empty(self):
        """Test converting empty list."""
        result = list_to_linkedlist([])
        assert result is None

    def test_list_to_linkedlist_single(self):
        """Test converting single element list."""
        result = list_to_linkedlist([42])
        assert result.val == 42
        assert result.next is None

    def test_linkedlist_to_list_empty(self):
        """Test converting empty linked list."""
        result = linkedlist_to_list(None)
        assert result == []

    def test_roundtrip_conversion(self):
        """Test that conversion is reversible."""
        original = [1, 2, 3, 4, 5]
        linked = list_to_linkedlist(original)
        result = linkedlist_to_list(linked)
        assert result == original
