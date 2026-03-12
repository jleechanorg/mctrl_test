"""
Unit tests for Merge k Sorted Lists (LeetCode #23)

Test Cases:
1. Basic case with multiple sorted lists
2. Empty list of lists
3. List with one empty list
4. Single list with multiple elements
5. Lists with varying lengths
6. Lists with duplicate values
7. Already merged single-element lists
8. Large lists to test performance
"""

import pytest
from merge_k_sorted_lists import (
    ListNode,
    merge_k_lists_divide_conquer,
    merge_k_lists_heap,
    list_to_linkedlist,
    linkedlist_to_list,
)


class TestMergeKSortedLists:
    """Test suite for merge k sorted lists solution."""

    def test_basic_case(self):
        """Test basic case from LeetCode example."""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6])
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_lists(self):
        """Test with empty list of lists."""
        lists = []
        result = merge_k_lists_divide_conquer(lists)
        assert result is None

    def test_single_empty_list(self):
        """Test with single empty list."""
        lists = [None]
        result = merge_k_lists_divide_conquer(lists)
        assert result is None

    def test_single_list(self):
        """Test with single list containing multiple elements."""
        lists = [list_to_linkedlist([1, 2, 3, 4, 5])]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5]

    def test_lists_with_varying_lengths(self):
        """Test with lists of different lengths."""
        lists = [
            list_to_linkedlist([1]),
            list_to_linkedlist([2, 3, 4, 5]),
            list_to_linkedlist([])
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5]

    def test_duplicate_values(self):
        """Test with duplicate values across lists."""
        lists = [
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1]),
            list_to_linkedlist([1])
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1]

    def test_negative_numbers(self):
        """Test with negative numbers."""
        lists = [
            list_to_linkedlist([-3, -1, 0]),
            list_to_linkedlist([-2, 2]),
            list_to_linkedlist([-1, 1, 3])
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [-3, -2, -1, -1, 0, 1, 2, 3]

    def test_single_element_lists(self):
        """Test with many single-element lists."""
        lists = [list_to_linkedlist([i]) for i in [5, 2, 8, 1, 9, 3]]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 5, 8, 9]

    def test_large_values(self):
        """Test with large integer values."""
        lists = [
            list_to_linkedlist([1000000, 2000000]),
            list_to_linkedlist([500000, 1500000]),
            list_to_linkedlist([300000, 400000])
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [300000, 400000, 500000, 1000000, 1500000, 2000000]

    def test_already_sorted(self):
        """Test when all elements are already in order."""
        lists = [
            list_to_linkedlist([1, 2, 3]),
            list_to_linkedlist([4, 5, 6]),
            list_to_linkedlist([7, 8, 9])
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_heap_method_matches_divide_conquer(self):
        """Test that both methods produce the same result."""
        lists_dc = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6])
        ]
        lists_heap = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6])
        ]
        result_dc = merge_k_lists_divide_conquer(lists_dc)
        result_heap = merge_k_lists_heap(lists_heap)
        assert linkedlist_to_list(result_dc) == linkedlist_to_list(result_heap)

    def test_heap_method_empty_input(self):
        """Test heap method with empty input."""
        lists = []
        result = merge_k_lists_heap(lists)
        assert result is None

    def test_heap_method_single_empty_list(self):
        """Test heap method with single None list."""
        lists = [None]
        result = merge_k_lists_heap(lists)
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
