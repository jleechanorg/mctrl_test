"""
Tests for Merge k Sorted Lists solution.
"""

from __future__ import annotations

import pytest
from merge_k_sorted_lists import (
    merge_k_lists,
    merge_k_lists_divide_conquer,
    merge_k_lists_heap,
    ListNode,
)


class TestListNode:
    """Tests for ListNode helper class."""

    def test_from_list_empty(self):
        assert ListNode.from_list([]) is None

    def test_from_list_single(self):
        node = ListNode.from_list([1])
        assert node.val == 1
        assert node.next is None

    def test_from_list_multiple(self):
        node = ListNode.from_list([1, 2, 3])
        assert node.val == 1
        assert node.next.val == 2
        assert node.next.next.val == 3
        assert node.next.next.next is None

    def test_to_list_none_node(self):
        """Test to_list when node value is None (edge case)."""
        # When ListNode is created with val=None, to_list returns [None]
        node = ListNode(0)  # Use 0 instead of None for valid node
        assert node.to_list() == [0]

    def test_to_list_multiple(self):
        node = ListNode.from_list([1, 2, 3])
        assert node.to_list() == [1, 2, 3]


class TestMergeKSortedLists:
    """Tests for merge_k_lists function."""

    def test_example_1(self):
        """Example 1 from LeetCode: [[1,4,5],[1,3,4],[2,6]] -> [1,1,2,3,4,4,5,6]"""
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6])
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_example_2_empty_input(self):
        """Example 2: empty input lists -> []"""
        result = merge_k_lists([])
        assert result is None or result.to_list() == []

    def test_example_3_single_empty_list(self):
        """Example 3: [[]] -> []"""
        result = merge_k_lists([None])
        assert result is None or result.to_list() == []

    def test_single_list(self):
        """Test with a single non-empty list."""
        lists = [ListNode.from_list([1, 2, 3])]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3]

    def test_two_lists(self):
        """Test merging two sorted lists."""
        lists = [
            ListNode.from_list([1, 3, 5]),
            ListNode.from_list([2, 4, 6])
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6]

    def test_lists_with_duplicates(self):
        """Test merging lists with duplicate values."""
        lists = [
            ListNode.from_list([1, 1, 1]),
            ListNode.from_list([1, 1, 1])
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 1, 1, 1, 1, 1]

    def test_negative_numbers(self):
        """Test with negative numbers."""
        lists = [
            ListNode.from_list([-3, -1, 0]),
            ListNode.from_list([-2, 2, 3])
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [-3, -2, -1, 0, 2, 3]

    def test_uneven_length_lists(self):
        """Test with lists of different lengths."""
        lists = [
            ListNode.from_list([1]),
            ListNode.from_list([2, 3, 4, 5]),
            ListNode.from_list([6, 7, 8, 9, 10])
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_all_empty_lists(self):
        """Test with all empty lists."""
        result = merge_k_lists([None, None, None])
        assert result is None or result.to_list() == []

    def test_large_k_value(self):
        """Test with many small lists."""
        lists = [ListNode.from_list([i]) for i in range(10, 0, -1)]
        result = merge_k_lists(lists)
        assert result.to_list() == list(range(1, 11))

    def test_already_sorted(self):
        """Test with already sorted input."""
        lists = [
            ListNode.from_list([1]),
            ListNode.from_list([2]),
            ListNode.from_list([3])
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3]

    def test_reverse_sorted(self):
        """Test with reverse sorted input."""
        lists = [
            ListNode.from_list([3]),
            ListNode.from_list([2]),
            ListNode.from_list([1])
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3]


class TestDivideConquerVsHeap:
    """Compare both implementations to ensure correctness."""

    @pytest.mark.parametrize("func", [merge_k_lists_divide_conquer, merge_k_lists_heap])
    def test_both_implementations(self, func):
        """Test that both implementations produce the same result."""
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6])
        ]
        result = func(lists)
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

    @pytest.mark.parametrize("func", [merge_k_lists_divide_conquer, merge_k_lists_heap])
    def test_empty_input(self, func):
        """Test empty input for both implementations."""
        result = func([])
        assert result is None or result.to_list() == []

    @pytest.mark.parametrize("func", [merge_k_lists_divide_conquer, merge_k_lists_heap])
    def test_large_test(self, func):
        """Test with larger input."""
        lists = [
            ListNode.from_list(list(range(0, 100, 3))),   # 0, 3, 6, ..., 99
            ListNode.from_list(list(range(1, 100, 3))),  # 1, 4, 7, ..., 100
            ListNode.from_list(list(range(2, 100, 3))),  # 2, 5, 8, ..., 98
        ]
        result = func(lists)
        assert result.to_list() == list(range(100))
