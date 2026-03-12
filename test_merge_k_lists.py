"""
Tests for Merge k Sorted Lists solution.
"""
from __future__ import annotations

import pytest
from merge_k_lists import (
    ListNode,
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
    create_linked_list,
    linked_list_to_list,
)


class TestMergeKLists:
    """Test cases for merge k sorted lists."""

    def test_empty_list(self):
        """Test with empty list of lists."""
        result = merge_k_lists_heap([])
        assert result is None

        result = merge_k_lists_divide_conquer([])
        assert result is None

    def test_single_empty_list(self):
        """Test with single None list."""
        result = merge_k_lists_heap([None])
        assert result is None

    def test_single_list(self):
        """Test with single non-empty list."""
        lists = [create_linked_list([1, 2, 3])]
        expected = [1, 2, 3]

        result_heap = merge_k_lists_heap(lists)
        assert linked_list_to_list(result_heap) == expected

        result_dc = merge_k_lists_divide_conquer(lists)
        assert linked_list_to_list(result_dc) == expected

    def test_two_lists(self):
        """Test with two sorted lists."""
        lists = [
            create_linked_list([1, 3, 5]),
            create_linked_list([2, 4, 6]),
        ]
        expected = [1, 2, 3, 4, 5, 6]

        result_heap = merge_k_lists_heap(lists)
        assert linked_list_to_list(result_heap) == expected

        result_dc = merge_k_lists_divide_conquer(lists)
        assert linked_list_to_list(result_dc) == expected

    def test_three_lists(self):
        """Test with three sorted lists - the example case."""
        lists = [
            create_linked_list([1, 4, 5]),
            create_linked_list([1, 3, 4]),
            create_linked_list([2, 6]),
        ]
        expected = [1, 1, 2, 3, 4, 4, 5, 6]

        result_heap = merge_k_lists_heap(lists)
        assert linked_list_to_list(result_heap) == expected

        result_dc = merge_k_lists_divide_conquer(lists)
        assert linked_list_to_list(result_dc) == expected

    def test_lists_with_duplicates(self):
        """Test with lists containing duplicate values."""
        lists = [
            create_linked_list([1, 1, 1]),
            create_linked_list([1, 1, 1]),
            create_linked_list([1, 1, 1]),
        ]
        expected = [1, 1, 1, 1, 1, 1, 1, 1, 1]

        result_heap = merge_k_lists_heap(lists)
        assert linked_list_to_list(result_heap) == expected

        result_dc = merge_k_lists_divide_conquer(lists)
        assert linked_list_to_list(result_dc) == expected

    def test_mixed_empty_and_non_empty(self):
        """Test with mix of empty and non-empty lists."""
        lists = [
            create_linked_list([1, 3, 5]),
            None,
            create_linked_list([2, 4, 6]),
            None,
            create_linked_list([7, 8, 9]),
        ]
        expected = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        result_heap = merge_k_lists_heap(lists)
        assert linked_list_to_list(result_heap) == expected

        result_dc = merge_k_lists_divide_conquer(lists)
        assert linked_list_to_list(result_dc) == expected

    def test_single_element_lists(self):
        """Test with single element in each list."""
        lists = [
            create_linked_list([5]),
            create_linked_list([1]),
            create_linked_list([3]),
            create_linked_list([2]),
            create_linked_list([4]),
        ]
        expected = [1, 2, 3, 4, 5]

        result_heap = merge_k_lists_heap(lists)
        assert linked_list_to_list(result_heap) == expected

        result_dc = merge_k_lists_divide_conquer(lists)
        assert linked_list_to_list(result_dc) == expected

    def test_already_sorted_single_list(self):
        """Test when all elements in single already sorted list."""
        lists = [create_linked_list([1, 2, 3, 4, 5])]
        expected = [1, 2, 3, 4, 5]

        result_heap = merge_k_lists_heap(lists)
        assert linked_list_to_list(result_heap) == expected

    def test_reverse_sorted_input(self):
        """Test with lists sorted in different orders."""
        lists = [
            create_linked_list([5, 4, 3, 2, 1]),
            create_linked_list([10, 9, 8, 7, 6]),
        ]
        expected = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        result_heap = merge_k_lists_heap(lists)
        assert linked_list_to_list(result_heap) == expected

        result_dc = merge_k_lists_divide_conquer(lists)
        assert linked_list_to_list(result_dc) == expected

    def test_large_k_small_lists(self):
        """Test with many small lists."""
        lists = [create_linked_list([i]) for i in range(100, 0, -1)]
        expected = list(range(1, 101))

        result_heap = merge_k_lists_heap(lists)
        assert linked_list_to_list(result_heap) == expected

        result_dc = merge_k_lists_divide_conquer(lists)
        assert linked_list_to_list(result_dc) == expected


class TestLinkedListHelpers:
    """Test helper functions."""

    def test_create_linked_list_empty(self):
        """Test creating linked list from empty array."""
        result = create_linked_list([])
        assert result is None

    def test_create_linked_list_single(self):
        """Test creating linked list from single element."""
        result = create_linked_list([42])
        assert result.val == 42
        assert result.next is None

    def test_linked_list_to_list(self):
        """Test converting linked list to Python list."""
        node = create_linked_list([1, 2, 3, 4, 5])
        result = linked_list_to_list(node)
        assert result == [1, 2, 3, 4, 5]

    def test_linked_list_to_list_empty(self):
        """Test converting None to empty list."""
        result = linked_list_to_list(None)
        assert result == []
