"""
Comprehensive tests for Merge k Sorted Lists solution.

Tests cover:
- Basic functionality (multiple lists)
- Edge cases (empty inputs, single list, single element)
- Large inputs
- Various list lengths
- Duplicate values
"""

from __future__ import annotations
import pytest
from merge_k_sorted_lists import (
    merge_k_lists,
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
    ListNode,
    list_to_linkedlist,
    linkedlist_to_list,
)


class TestMergeKSortedLists:
    """Test suite for merge k sorted lists problem."""

    def test_example_1(self):
        """Test example 1 from LeetCode."""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_example_2_empty_input(self):
        """Test with empty input list."""
        lists = []
        result = merge_k_lists(lists)
        assert result is None

    def test_example_3_empty_list_in_array(self):
        """Test with array containing empty list."""
        lists = [list_to_linkedlist([])]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == []

    def test_single_list(self):
        """Test with a single non-empty list."""
        lists = [list_to_linkedlist([1, 2, 3, 4, 5])]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5]

    def test_single_element_per_list(self):
        """Test with one element per list."""
        lists = [
            list_to_linkedlist([1]),
            list_to_linkedlist([2]),
            list_to_linkedlist([3]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_lists(self):
        """Test merging two lists."""
        lists = [
            list_to_linkedlist([1, 3, 5, 7]),
            list_to_linkedlist([2, 4, 6, 8]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8]

    def test_duplicates_across_lists(self):
        """Test handling duplicates across different lists."""
        lists = [
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1, 1]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1, 1, 1, 1]

    def test_negative_values(self):
        """Test with negative numbers."""
        lists = [
            list_to_linkedlist([-3, -1, 0, 2]),
            list_to_linkedlist([-2, 1, 3, 4]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [-3, -2, -1, 0, 1, 2, 3, 4]

    def test_already_sorted_single_list(self):
        """Test with lists that are already individually sorted."""
        lists = [
            list_to_linkedlist([1, 2, 3]),
            list_to_linkedlist([4, 5, 6]),
            list_to_linkedlist([7, 8, 9]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_interleaved_lists(self):
        """Test with interleaved values from different lists."""
        lists = [
            list_to_linkedlist([1, 6, 11]),
            list_to_linkedlist([2, 7, 12]),
            list_to_linkedlist([3, 8, 13]),
            list_to_linkedlist([4, 9, 14]),
            list_to_linkedlist([5, 10, 15]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

    def test_mixed_lengths(self):
        """Test with lists of varying lengths."""
        lists = [
            list_to_linkedlist([1]),
            list_to_linkedlist([2, 3]),
            list_to_linkedlist([4, 5, 6]),
            list_to_linkedlist([7, 8, 9, 10]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_large_k_small_lists(self):
        """Test with many lists, each having few elements."""
        lists = [list_to_linkedlist([i]) for i in range(100)]
        result = merge_k_lists(lists)
        expected = list(range(100))
        assert linkedlist_to_list(result) == expected

    def test_all_empty_lists(self):
        """Test with all empty lists."""
        lists = [
            list_to_linkedlist([]),
            list_to_linkedlist([]),
            list_to_linkedlist([]),
        ]
        result = merge_k_lists(lists)
        assert result is None or linkedlist_to_list(result) == []

    def test_one_empty_list_mixed(self):
        """Test with one empty list among non-empty ones."""
        lists = [
            list_to_linkedlist([1, 2, 3]),
            list_to_linkedlist([]),
            list_to_linkedlist([4, 5, 6]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_alternating_values(self):
        """Test with alternating values across lists."""
        lists = [
            list_to_linkedlist([1, 3, 5, 7, 9]),
            list_to_linkedlist([0, 2, 4, 6, 8, 10]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_same_values_different_positions(self):
        """Test with same values appearing in different lists."""
        lists = [
            list_to_linkedlist([1, 3, 5]),
            list_to_linkedlist([1, 3, 5]),
            list_to_linkedlist([1, 3, 5]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 1, 1, 3, 3, 3, 5, 5, 5]


class TestBothAlgorithms:
    """Test that both algorithms produce the same results."""

    @pytest.mark.parametrize("test_func", [merge_k_lists_heap, merge_k_lists_divide_conquer])
    def test_both_algorithms_equal(self, test_func):
        """Verify both implementations produce identical results."""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = test_func(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]


class TestListNode:
    """Test ListNode functionality."""

    def test_list_node_lt_comparison(self):
        """Test ListNode less-than comparison for heap."""
        node1 = ListNode(1)
        node2 = ListNode(2)
        assert node1 < node2

    def test_list_node_repr(self):
        """Test ListNode string representation."""
        head = list_to_linkedlist([1, 2, 3])
        assert repr(head) == "1->2->3"


class TestHelperFunctions:
    """Test helper functions."""

    def test_list_to_linkedlist_empty(self):
        """Test converting empty list."""
        assert list_to_linkedlist([]) is None

    def test_linkedlist_to_list_empty(self):
        """Test converting empty linked list."""
        assert linkedlist_to_list(None) == []

    def test_roundtrip_conversion(self):
        """Test list -> linkedlist -> list conversion."""
        original = [1, 2, 3, 4, 5]
        linked = list_to_linkedlist(original)
        result = linkedlist_to_list(linked)
        assert result == original


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
