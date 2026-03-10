from __future__ import annotations

import pytest
from merge_k_sorted_lists import (
    ListNode,
    merge_k_sorted_lists,
    list_to_linked,
    linked_to_list,
)


class TestMergeKSortedLists:
    """Test cases for Merge K Sorted Lists problem."""

    def test_empty_list_of_lists(self):
        """Test with empty input list."""
        result = merge_k_sorted_lists([])
        assert result is None

    def test_all_empty_lists(self):
        """Test with all None lists."""
        result = merge_k_sorted_lists([None, None, None])
        assert result is None

    def test_single_list(self):
        """Test with a single sorted list."""
        lists = [list_to_linked([1, 2, 3])]
        result = merge_k_sorted_lists(lists)
        assert linked_to_list(result) == [1, 2, 3]

    def test_two_sorted_lists(self):
        """Test merging two sorted lists."""
        lists = [
            list_to_linked([1, 4, 5]),
            list_to_linked([1, 3, 4]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linked_to_list(result) == [1, 1, 3, 4, 4, 5]

    def test_three_sorted_lists(self):
        """Test merging three sorted lists."""
        lists = [
            list_to_linked([1, 6, 7]),
            list_to_linked([2, 5, 8]),
            list_to_linked([3, 4, 9]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linked_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_lists_with_different_lengths(self):
        """Test merging lists of varying lengths."""
        lists = [
            list_to_linked([1]),
            list_to_linked([2, 3, 4, 5]),
            list_to_linked([]),
            list_to_linked([6, 7, 8, 9, 10]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linked_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_with_duplicates_across_lists(self):
        """Test merging lists that contain duplicate values."""
        lists = [
            list_to_linked([1, 1, 1]),
            list_to_linked([1, 1]),
            list_to_linked([1]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linked_to_list(result) == [1, 1, 1, 1, 1, 1]

    def test_negative_numbers(self):
        """Test merging lists with negative numbers."""
        lists = [
            list_to_linked([-5, -3, 0]),
            list_to_linked([-4, -2, 1]),
            list_to_linked([-1, 2]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linked_to_list(result) == [-5, -4, -3, -2, -1, 0, 1, 2]

    def test_single_element_lists(self):
        """Test merging multiple single-element lists."""
        lists = [
            list_to_linked([5]),
            list_to_linked([2]),
            list_to_linked([8]),
            list_to_linked([1]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linked_to_list(result) == [1, 2, 5, 8]

    def test_already_sorted_input(self):
        """Test when input lists are already in order."""
        lists = [
            list_to_linked([1, 2]),
            list_to_linked([3, 4]),
            list_to_linked([5, 6]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linked_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_reverse_sorted_input(self):
        """Test when lists contain reverse sorted elements."""
        lists = [
            list_to_linked([3, 2, 1]),  # Actually this shouldn't happen per problem
            list_to_linked([6, 5, 4]),
        ]
        result = merge_k_sorted_lists(lists)
        # Our implementation doesn't sort within each list, assumes sorted input
        assert linked_to_list(result) == [3, 2, 1, 6, 5, 4]
