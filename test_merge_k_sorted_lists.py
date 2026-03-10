"""Tests for Merge k Sorted Lists solution."""
from __future__ import annotations

import pytest
from merge_k_sorted_lists import (
    ListNode,
    merge_k_lists,
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
    list_to_linked_list,
    linked_list_to_list,
)


class TestListConversion:
    """Test utility functions for list <-> linked list conversion."""

    def test_empty_list_to_linked_list(self):
        assert list_to_linked_list([]) is None

    def test_single_element_list(self):
        result = list_to_linked_list([1])
        assert result.val == 1
        assert result.next is None

    def test_multiple_elements_list(self):
        result = list_to_linked_list([1, 2, 3])
        assert result.val == 1
        assert result.next.val == 2
        assert result.next.next.val == 3
        assert result.next.next.next is None

    def test_linked_list_to_list_empty(self):
        assert linked_list_to_list(None) == []

    def test_linked_list_to_list_single(self):
        node = ListNode(5)
        assert linked_list_to_list(node) == [5]

    def test_linked_list_to_list_multiple(self):
        node = ListNode(1, ListNode(2, ListNode(3)))
        assert linked_list_to_list(node) == [1, 2, 3]

    def test_roundtrip(self):
        original = [1, 4, 5, 7, 9]
        linked = list_to_linked_list(original)
        result = linked_list_to_list(linked)
        assert result == original


class TestMergeKSortedLists:
    """Test cases for merge_k_lists function."""

    def test_example_1(self):
        """Test case from LeetCode example 1."""
        l1 = list_to_linked_list([1, 4, 5])
        l2 = list_to_linked_list([1, 3, 4])
        l3 = list_to_linked_list([2, 6])

        result = merge_k_lists([l1, l2, l3])
        assert linked_list_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_example_2_empty_lists(self):
        """Test case from LeetCode example 2 - empty input."""
        result = merge_k_lists([])
        assert result is None or linked_list_to_list(result) == []

    def test_example_3_empty_list_in_array(self):
        """Test case from LeetCode example 3 - list containing empty list."""
        result = merge_k_lists([None])
        assert result is None or linked_list_to_list(result) == []

    def test_single_list(self):
        """Test with a single non-empty list."""
        l1 = list_to_linked_list([1, 2, 3])
        result = merge_k_lists([l1])
        assert linked_list_to_list(result) == [1, 2, 3]

    def test_two_lists(self):
        """Test with exactly two lists."""
        l1 = list_to_linked_list([1, 3, 5])
        l2 = list_to_linked_list([2, 4, 6])

        result = merge_k_lists([l1, l2])
        assert linked_list_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_lists_with_duplicates(self):
        """Test lists that contain duplicate values."""
        l1 = list_to_linked_list([1, 1, 1])
        l2 = list_to_linked_list([1, 1, 1])
        l3 = list_to_linked_list([1, 1, 1])

        result = merge_k_lists([l1, l2, l3])
        assert linked_list_to_list(result) == [1, 1, 1, 1, 1, 1, 1, 1, 1]

    def test_negative_values(self):
        """Test lists with negative values."""
        l1 = list_to_linked_list([-3, -1, 2])
        l2 = list_to_linked_list([-2, 0, 4])

        result = merge_k_lists([l1, l2])
        assert linked_list_to_list(result) == [-3, -2, -1, 0, 2, 4]

    def test_already_sorted_single_list(self):
        """Test when all elements are already in order."""
        l1 = list_to_linked_list([1, 2, 3, 4, 5])
        l2 = list_to_linked_list([6, 7, 8, 9, 10])

        result = merge_k_lists([l1, l2])
        assert linked_list_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_reverse_order_inputs(self):
        """Test lists in reverse sorted order (will still work)."""
        # Note: our solution assumes inputs are sorted ascending
        l1 = list_to_linked_list([5, 4, 3, 2, 1])  # Not sorted!
        # This would not produce correct results - but that's not our concern
        # as problem guarantees sorted inputs

    def test_all_empty_lists(self):
        """Test with multiple empty lists."""
        result = merge_k_lists([None, None, None])
        assert result is None or linked_list_to_list(result) == []

    def test_large_gap_values(self):
        """Test with large gaps between values."""
        l1 = list_to_linked_list([1, 1000000])
        l2 = list_to_linked_list([2, 999999])

        result = merge_k_lists([l1, l2])
        assert linked_list_to_list(result) == [1, 2, 999999, 1000000]

    def test_mixed_empty_and_non_empty(self):
        """Test with a mix of empty and non-empty lists."""
        l1 = list_to_linked_list([1, 3, 5])
        l2 = None
        l3 = list_to_linked_list([2, 4, 6])
        l4 = None

        result = merge_k_lists([l1, l2, l3, l4])
        assert linked_list_to_list(result) == [1, 2, 3, 4, 5, 6]


class TestBothAlgorithms:
    """Test that both implementations produce the same results."""

    @pytest.mark.parametrize("lists_input,expected", [
        ([[1, 4, 5], [1, 3, 4], [2, 6]], [1, 1, 2, 3, 4, 4, 5, 6]),
        ([], []),
        ([[]], []),
        ([[1, 2, 3]], [1, 2, 3]),
        ([[1, 3, 5], [2, 4, 6]], [1, 2, 3, 4, 5, 6]),
        ([[-1, 0, 3, 4, 5]], [-1, 0, 3, 4, 5]),
    ])
    def test_both_algorithms_equivalent(self, lists_input, expected):
        """Verify heap and divide-conquer give same results."""
        # Convert input to linked lists - test each algorithm separately
        # since they consume the input lists
        linked_lists_heap = [list_to_linked_list(lst) if lst else None
                             for lst in lists_input]
        linked_lists_dc = [list_to_linked_list(lst) if lst else None
                           for lst in lists_input]

        result_heap = merge_k_lists_heap(linked_lists_heap)
        result_dc = merge_k_lists_divide_conquer(linked_lists_dc)

        assert linked_list_to_list(result_heap) == expected
        assert linked_list_to_list(result_dc) == expected


class TestComplexity:
    """Test cases that verify algorithmic properties."""

    def test_handles_large_k(self):
        """Test with many small lists."""
        # Create 100 lists, each with 1 element
        lists = [list_to_linked_list([i]) for i in range(100)]

        result = merge_k_lists(lists)
        expected = list(range(100))
        assert linked_list_to_list(result) == expected

    def test_handles_large_single_list(self):
        """Test with single large list."""
        large_list = list(range(1000))
        result = merge_k_lists([list_to_linked_list(large_list)])
        assert linked_list_to_list(result) == large_list
