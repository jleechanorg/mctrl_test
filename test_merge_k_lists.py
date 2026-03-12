from __future__ import annotations

import pytest
from merge_k_lists import (
    merge_k_lists_divide_conquer,
    merge_k_lists_heap,
    list_to_linkedlist,
    linkedlist_to_list,
)


class TestMergeKSortedLists:
    """Test cases for Merge k Sorted Lists problem."""

    def test_empty_list(self):
        """Test with empty list of lists."""
        result = merge_k_lists_divide_conquer([])
        assert result is None

        result = merge_k_lists_heap([])
        assert result is None

    def test_single_empty_list(self):
        """Test with single None list."""
        result = merge_k_lists_divide_conquer([None])
        assert linkedlist_to_list(result) == []

        result = merge_k_lists_heap([None])
        assert linkedlist_to_list(result) == []

    def test_single_list(self):
        """Test with single non-empty list."""
        lists = [list_to_linkedlist([1, 2, 3])]
        expected = [1, 2, 3]

        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == expected

        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == expected

    def test_two_lists(self):
        """Test merging two sorted lists."""
        lists = [
            list_to_linkedlist([1, 4, 7]),
            list_to_linkedlist([2, 5, 8])
        ]
        expected = [1, 2, 4, 5, 7, 8]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == expected

        # Test heap version with fresh lists
        lists2 = [
            list_to_linkedlist([1, 4, 7]),
            list_to_linkedlist([2, 5, 8])
        ]
        result = merge_k_lists_heap(lists2)
        assert linkedlist_to_list(result) == expected

    def test_three_lists(self):
        """Test merging three sorted lists."""
        lists = [
            list_to_linkedlist([1, 3, 5]),
            list_to_linkedlist([2, 4, 6]),
            list_to_linkedlist([0, 7, 8])
        ]
        expected = [0, 1, 2, 3, 4, 5, 6, 7, 8]

        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == expected

        # Test heap version with fresh lists
        lists2 = [
            list_to_linkedlist([1, 3, 5]),
            list_to_linkedlist([2, 4, 6]),
            list_to_linkedlist([0, 7, 8])
        ]
        result = merge_k_lists_heap(lists2)
        assert linkedlist_to_list(result) == expected

    def test_lists_with_duplicates(self):
        """Test merging lists with duplicate values."""
        lists = [
            list_to_linkedlist([1, 1, 3]),
            list_to_linkedlist([1, 2, 2])
        ]
        expected = [1, 1, 1, 2, 2, 3]

        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == expected

        # Test heap version with fresh lists
        lists2 = [
            list_to_linkedlist([1, 1, 3]),
            list_to_linkedlist([1, 2, 2])
        ]
        result = merge_k_lists_heap(lists2)
        assert linkedlist_to_list(result) == expected

    def test_uneven_lists(self):
        """Test with lists of varying lengths."""
        lists = [
            list_to_linkedlist([1]),
            list_to_linkedlist([2, 3, 4, 5]),
            list_to_linkedlist([])
        ]
        expected = [1, 2, 3, 4, 5]

        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == expected

        # Test heap version with fresh lists
        lists2 = [
            list_to_linkedlist([1]),
            list_to_linkedlist([2, 3, 4, 5]),
            list_to_linkedlist([])
        ]
        result = merge_k_lists_heap(lists2)
        assert linkedlist_to_list(result) == expected

    def test_negative_numbers(self):
        """Test with negative numbers."""
        lists = [
            list_to_linkedlist([-3, -1, 0]),
            list_to_linkedlist([-2, 2]),
            list_to_linkedlist([1, 3])
        ]
        expected = [-3, -2, -1, 0, 1, 2, 3]

        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == expected

        # Test heap version with fresh lists
        lists2 = [
            list_to_linkedlist([-3, -1, 0]),
            list_to_linkedlist([-2, 2]),
            list_to_linkedlist([1, 3])
        ]
        result = merge_k_lists_heap(lists2)
        assert linkedlist_to_list(result) == expected

    def test_large_k_small_lists(self):
        """Test with many small lists."""
        lists = [list_to_linkedlist([i]) for i in range(10, 0, -1)]
        expected = list(range(1, 11))

        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == expected

        # Test heap version with fresh lists
        lists2 = [list_to_linkedlist([i]) for i in range(10, 0, -1)]
        result = merge_k_lists_heap(lists2)
        assert linkedlist_to_list(result) == expected

    def test_both_algorithms_equal(self):
        """Verify both algorithms produce same results."""
        lists = [
            list_to_linkedlist([1, 5, 9]),
            list_to_linkedlist([2, 6]),
            list_to_linkedlist([3, 7, 8])
        ]

        result_divide = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result_divide) == [1, 2, 3, 5, 6, 7, 8, 9]

        # Test heap version with fresh lists
        lists2 = [
            list_to_linkedlist([1, 5, 9]),
            list_to_linkedlist([2, 6]),
            list_to_linkedlist([3, 7, 8])
        ]
        result_heap = merge_k_lists_heap(lists2)

        assert linkedlist_to_list(result_heap) == [1, 2, 3, 5, 6, 7, 8, 9]
