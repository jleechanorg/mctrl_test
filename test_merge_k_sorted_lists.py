"""
Tests for Merge k Sorted Lists solution.
"""

from __future__ import annotations

from merge_k_sorted_lists import (
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
    create_linked_list,
    linked_list_to_list,
)


class TestMergeKSortedLists:
    """Test cases for merge k sorted lists."""

    def test_empty_list(self):
        """Test with empty list of lists."""
        assert linked_list_to_list(merge_k_lists_heap([])) == []
        assert linked_list_to_list(merge_k_lists_divide_conquer([])) == []

    def test_single_empty_list(self):
        """Test with single None list."""
        assert linked_list_to_list(merge_k_lists_heap([None])) == []
        assert linked_list_to_list(merge_k_lists_divide_conquer([None])) == []

    def test_single_list(self):
        """Test with single non-empty list."""
        lists = [create_linked_list([1, 2, 3])]
        expected = [1, 2, 3]

        assert linked_list_to_list(merge_k_lists_heap(lists)) == expected

        lists2 = [create_linked_list([1, 2, 3])]
        assert linked_list_to_list(merge_k_lists_divide_conquer(lists2)) == expected

    def test_two_lists(self):
        """Test merging two sorted lists."""
        lists = [create_linked_list([1, 4, 5]), create_linked_list([1, 3, 4])]
        expected = [1, 1, 3, 4, 4, 5]

        assert linked_list_to_list(merge_k_lists_heap(lists)) == expected

        lists2 = [create_linked_list([1, 4, 5]), create_linked_list([1, 3, 4])]
        assert linked_list_to_list(merge_k_lists_divide_conquer(lists2)) == expected

    def test_three_lists(self):
        """Test merging three sorted lists."""
        lists = [
            create_linked_list([1, 4, 7, 10]),
            create_linked_list([2, 5, 8]),
            create_linked_list([3, 6, 9]),
        ]
        expected = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        assert linked_list_to_list(merge_k_lists_heap(lists)) == expected

        lists2 = [
            create_linked_list([1, 4, 7, 10]),
            create_linked_list([2, 5, 8]),
            create_linked_list([3, 6, 9]),
        ]
        assert linked_list_to_list(merge_k_lists_divide_conquer(lists2)) == expected

    def test_lists_with_duplicates(self):
        """Test merging lists with duplicate values."""
        lists = [
            create_linked_list([1, 1, 1]),
            create_linked_list([1, 1, 2]),
            create_linked_list([1, 2, 2]),
        ]
        # 6 ones (3+2+1), 3 twos (1+2)
        expected = [1, 1, 1, 1, 1, 1, 2, 2, 2]

        assert linked_list_to_list(merge_k_lists_heap(lists)) == expected

        lists2 = [
            create_linked_list([1, 1, 1]),
            create_linked_list([1, 1, 2]),
            create_linked_list([1, 2, 2]),
        ]
        assert linked_list_to_list(merge_k_lists_divide_conquer(lists2)) == expected

    def test_mixed_empty_and_non_empty(self):
        """Test with mix of empty and non-empty lists."""
        lists = [None, create_linked_list([1, 2, 3]), None, create_linked_list([4, 5])]
        expected = [1, 2, 3, 4, 5]

        assert linked_list_to_list(merge_k_lists_heap(lists)) == expected

        lists2 = [None, create_linked_list([1, 2, 3]), None, create_linked_list([4, 5])]
        assert linked_list_to_list(merge_k_lists_divide_conquer(lists2)) == expected

    def test_single_element_lists(self):
        """Test with lists containing single elements."""
        lists = [
            create_linked_list([1]),
            create_linked_list([2]),
            create_linked_list([3]),
            create_linked_list([0]),
        ]
        expected = [0, 1, 2, 3]

        assert linked_list_to_list(merge_k_lists_heap(lists)) == expected

        lists2 = [
            create_linked_list([1]),
            create_linked_list([2]),
            create_linked_list([3]),
            create_linked_list([0]),
        ]
        assert linked_list_to_list(merge_k_lists_divide_conquer(lists2)) == expected

    def test_negative_numbers(self):
        """Test with negative numbers."""
        lists = [
            create_linked_list([-3, -1, 2]),
            create_linked_list([-5, -2, 0]),
            create_linked_list([-4, 1]),
        ]
        expected = [-5, -4, -3, -2, -1, 0, 1, 2]

        assert linked_list_to_list(merge_k_lists_heap(lists)) == expected

        lists2 = [
            create_linked_list([-3, -1, 2]),
            create_linked_list([-5, -2, 0]),
            create_linked_list([-4, 1]),
        ]
        assert linked_list_to_list(merge_k_lists_divide_conquer(lists2)) == expected

    def test_large_values(self):
        """Test with large values."""
        lists = [
            create_linked_list([10**6, 10**6 + 5]),
            create_linked_list([10**6 + 1, 10**6 + 10]),
            create_linked_list([10**6 - 10, 10**6 - 5]),
        ]
        # Sorted: 999990, 999995, 1000000, 1000001, 1000005, 1000010
        expected = [
            10**6 - 10,
            10**6 - 5,
            10**6,
            10**6 + 1,
            10**6 + 5,
            10**6 + 10,
        ]

        assert linked_list_to_list(merge_k_lists_heap(lists)) == expected

        lists2 = [
            create_linked_list([10**6, 10**6 + 5]),
            create_linked_list([10**6 + 1, 10**6 + 10]),
            create_linked_list([10**6 - 10, 10**6 - 5]),
        ]
        assert linked_list_to_list(merge_k_lists_divide_conquer(lists2)) == expected


if __name__ == "__main__":
    # Run pytest if available
    try:
        import pytest
        pytest.main([__file__, "-v"])
    except ImportError:
        print("pytest not available")
