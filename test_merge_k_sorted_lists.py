"""
Tests for Merge k Sorted Lists solution.
"""

import pytest
from merge_k_sorted_lists import (
    ListNode,
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
    list_to_linkedlist,
    linkedlist_to_list,
)


class TestMergeKListsHeap:
    """Tests for heap-based solution."""

    def test_empty_list(self):
        """Test with empty input."""
        result = merge_k_lists_heap([])
        assert result is None

    def test_single_empty_list(self):
        """Test with single None in list."""
        result = merge_k_lists_heap([None])
        assert result is None

    def test_single_list(self):
        """Test with single non-empty list."""
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_sorted_lists(self):
        """Test merging two sorted lists."""
        lists = [
            list_to_linkedlist([1, 4, 7]),
            list_to_linkedlist([2, 5, 8]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 4, 5, 7, 8]

    def test_three_sorted_lists(self):
        """Test merging three sorted lists."""
        lists = [
            list_to_linkedlist([1, 3, 5]),
            list_to_linkedlist([2, 4, 6]),
            list_to_linkedlist([0, 7, 8]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [0, 1, 2, 3, 4, 5, 6, 7, 8]

    def test_lists_with_different_lengths(self):
        """Test with lists of varying lengths."""
        lists = [
            list_to_linkedlist([1]),
            list_to_linkedlist([2, 3, 4, 5]),
            list_to_linkedlist([]),
            list_to_linkedlist([6, 7, 8, 9, 10]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_with_duplicates(self):
        """Test with duplicate values across lists."""
        lists = [
            list_to_linkedlist([1, 1, 3]),
            list_to_linkedlist([1, 2, 2]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 1, 1, 2, 2, 3]

    def test_negative_values(self):
        """Test with negative values."""
        lists = [
            list_to_linkedlist([-3, -2, -1]),
            list_to_linkedlist([0, 1, 2]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [-3, -2, -1, 0, 1, 2]

    def test_already_sorted_single_list(self):
        """Test single already sorted list."""
        lists = [list_to_linkedlist([1, 2, 3, 4, 5])]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5]


class TestMergeKListsDivideConquer:
    """Tests for divide-and-conquer solution."""

    def test_empty_list(self):
        """Test with empty input."""
        result = merge_k_lists_divide_conquer([])
        assert result is None

    def test_single_list(self):
        """Test with single non-empty list."""
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_sorted_lists(self):
        """Test merging two sorted lists."""
        lists = [
            list_to_linkedlist([1, 4, 7]),
            list_to_linkedlist([2, 5, 8]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 4, 5, 7, 8]

    def test_three_sorted_lists(self):
        """Test merging three sorted lists."""
        lists = [
            list_to_linkedlist([1, 3, 5]),
            list_to_linkedlist([2, 4, 6]),
            list_to_linkedlist([0, 7, 8]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [0, 1, 2, 3, 4, 5, 6, 7, 8]


class TestSolutions:
    """Verify both solutions produce same results."""

    @pytest.mark.parametrize(
        "lists",
        [
            [[1, 4, 7], [2, 5, 8]],
            [[1, 3, 5], [2, 4, 6], [0, 7, 8]],
            [[1], [2, 3, 4, 5], [], [6, 7, 8, 9, 10]],
            [[1, 1, 3], [1, 2, 2]],
        ],
    )
    def test_both_solutions_match(self, lists):
        """Both solutions should produce identical results."""
        linked_lists = [list_to_linkedlist(l) for l in lists]

        heap_result = merge_k_lists_heap(linked_lists)
        dc_result = merge_k_lists_divide_conquer(linked_lists)

        assert linkedlist_to_list(heap_result) == linkedlist_to_list(dc_result)
