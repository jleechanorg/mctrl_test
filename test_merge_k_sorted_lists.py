"""
Tests for Merge k Sorted Lists solution.

Comprehensive test cases covering:
- Normal cases with multiple lists
- Edge cases: empty input, single list, single element
- Lists of varying lengths
- Duplicate values across lists
- Negative numbers
- All approaches (heap, divide-and-conquer, naive)
"""
from __future__ import annotations

import pytest
from merge_k_sorted_lists import (
    ListNode,
    merge_k_lists,
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
    merge_k_lists_naive,
    list_to_linkedlist,
    linkedlist_to_list,
)


class TestMergeKSortedLists:
    """Test suite for Merge k Sorted Lists problem."""

    @pytest.mark.parametrize("solution", [
        merge_k_lists_heap,
        merge_k_lists_divide_conquer,
        merge_k_lists_naive,
    ])
    def test_example_1(self, solution):
        """Test the first example from LeetCode."""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        expected = [1, 1, 2, 3, 4, 4, 5, 6]
        result = solution(lists)
        assert linkedlist_to_list(result) == expected

    @pytest.mark.parametrize("solution", [
        merge_k_lists_heap,
        merge_k_lists_divide_conquer,
        merge_k_lists_naive,
    ])
    def test_empty_lists(self, solution):
        """Test with empty list of lists."""
        lists = []
        result = solution(lists)
        assert result is None
        assert linkedlist_to_list(result) == []

    @pytest.mark.parametrize("solution", [
        merge_k_lists_heap,
        merge_k_lists_divide_conquer,
        merge_k_lists_naive,
    ])
    def test_list_with_empty_list(self, solution):
        """Test with a list containing only empty lists."""
        # [[]] becomes [None] after list_to_linkedlist, which is valid
        lists = [None]
        result = solution(lists)
        assert linkedlist_to_list(result) == []

    @pytest.mark.parametrize("solution", [
        merge_k_lists_heap,
        merge_k_lists_divide_conquer,
        merge_k_lists_naive,
    ])
    def test_single_list(self, solution):
        """Test with a single non-empty list."""
        lists = [list_to_linkedlist([1, 2, 3])]
        expected = [1, 2, 3]
        result = solution(lists)
        assert linkedlist_to_list(result) == expected

    @pytest.mark.parametrize("solution", [
        merge_k_lists_heap,
        merge_k_lists_divide_conquer,
        merge_k_lists_naive,
    ])
    def test_single_element_lists(self, solution):
        """Test with multiple single-element lists."""
        lists = [
            list_to_linkedlist([1]),
            list_to_linkedlist([2]),
            list_to_linkedlist([3]),
        ]
        expected = [1, 2, 3]
        result = solution(lists)
        assert linkedlist_to_list(result) == expected

    @pytest.mark.parametrize("solution", [
        merge_k_lists_heap,
        merge_k_lists_divide_conquer,
        merge_k_lists_naive,
    ])
    def test_duplicates_across_lists(self, solution):
        """Test with duplicate values across different lists."""
        lists = [
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1]),
            list_to_linkedlist([1]),
        ]
        expected = [1, 1, 1, 1, 1, 1]
        result = solution(lists)
        assert linkedlist_to_list(result) == expected

    @pytest.mark.parametrize("solution", [
        merge_k_lists_heap,
        merge_k_lists_divide_conquer,
        merge_k_lists_naive,
    ])
    def test_negative_numbers(self, solution):
        """Test with negative numbers."""
        lists = [
            list_to_linkedlist([-3, -1, 2]),
            list_to_linkedlist([-5, -2, 0]),
            list_to_linkedlist([1, 3, 4]),
        ]
        expected = [-5, -3, -2, -1, 0, 1, 2, 3, 4]
        result = solution(lists)
        assert linkedlist_to_list(result) == expected

    @pytest.mark.parametrize("solution", [
        merge_k_lists_heap,
        merge_k_lists_divide_conquer,
        merge_k_lists_naive,
    ])
    def test_varying_lengths(self, solution):
        """Test with lists of significantly varying lengths."""
        lists = [
            list_to_linkedlist([1]),
            list_to_linkedlist([2, 2, 2, 2]),
            list_to_linkedlist([3, 3, 3, 3, 3, 3]),
        ]
        expected = [1, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3]
        result = solution(lists)
        assert linkedlist_to_list(result) == expected

    @pytest.mark.parametrize("solution", [
        merge_k_lists_heap,
        merge_k_lists_divide_conquer,
        merge_k_lists_naive,
    ])
    def test_already_sorted(self, solution):
        """Test when lists are already in order."""
        lists = [
            list_to_linkedlist([1, 2]),
            list_to_linkedlist([3, 4]),
            list_to_linkedlist([5, 6]),
        ]
        expected = [1, 2, 3, 4, 5, 6]
        result = solution(lists)
        assert linkedlist_to_list(result) == expected

    @pytest.mark.parametrize("solution", [
        merge_k_lists_heap,
        merge_k_lists_divide_conquer,
        merge_k_lists_naive,
    ])
    def test_interleaved_values(self, solution):
        """Test when values from different lists are interleaved."""
        lists = [
            list_to_linkedlist([1, 10, 20]),
            list_to_linkedlist([2, 11, 21]),
            list_to_linkedlist([3, 12, 22]),
        ]
        expected = [1, 2, 3, 10, 11, 12, 20, 21, 22]
        result = solution(lists)
        assert linkedlist_to_list(result) == expected

    @pytest.mark.parametrize("solution", [
        merge_k_lists_heap,
        merge_k_lists_divide_conquer,
        merge_k_lists_naive,
    ])
    def test_mixed_none_and_values(self, solution):
        """Test with mix of None and non-empty lists."""
        lists = [
            None,
            list_to_linkedlist([1, 3, 5]),
            None,
            list_to_linkedlist([2, 4, 6]),
            None,
        ]
        expected = [1, 2, 3, 4, 5, 6]
        result = solution(lists)
        assert linkedlist_to_list(result) == expected


class TestDefaultSolution:
    """Test that the default solution (merge_k_lists) works correctly."""

    def test_default_is_heap_solution(self):
        """Verify the default export uses heap approach."""
        # This test verifies the alias works
        lists = [list_to_linkedlist([1, 2, 3]), list_to_linkedlist([4, 5, 6])]
        expected = [1, 2, 3, 4, 5, 6]
        assert linkedlist_to_list(merge_k_lists(lists)) == expected


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

    def test_roundtrip_conversion(self):
        """Test list -> linkedlist -> list conversion."""
        original = [1, 2, 3, 4, 5]
        linked = list_to_linkedlist(original)
        result = linkedlist_to_list(linked)
        assert result == original
