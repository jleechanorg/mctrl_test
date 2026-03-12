"""Tests for Merge k Sorted Lists solution."""

from __future__ import annotations

import pytest
from merge_k_sorted_lists import (
    ListNode,
    merge_k_lists,
    merge_k_lists_divide_conquer,
    merge_k_lists_brute_force,
)


class TestListNodeHelper:
    """Test the ListNode helper functions."""

    def test_from_list_empty(self):
        assert ListNode.from_list([]) is None

    def test_from_list_single(self):
        head = ListNode.from_list([1])
        assert head.val == 1
        assert head.next is None

    def test_from_list_multiple(self):
        head = ListNode.from_list([1, 2, 3])
        assert head.val == 1
        assert head.next.val == 2
        assert head.next.next.val == 3
        assert head.next.next.next is None

    def test_to_list_empty(self):
        head = ListNode.from_list([])
        assert head is None or head.to_list() == []

    def test_to_list_single(self):
        head = ListNode.from_list([5])
        assert head.to_list() == [5]

    def test_to_list_multiple(self):
        head = ListNode.from_list([1, 2, 3, 4, 5])
        assert head.to_list() == [1, 2, 3, 4, 5]


class TestMergeKListsHeap:
    """Test the min-heap based solution."""

    def test_example_1(self):
        """Example 1: lists = [[1,4,5],[1,3,4],[2,6]]"""
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_example_2_empty_lists(self):
        """Example 2: lists = []"""
        lists = []
        result = merge_k_lists(lists)
        assert result is None

    def test_example_3_empty_sublist(self):
        """Example 3: lists = [[]]"""
        lists = [ListNode.from_list([])]
        result = merge_k_lists(lists)
        assert result is None

    def test_single_list(self):
        """Test with a single non-empty list."""
        lists = [ListNode.from_list([1, 2, 3])]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3]

    def test_two_lists(self):
        """Test with two lists."""
        lists = [
            ListNode.from_list([1, 3, 5]),
            ListNode.from_list([2, 4, 6]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6]

    def test_lists_with_duplicates(self):
        """Test with duplicate values across lists."""
        lists = [
            ListNode.from_list([1, 1, 1]),
            ListNode.from_list([1, 1]),
            ListNode.from_list([1]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 1, 1, 1, 1, 1]

    def test_all_empty_lists(self):
        """Test with all empty lists."""
        lists = [ListNode.from_list([]) for _ in range(3)]
        result = merge_k_lists(lists)
        assert result is None

    def test_mixed_empty_and_non_empty(self):
        """Test with mix of empty and non-empty lists."""
        lists = [
            ListNode.from_list([]),
            ListNode.from_list([1, 2]),
            ListNode.from_list([]),
            ListNode.from_list([3]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3]

    def test_negative_numbers(self):
        """Test with negative values."""
        lists = [
            ListNode.from_list([-3, -1, 0]),
            ListNode.from_list([-2, 2]),
            ListNode.from_list([-1, 1, 3]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [-3, -2, -1, -1, 0, 1, 2, 3]

    def test_single_element_each(self):
        """Test with single element in each list."""
        lists = [ListNode.from_list([i]) for i in [5, 2, 8, 1, 9]]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 5, 8, 9]

    def test_already_sorted_single_list(self):
        """Test with one already sorted large list."""
        lists = [ListNode.from_list(list(range(100)))]
        result = merge_k_lists(lists)
        assert result.to_list() == list(range(100))

    def test_reverse_sorted_merged(self):
        """Test merging lists with reverse-sorted individual elements."""
        # Each list is sorted in ascending order, but together form descending sequence
        lists = [
            ListNode.from_list([8, 9, 10]),
            ListNode.from_list([5, 6, 7]),
            ListNode.from_list([1, 2, 3, 4]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


class TestMergeKListsDivideConquer:
    """Test the divide and conquer solution."""

    def test_example_1(self):
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty(self):
        lists = []
        result = merge_k_lists_divide_conquer(lists)
        assert result is None

    def test_single_list(self):
        lists = [ListNode.from_list([1, 2, 3])]
        result = merge_k_lists_divide_conquer(lists)
        assert result.to_list() == [1, 2, 3]

    def test_two_lists(self):
        lists = [
            ListNode.from_list([1, 3, 5]),
            ListNode.from_list([2, 4, 6]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6]


class TestMergeKListsBruteForce:
    """Test the brute force solution."""

    def test_example_1(self):
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6]),
        ]
        result = merge_k_lists_brute_force(lists)
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty(self):
        lists = []
        result = merge_k_lists_brute_force(lists)
        assert result is None


class TestAllSolutionsConsistent:
    """Verify all solutions produce the same results."""

    def test_all_solutions_equal(self):
        """All three solutions should produce identical results."""
        test_cases = [
            [[1, 4, 5], [1, 3, 4], [2, 6]],
            [],
            [[]],
            [[1], [2], [3]],
            [[1, 1, 1], [1, 1], [1]],
            [[-3, -1], [-2, 2], [-1, 1]],
        ]

        for lists_input in test_cases:
            lists = [ListNode.from_list(lst) if lst else None for lst in lists_input]

            result_heap = merge_k_lists([ListNode.from_list(lst) if lst else None for lst in lists_input])
            result_dc = merge_k_lists_divide_conquer([ListNode.from_list(lst) if lst else None for lst in lists_input])
            result_bf = merge_k_lists_brute_force([ListNode.from_list(lst) if lst else None for lst in lists_input])

            # Convert to lists for comparison
            list_heap = result_heap.to_list() if result_heap else []
            list_dc = result_dc.to_list() if result_dc else []
            list_bf = result_bf.to_list() if result_bf else []

            assert list_heap == list_dc == list_bf, f"Failed for input {lists_input}"
