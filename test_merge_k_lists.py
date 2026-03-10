"""
Tests for Merge k Sorted Lists solution.
"""
from __future__ import annotations

import pytest
from merge_k_lists import (
    merge_k_lists,
    list_to_linkedlist,
    linkedlist_to_list,
    ListNode,
)


class TestMergeKSortedLists:
    """Test cases for the merge_k_lists function."""

    def test_example_from_leetcode(self):
        """Test the example provided in LeetCode problem."""
        list1 = list_to_linkedlist([1, 4, 5])
        list2 = list_to_linkedlist([1, 3, 4])
        list3 = list_to_linkedlist([2, 6])

        result = merge_k_lists([list1, list2, list3])
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_list_of_lists(self):
        """Test with empty list of lists."""
        result = merge_k_lists([])
        assert result is None

    def test_single_list(self):
        """Test with single linked list."""
        list1 = list_to_linkedlist([1, 2, 3])
        result = merge_k_lists([list1])
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_lists_with_single_elements(self):
        """Test with multiple lists each containing single element."""
        list1 = list_to_linkedlist([1])
        list2 = list_to_linkedlist([2])
        list3 = list_to_linkedlist([3])

        result = merge_k_lists([list1, list2, list3])
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_empty_lists(self):
        """Test with two empty lists."""
        result = merge_k_lists([None, None])
        assert result is None

    def test_one_empty_list_others_not(self):
        """Test with one empty list and others non-empty."""
        list1 = list_to_linkedlist([1, 2, 3])
        result = merge_k_lists([None, list1])
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_all_empty_lists(self):
        """Test with all empty lists."""
        result = merge_k_lists([None, None, None])
        assert result is None

    def test_duplicate_values(self):
        """Test with duplicate values across lists."""
        list1 = list_to_linkedlist([1, 1, 1])
        list2 = list_to_linkedlist([1, 1, 1])
        list3 = list_to_linkedlist([1, 1, 1])

        result = merge_k_lists([list1, list2, list3])
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1, 1, 1, 1]

    def test_negative_numbers(self):
        """Test with negative numbers."""
        list1 = list_to_linkedlist([-3, -1, 2])
        list2 = list_to_linkedlist([-2, 0, 4])

        result = merge_k_lists([list1, list2])
        assert linkedlist_to_list(result) == [-3, -2, -1, 0, 2, 4]

    def test_already_sorted_single_list(self):
        """Test with single list that is already sorted."""
        list1 = list_to_linkedlist([1, 2, 3, 4, 5])
        result = merge_k_lists([list1])
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5]

    def test_reverse_order(self):
        """Test with lists in reverse order."""
        list1 = list_to_linkedlist([5])
        list2 = list_to_linkedlist([3])
        list3 = list_to_linkedlist([1])

        result = merge_k_lists([list1, list2, list3])
        assert linkedlist_to_list(result) == [1, 3, 5]

    def test_large_values(self):
        """Test with large integer values."""
        list1 = list_to_linkedlist([10**9, 10**9 + 1])
        list2 = list_to_linkedlist([10**8, 10**8 + 1])

        result = merge_k_lists([list1, list2])
        assert linkedlist_to_list(result) == [10**8, 10**8 + 1, 10**9, 10**9 + 1]

    def test_interleaved_values(self):
        """Test with interleaved values from different lists."""
        list1 = list_to_linkedlist([1, 3, 5, 7, 9])
        list2 = list_to_linkedlist([2, 4, 6, 8, 10])

        result = merge_k_lists([list1, list2])
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_mixed_empty_and_non_empty(self):
        """Test with mix of empty and non-empty lists."""
        list1 = list_to_linkedlist([1, 5])
        list2 = None
        list3 = list_to_linkedlist([2, 3])
        list4 = None
        list5 = list_to_linkedlist([4])

        result = merge_k_lists([list1, list2, list3, list4, list5])
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5]

    def test_list_to_linkedlist_empty(self):
        """Test list_to_linkedlist with empty list."""
        result = list_to_linkedlist([])
        assert result is None

    def test_linkedlist_to_list_empty(self):
        """Test linkedlist_to_list with None."""
        result = linkedlist_to_list(None)
        assert result == []

    def test_linkedlist_to_list_single(self):
        """Test linkedlist_to_list with single node."""
        node = ListNode(42)
        result = linkedlist_to_list(node)
        assert result == [42]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
