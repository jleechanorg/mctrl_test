"""
Unit tests for Merge k Sorted Lists solution.
"""
from __future__ import annotations

import pytest

from merge_k_sorted_lists import (
    ListNode,
    merge_k_lists,
    merge_k_lists_naive,
)


class TestListNode:
    """Tests for ListNode utility methods."""

    def test_from_list_empty(self):
        assert ListNode.from_list([]) is None

    def test_from_list_single(self):
        head = ListNode.from_list([1])
        assert head.val == 1
        assert head.next is None

    def test_from_list_multiple(self):
        head = ListNode.from_list([1, 2, 3])
        assert head.to_list() == [1, 2, 3]

    def test_to_list_single(self):
        head = ListNode(5)
        assert head.to_list() == [5]

    def test_to_list_multiple(self):
        head = ListNode(1, ListNode(2, ListNode(3)))
        assert head.to_list() == [1, 2, 3]


class TestMergeKSortedLists:
    """Tests for merge_k_lists function."""

    def test_empty_list(self):
        """Empty input should return None."""
        result = merge_k_lists([])
        assert result is None

    def test_single_empty_list(self):
        """Single empty list should return None."""
        result = merge_k_lists([None])
        assert result is None

    def test_single_list(self):
        """Single sorted list should return as-is."""
        head = ListNode.from_list([1, 2, 3])
        result = merge_k_lists([head])
        assert result.to_list() == [1, 2, 3]

    def test_two_lists(self):
        """Two sorted lists should merge correctly."""
        l1 = ListNode.from_list([1, 3, 5])
        l2 = ListNode.from_list([2, 4, 6])
        result = merge_k_lists([l1, l2])
        assert result.to_list() == [1, 2, 3, 4, 5, 6]

    def test_three_lists(self):
        """Three sorted lists from LeetCode example."""
        l1 = ListNode.from_list([1, 4, 5])
        l2 = ListNode.from_list([1, 3, 4])
        l3 = ListNode.from_list([2, 6])
        result = merge_k_lists([l1, l2, l3])
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_with_empty_lists(self):
        """Lists with some empty should skip empty ones."""
        l1 = ListNode.from_list([1, 3])
        l2 = None
        l3 = ListNode.from_list([2, 4])
        result = merge_k_lists([l1, l2, l3])
        assert result.to_list() == [1, 2, 3, 4]

    def test_single_element_each(self):
        """Single element from each list."""
        l1 = ListNode.from_list([1])
        l2 = ListNode.from_list([0])
        l3 = ListNode.from_list([2])
        result = merge_k_lists([l1, l2, l3])
        assert result.to_list() == [0, 1, 2]

    def test_duplicates(self):
        """Handle duplicate values correctly."""
        l1 = ListNode.from_list([1, 1, 1])
        l2 = ListNode.from_list([1, 1, 1])
        result = merge_k_lists([l1, l2])
        assert result.to_list() == [1, 1, 1, 1, 1, 1]

    def test_descending_input_order(self):
        """Lists in reverse order should still work."""
        l1 = ListNode.from_list([6])
        l2 = ListNode.from_list([3])
        l3 = ListNode.from_list([1])
        result = merge_k_lists([l1, l2, l3])
        assert result.to_list() == [1, 3, 6]

    def test_all_but_one_empty(self):
        """All lists empty except one."""
        l1 = ListNode.from_list([1, 2, 3])
        result = merge_k_lists([None, None, l1, None])
        assert result.to_list() == [1, 2, 3]

    def test_large_values(self):
        """Handle large integer values."""
        l1 = ListNode.from_list([1000000, 2000000])
        l2 = ListNode.from_list([500000, 1500000])
        result = merge_k_lists([l1, l2])
        assert result.to_list() == [500000, 1000000, 1500000, 2000000]

    def test_negative_values(self):
        """Handle negative values."""
        l1 = ListNode.from_list([-3, -1, 0])
        l2 = ListNode.from_list([-2, 2])
        result = merge_k_lists([l1, l2])
        assert result.to_list() == [-3, -2, -1, 0, 2]

    def test_10_lists(self):
        """Test with many small lists."""
        lists = [ListNode.from_list([i]) for i in range(10)]
        result = merge_k_lists(lists)
        assert result.to_list() == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


class TestMergeKSortedListsNaive:
    """Tests for naive implementation (verification)."""

    def test_agrees_with_heap_solution(self):
        """Naive solution should produce same results."""
        test_cases = [
            ([1, 4, 5], [1, 3, 4], [2, 6]),
            ([1, 2], [1, 3]),
            ([5], [1, 2, 3, 4]),
        ]

        for values_list in test_cases:
            lists = [ListNode.from_list(v) for v in values_list]
            heap_result = merge_k_lists(lists)
            # Create fresh lists for naive approach
            lists2 = [ListNode.from_list(v) for v in values_list]
            naive_result = merge_k_lists_naive(lists2)
            assert heap_result.to_list() == naive_result.to_list()


class TestComplexity:
    """Verify the algorithm handles large inputs efficiently."""

    def test_large_input(self):
        """Test with reasonably large input."""
        # Create 10 lists with 100 elements each
        lists = []
        for i in range(10):
            values = list(range(i, 1000, 10))
            lists.append(ListNode.from_list(values))

        result = merge_k_lists(lists)
        # Should contain all 1000 elements (10 * 100)
        result_list = result.to_list()
        assert len(result_list) == 1000
        # Verify sorted
        assert result_list == sorted(result_list)
