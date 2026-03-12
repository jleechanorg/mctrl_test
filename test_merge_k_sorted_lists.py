"""
Tests for LeetCode 23: Merge k Sorted Lists
"""
from __future__ import annotations

import pytest
from merge_k_sorted_lists import (
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
    list_to_linkedlist,
    linkedlist_to_list,
    ListNode,
)


class TestMergeKSortedLists:
    """Test cases for merge k sorted lists solutions."""

    def test_example_1_heap(self):
        """Test example 1 with heap approach."""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_example_1_divide_conquer(self):
        """Test example 1 with divide and conquer approach."""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_lists_heap(self):
        """Test with empty list of lists."""
        lists = []
        result = merge_k_lists_heap(lists)
        assert result is None

    def test_empty_lists_divide_conquer(self):
        """Test with empty list of lists."""
        lists = []
        result = merge_k_lists_divide_conquer(lists)
        assert result is None

    def test_lists_with_empty_list_heap(self):
        """Test with list containing empty list."""
        lists = [[]]
        result = merge_k_lists_heap(lists)
        assert result is None

    def test_lists_with_empty_list_divide_conquer(self):
        """Test with list containing empty list."""
        lists = [list_to_linkedlist([])]
        result = merge_k_lists_divide_conquer(lists)
        assert result is None

    def test_single_list_heap(self):
        """Test with a single list."""
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_single_list_divide_conquer(self):
        """Test with a single list."""
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_lists_heap(self):
        """Test with two lists."""
        lists = [
            list_to_linkedlist([1, 3, 5]),
            list_to_linkedlist([2, 4, 6]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_two_lists_divide_conquer(self):
        """Test with two lists."""
        lists = [
            list_to_linkedlist([1, 3, 5]),
            list_to_linkedlist([2, 4, 6]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_already_sorted_heap(self):
        """Test with already sorted lists."""
        lists = [
            list_to_linkedlist([1]),
            list_to_linkedlist([2]),
            list_to_linkedlist([3]),
            list_to_linkedlist([4]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4]

    def test_already_sorted_divide_conquer(self):
        """Test with already sorted lists."""
        lists = [
            list_to_linkedlist([1]),
            list_to_linkedlist([2]),
            list_to_linkedlist([3]),
            list_to_linkedlist([4]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4]

    def test_reverse_sorted_heap(self):
        """Test with reverse sorted input (but lists are sorted internally)."""
        lists = [
            list_to_linkedlist([5, 4, 3, 2, 1]),  # Note: internal list must be sorted
            list_to_linkedlist([10, 9, 8, 7, 6]),
        ]
        # Since we assume sorted input, this is just to verify we maintain order
        lists_sorted = [
            list_to_linkedlist([1, 2, 3, 4, 5]),
            list_to_linkedlist([6, 7, 8, 9, 10]),
        ]
        result = merge_k_lists_heap(lists_sorted)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_negative_numbers_heap(self):
        """Test with negative numbers."""
        lists = [
            list_to_linkedlist([-5, -3, -1]),
            list_to_linkedlist([-4, -2, 0]),
            list_to_linkedlist([-6, -2, 2]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [-6, -5, -4, -3, -2, -2, -1, 0, 2]

    def test_negative_numbers_divide_conquer(self):
        """Test with negative numbers."""
        lists = [
            list_to_linkedlist([-5, -3, -1]),
            list_to_linkedlist([-4, -2, 0]),
            list_to_linkedlist([-6, -2, 2]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [-6, -5, -4, -3, -2, -2, -1, 0, 2]

    def test_duplicates_heap(self):
        """Test with many duplicate values."""
        lists = [
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1, 1]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1, 1, 1, 1]

    def test_duplicates_divide_conquer(self):
        """Test with many duplicate values."""
        lists = [
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1, 1]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1, 1, 1, 1]

    def test_large_k_heap(self):
        """Test with many small lists (k=10)."""
        lists = [list_to_linkedlist([i]) for i in range(10)]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_large_k_divide_conquer(self):
        """Test with many small lists (k=10)."""
        lists = [list_to_linkedlist([i]) for i in range(10)]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_single_element_lists_heap(self):
        """Test with single element in each list."""
        lists = [
            list_to_linkedlist([5]),
            list_to_linkedlist([2]),
            list_to_linkedlist([8]),
            list_to_linkedlist([1]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 5, 8]

    def test_single_element_lists_divide_conquer(self):
        """Test with single element in each list."""
        lists = [
            list_to_linkedlist([5]),
            list_to_linkedlist([2]),
            list_to_linkedlist([8]),
            list_to_linkedlist([1]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 5, 8]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
