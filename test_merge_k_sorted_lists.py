"""
Tests for Merge k Sorted Lists solution.
"""

import pytest
from merge_k_sorted_lists import (
    merge_k_sorted_lists,
    merge_k_sorted_lists_divide_conquer,
    ListNode,
    list_to_linkedlist,
    linkedlist_to_list,
)


class TestMergeKSortedLists:
    """Test cases for merge k sorted lists."""

    def test_example1(self):
        """Test example 1 from LeetCode."""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_example1_divide_conquer(self):
        """Test example 1 with divide and conquer approach."""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = merge_k_sorted_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_lists(self):
        """Test with empty lists array."""
        lists = []
        result = merge_k_sorted_lists(lists)
        assert result is None

    def test_empty_lists_divide_conquer(self):
        """Test with empty lists array (divide and conquer)."""
        lists = []
        result = merge_k_sorted_lists_divide_conquer(lists)
        assert result is None

    def test_lists_with_empty_list(self):
        """Test with lists containing empty list."""
        lists = [list_to_linkedlist([])]
        result = merge_k_sorted_lists(lists)
        assert result is None

    def test_single_list(self):
        """Test with single non-empty list."""
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_single_list_divide_conquer(self):
        """Test with single non-empty list (divide and conquer)."""
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_sorted_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_lists(self):
        """Test with two lists."""
        lists = [
            list_to_linkedlist([1, 3, 5]),
            list_to_linkedlist([2, 4, 6]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_duplicates_across_lists(self):
        """Test with duplicate values across different lists."""
        lists = [
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1, 1]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1, 1, 1, 1]

    def test_negative_values(self):
        """Test with negative values."""
        lists = [
            list_to_linkedlist([-3, -1, 2]),
            list_to_linkedlist([-2, 0, 4]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [-3, -2, -1, 0, 2, 4]

    def test_already_sorted_single_elements(self):
        """Test with single element in each list, already sorted."""
        lists = [list_to_linkedlist([i]) for i in range(5)]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [0, 1, 2, 3, 4]

    def test_mixed_empty_and_non_empty(self):
        """Test with mix of empty and non-empty lists."""
        lists = [
            list_to_linkedlist([1, 3]),
            None,
            list_to_linkedlist([2, 4]),
            None,
            list_to_linkedlist([5]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5]

    def test_large_values(self):
        """Test with large values."""
        lists = [
            list_to_linkedlist([10000]),
            list_to_linkedlist([-10000]),
            list_to_linkedlist([0]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [-10000, 0, 10000]

    def test_divide_conquer_equivalence(self):
        """Verify both algorithms produce same results."""
        test_cases = [
            [
                list_to_linkedlist([1, 4, 5]),
                list_to_linkedlist([1, 3, 4]),
                list_to_linkedlist([2, 6]),
            ],
            [list_to_linkedlist([1, 2, 3]), list_to_linkedlist([4, 5, 6])],
            [list_to_linkedlist([1])],
            [],
            [None, list_to_linkedlist([1, 2])],
        ]

        for lists in test_cases:
            # Create copies for each algorithm
            lists_heap = [list_to_linkedlist(linkedlist_to_list(l)) if l else None for l in lists]
            lists_dc = [list_to_linkedlist(linkedlist_to_list(l)) if l else None for l in lists]

            result_heap = merge_k_sorted_lists(lists_heap)
            result_dc = merge_k_sorted_lists_divide_conquer(lists_dc)

            assert linkedlist_to_list(result_heap) == linkedlist_to_list(result_dc)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
