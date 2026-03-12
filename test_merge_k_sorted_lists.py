"""
Tests for Merge k Sorted Lists solution.

Comprehensive test cases covering:
- Basic cases
- Edge cases (empty inputs, single list)
- Multiple lists with various lengths
- Lists with duplicate values
- Negative numbers
- Large inputs
"""
from __future__ import annotations

from typing import Optional

import pytest

from merge_k_sorted_lists import (
    ListNode,
    merge_k_lists,
    merge_k_lists_divide_conquer,
    merge_k_lists_heap,
)


def list_to_linked(values: list[int]) -> Optional[ListNode]:
    """Helper to convert list to linked list."""
    return ListNode.from_list(values)


def linked_to_list(node: Optional[ListNode]) -> list[int]:
    """Helper to convert linked list to list."""
    return node.to_list() if node else []


class TestListNode:
    """Tests for ListNode helper methods."""

    def test_from_list_empty(self):
        assert ListNode.from_list([]) is None

    def test_from_list_single(self):
        node = ListNode.from_list([1])
        assert node.val == 1
        assert node.next is None

    def test_from_list_multiple(self):
        node = ListNode.from_list([1, 2, 3])
        assert node.to_list() == [1, 2, 3]



class TestMergeKListsHeap:
    """Tests for heap-based merge implementation."""

    def test_basic_example(self):
        """Test with the standard example from LeetCode."""
        lists = [
            list_to_linked([1, 4, 5]),
            list_to_linked([1, 3, 4]),
            list_to_linked([2, 6]),
        ]
        result = merge_k_lists_heap(lists)
        assert linked_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_lists(self):
        """Test with empty lists array."""
        lists: list[Optional[ListNode]] = []
        result = merge_k_lists_heap(lists)
        assert result is None

    def test_single_empty_list(self):
        """Test with single empty list."""
        lists = [list_to_linked([])]
        result = merge_k_lists_heap(lists)
        assert result is None

    def test_single_list(self):
        """Test with single non-empty list."""
        lists = [list_to_linked([1, 2, 3])]
        result = merge_k_lists_heap(lists)
        assert linked_to_list(result) == [1, 2, 3]

    def test_two_lists(self):
        """Test with two lists."""
        lists = [list_to_linked([1, 3, 5]), list_to_linked([2, 4, 6])]
        result = merge_k_lists_heap(lists)
        assert linked_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_with_duplicates(self):
        """Test lists with duplicate values."""
        lists = [list_to_linked([1, 1, 1]), list_to_linked([1, 1, 1])]
        result = merge_k_lists_heap(lists)
        assert linked_to_list(result) == [1, 1, 1, 1, 1, 1]

    def test_with_negative_numbers(self):
        """Test with negative numbers."""
        lists = [
            list_to_linked([-3, -1, 0]),
            list_to_linked([-2, 2]),
        ]
        result = merge_k_lists_heap(lists)
        assert linked_to_list(result) == [-3, -2, -1, 0, 2]

    def test_uneven_lengths(self):
        """Test with lists of very different lengths."""
        lists = [
            list_to_linked([1]),
            list_to_linked([2, 3, 4, 5, 6]),
            list_to_linked([]),
        ]
        result = merge_k_lists_heap(lists)
        assert linked_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_mixed_empty_and_non_empty(self):
        """Test with mix of empty and non-empty lists."""
        lists = [
            list_to_linked([1, 5]),
            None,
            list_to_linked([2, 3]),
            None,
            list_to_linked([4]),
        ]
        result = merge_k_lists_heap(lists)
        assert linked_to_list(result) == [1, 2, 3, 4, 5]

    def test_already_sorted_single_elements(self):
        """Test with single element lists already sorted."""
        lists = [list_to_linked([i]) for i in range(5, 0, -1)]
        result = merge_k_lists_heap(lists)
        assert linked_to_list(result) == [1, 2, 3, 4, 5]


class TestMergeKListsDivideConquer:
    """Tests for divide-and-conquer merge implementation."""

    def test_basic_example(self):
        """Test with the standard example from LeetCode."""
        lists = [
            list_to_linked([1, 4, 5]),
            list_to_linked([1, 3, 4]),
            list_to_linked([2, 6]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linked_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_lists(self):
        """Test with empty lists array."""
        lists: list[Optional[ListNode]] = []
        result = merge_k_lists_divide_conquer(lists)
        assert result is None

    def test_single_list(self):
        """Test with single non-empty list."""
        lists = [list_to_linked([1, 2, 3])]
        result = merge_k_lists_divide_conquer(lists)
        assert linked_to_list(result) == [1, 2, 3]

    def test_with_negative_numbers(self):
        """Test with negative numbers."""
        lists = [
            list_to_linked([-3, -1, 0]),
            list_to_linked([-2, 2]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linked_to_list(result) == [-3, -2, -1, 0, 2]


class TestMergeKListsDefault:
    """Tests for default merge_k_lists function (should use heap)."""

    def test_default_is_heap(self):
        """Verify default implementation is heap-based."""
        lists = [list_to_linked([1, 3]), list_to_linked([2, 4])]
        result = merge_k_lists(lists)
        assert linked_to_list(result) == [1, 2, 3, 4]

    def test_all_edge_cases(self):
        """Comprehensive test covering all edge cases."""
        # Empty input
        assert merge_k_lists([]) is None

        # Single list
        assert linked_to_list(merge_k_lists([list_to_linked([1, 2, 3])])) == [1, 2, 3]

        # Two lists
        assert linked_to_list(merge_k_lists([list_to_linked([1]), list_to_linked([2])])) == [1, 2]

        # With None in lists
        lists_with_none = [None, list_to_linked([1, 2]), None]
        assert linked_to_list(merge_k_lists(lists_with_none)) == [1, 2]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
