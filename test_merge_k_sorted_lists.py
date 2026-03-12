"""
Tests for Merge k Sorted Lists solution.
"""
from __future__ import annotations

import pytest

from merge_k_sorted_lists import (
    ListNode,
    merge_k_lists,
    list_to_linkedlist,
    linkedlist_to_list,
)


class TestMergeKSortedLists:
    """Test cases for merge_k_lists function."""

    def test_multiple_lists(self):
        """Test merging multiple sorted lists."""
        list1 = list_to_linkedlist([1, 4, 5])
        list2 = list_to_linkedlist([1, 3, 4])
        list3 = list_to_linkedlist([2, 6])

        result = merge_k_lists([list1, list2, list3])
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_single_list(self):
        """Test when there is only one list."""
        list1 = list_to_linkedlist([1, 2, 3])
        result = merge_k_lists([list1])
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_empty_lists(self):
        """Test with empty list of lists."""
        result = merge_k_lists([])
        assert result is None

    def test_lists_with_none(self):
        """Test when some lists are None."""
        list1 = list_to_linkedlist([1, 3, 5])
        result = merge_k_lists([list1, None, None])
        assert linkedlist_to_list(result) == [1, 3, 5]

    def test_all_none_lists(self):
        """Test when all lists are None."""
        result = merge_k_lists([None, None, None])
        assert result is None

    def test_single_element_lists(self):
        """Test with single element lists."""
        list1 = list_to_linkedlist([1])
        list2 = list_to_linkedlist([2])
        list3 = list_to_linkedlist([3])

        result = merge_k_lists([list1, list2, list3])
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_already_sorted(self):
        """Test when all elements are already in order."""
        list1 = list_to_linkedlist([1, 2, 3])
        list2 = list_to_linkedlist([4, 5, 6])
        list3 = list_to_linkedlist([7, 8, 9])

        result = merge_k_lists([list1, list2, list3])
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_interleaved_values(self):
        """Test with interleaved values across lists."""
        list1 = list_to_linkedlist([1, 6, 7])
        list2 = list_to_linkedlist([2, 5, 8])
        list3 = list_to_linkedlist([3, 4, 9])

        result = merge_k_lists([list1, list2, list3])
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_duplicates_across_lists(self):
        """Test when duplicates exist across different lists."""
        list1 = list_to_linkedlist([1, 1, 1])
        list2 = list_to_linkedlist([1, 1, 1])
        list3 = list_to_linkedlist([1, 1, 1])

        result = merge_k_lists([list1, list2, list3])
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1, 1, 1, 1]

    def test_negative_numbers(self):
        """Test with negative numbers."""
        list1 = list_to_linkedlist([-3, -1, 0])
        list2 = list_to_linkedlist([-2, 2, 5])

        result = merge_k_lists([list1, list2])
        assert linkedlist_to_list(result) == [-3, -2, -1, 0, 2, 5]

    def test_large_values(self):
        """Test with large integer values."""
        list1 = list_to_linkedlist([10**9, 10**9 + 1])
        list2 = list_to_linkedlist([-10**9, 0])

        result = merge_k_lists([list1, list2])
        assert linkedlist_to_list(result) == [-10**9, 0, 10**9, 10**9 + 1]

    def test_two_empty_one_with_values(self):
        """Test with two empty lists and one with values."""
        list1 = None
        list2 = list_to_linkedlist([1, 2, 3])
        list3 = None

        result = merge_k_lists([list1, list2, list3])
        assert linkedlist_to_list(result) == [1, 2, 3]


class TestHelperFunctions:
    """Test helper functions."""

    def test_list_to_linkedlist_empty(self):
        """Test converting empty list."""
        assert list_to_linkedlist([]) is None

    def test_list_to_linkedlist_single(self):
        """Test converting single element list."""
        result = list_to_linkedlist([5])
        assert result.val == 5
        assert result.next is None

    def test_linkedlist_to_list_empty(self):
        """Test converting empty linked list."""
        assert linkedlist_to_list(None) == []

    def test_linkedlist_to_list_single(self):
        """Test converting single node linked list."""
        node = ListNode(42)
        assert linkedlist_to_list(node) == [42]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
