"""
Tests for Merge k Sorted Lists solution.
"""

from merge_k_sorted_lists import (
    merge_k_sorted_lists,
    list_to_linkedlist,
    linkedlist_to_list,
    ListNode,
)


class TestMergeKSortedLists:
    """Test cases for merge_k_sorted_lists function."""

    def test_basic_example(self):
        """Test with the classic example from LeetCode."""
        list1 = list_to_linkedlist([1, 4, 5])
        list2 = list_to_linkedlist([1, 3, 4])
        list3 = list_to_linkedlist([2, 6])

        result = merge_k_sorted_lists([list1, list2, list3])
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_input(self):
        """Test with empty input list."""
        result = merge_k_sorted_lists([])
        assert result is None

    def test_single_empty_list(self):
        """Test with a single None list."""
        result = merge_k_sorted_lists([None])
        assert result is None

    def test_single_list(self):
        """Test with a single non-empty list."""
        list1 = list_to_linkedlist([1, 2, 3])
        result = merge_k_sorted_lists([list1])
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_lists(self):
        """Test merging two lists."""
        list1 = list_to_linkedlist([1, 3, 5])
        list2 = list_to_linkedlist([2, 4, 6])

        result = merge_k_sorted_lists([list1, list2])
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_lists_with_duplicates(self):
        """Test merging lists that have duplicate values."""
        list1 = list_to_linkedlist([1, 1, 1])
        list2 = list_to_linkedlist([1, 1, 1])

        result = merge_k_sorted_lists([list1, list2])
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1]

    def test_some_empty_lists(self):
        """Test when some lists are empty (None)."""
        list1 = list_to_linkedlist([1, 3, 5])
        list2 = None
        list3 = list_to_linkedlist([2, 4, 6])

        result = merge_k_sorted_lists([list1, list2, list3])
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_single_element_lists(self):
        """Test with single-element lists."""
        list1 = list_to_linkedlist([1])
        list2 = list_to_linkedlist([0])
        list3 = list_to_linkedlist([2])

        result = merge_k_sorted_lists([list1, list2, list3])
        assert linkedlist_to_list(result) == [0, 1, 2]

    def test_already_sorted_single_list(self):
        """Test with multiple lists that are already sorted individually."""
        result = merge_k_sorted_lists([
            list_to_linkedlist([1, 2, 3]),
            list_to_linkedlist([4, 5, 6]),
            list_to_linkedlist([7, 8, 9]),
        ])
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_reverse_order_input(self):
        """Test with lists in reverse order."""
        result = merge_k_sorted_lists([
            list_to_linkedlist([6, 7, 8]),
            list_to_linkedlist([3, 4, 5]),
            list_to_linkedlist([1, 2, 3]),
        ])
        assert linkedlist_to_list(result) == [1, 2, 3, 3, 4, 5, 6, 7, 8]

    def test_negative_values(self):
        """Test with negative values."""
        list1 = list_to_linkedlist([-3, -1, 0])
        list2 = list_to_linkedlist([-2, 2, 3])

        result = merge_k_sorted_lists([list1, list2])
        assert linkedlist_to_list(result) == [-3, -2, -1, 0, 2, 3]

    def test_mixed_length_lists(self):
        """Test with lists of varying lengths."""
        result = merge_k_sorted_lists([
            list_to_linkedlist([1]),
            list_to_linkedlist([2, 3, 4, 5]),
            list_to_linkedlist([6, 7]),
        ])
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6, 7]


class TestListConversion:
    """Test helper functions for list/linked list conversion."""

    def test_list_to_linkedlist_empty(self):
        """Test converting empty list."""
        assert list_to_linkedlist([]) is None

    def test_list_to_linkedlist_single(self):
        """Test converting single element list."""
        result = list_to_linkedlist([42])
        assert result.val == 42
        assert result.next is None

    def test_linkedlist_to_list_empty(self):
        """Test converting empty linked list."""
        assert linkedlist_to_list(None) == []

    def test_linkedlist_to_list_roundtrip(self):
        """Test that conversion is reversible."""
        original = [1, 2, 3, 4, 5]
        linked = list_to_linkedlist(original)
        result = linkedlist_to_list(linked)
        assert result == original
