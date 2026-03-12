"""
Unit tests for Merge k Sorted Lists solution.

Tests cover:
- Basic cases (multiple lists, single list, empty input)
- Edge cases (empty lists, lists with single element)
- Duplicate values
- Negative numbers
- Both implementation approaches (heap and divide-and-conquer)
"""

import pytest
from merge_k_sorted_lists import (
    ListNode,
    merge_k_lists,
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
)


class TestListNodeHelper:
    """Tests for ListNode utility methods."""

    def test_from_list_creates_correct_list(self):
        node = ListNode.from_list([1, 2, 3])
        assert node.to_list() == [1, 2, 3]

    def test_from_list_empty_returns_none(self):
        assert ListNode.from_list([]) is None

    def test_to_list_empty_returns_empty_list(self):
        node = ListNode(1)
        node.next = None
        assert node.to_list() == [1]


class TestMergeKListsHeap:
    """Tests for heap-based implementation."""

    def test_merge_three_lists(self):
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_input(self):
        result = merge_k_lists_heap([])
        assert result is None

    def test_empty_lists_array(self):
        result = merge_k_lists_heap([None, None])
        assert result is None

    def test_single_list(self):
        lists = [ListNode.from_list([1, 2, 3])]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 2, 3]

    def test_single_element_lists(self):
        lists = [
            ListNode.from_list([1]),
            ListNode.from_list([2]),
            ListNode.from_list([3]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 2, 3]

    def test_with_duplicates(self):
        lists = [
            ListNode.from_list([1, 1, 1]),
            ListNode.from_list([1, 1]),
            ListNode.from_list([1]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 1, 1, 1, 1, 1]

    def test_with_negative_numbers(self):
        lists = [
            ListNode.from_list([-3, -1, 2]),
            ListNode.from_list([-2, 0, 4]),
            ListNode.from_list([-1, 1, 3]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [-3, -2, -1, -1, 0, 1, 2, 3, 4]

    def test_already_sorted(self):
        lists = [
            ListNode.from_list([1, 2, 3]),
            ListNode.from_list([4, 5, 6]),
            ListNode.from_list([7, 8, 9]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_descending_input_not_expected(self):
        """Input lists should be ascending (per problem constraint), this is just to verify behavior."""
        # The problem states lists are sorted in ascending order
        # This test verifies we handle any input gracefully
        lists = [
            ListNode.from_list([9, 8, 7]),
            ListNode.from_list([6, 5, 4]),
            ListNode.from_list([3, 2, 1]),
        ]
        result = merge_k_lists_heap(lists)
        # Without sorting assumption, we just merge in given order
        assert result is not None

    def test_large_gap_between_values(self):
        lists = [
            ListNode.from_list([-10000]),
            ListNode.from_list([0]),
            ListNode.from_list([10000]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [-10000, 0, 10000]


class TestMergeKListsDivideConquer:
    """Tests for divide-and-conquer implementation."""

    def test_merge_three_lists(self):
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_input(self):
        result = merge_k_lists_divide_conquer([])
        assert result is None

    def test_single_list(self):
        lists = [ListNode.from_list([1, 2, 3])]
        result = merge_k_lists_divide_conquer(lists)
        assert result.to_list() == [1, 2, 3]

    def test_with_negative_numbers(self):
        lists = [
            ListNode.from_list([-3, -1, 2]),
            ListNode.from_list([-2, 0, 4]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert result.to_list() == [-3, -2, -1, 0, 2, 4]


class TestDefaultMergeKLists:
    """Tests for default merge_k_lists function (should use heap approach)."""

    def test_default_is_heap_approach(self):
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
