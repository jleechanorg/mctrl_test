"""Tests for Merge k Sorted Lists solution."""

from __future__ import annotations

import pytest

from merge_k_lists import (
    ListNode,
    linkedlist_to_list,
    list_to_linkedlist,
    merge_k_lists,
)


class TestMergeKSortedLists:
    """Test cases for merge_k_lists function."""

    def test_multiple_sorted_lists(self):
        """Test merging multiple sorted lists."""
        l1 = list_to_linkedlist([1, 4, 5])
        l2 = list_to_linkedlist([1, 3, 4])
        l3 = list_to_linkedlist([2, 6])

        result = merge_k_lists([l1, l2, l3])
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_single_list(self):
        """Test with a single list."""
        l1 = list_to_linkedlist([1, 2, 3])
        result = merge_k_lists([l1])
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_lists(self):
        """Test with two lists."""
        l1 = list_to_linkedlist([1, 3, 5])
        l2 = list_to_linkedlist([2, 4, 6])

        result = merge_k_lists([l1, l2])
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_empty_lists(self):
        """Test with empty list of lists."""
        result = merge_k_lists([])
        assert result is None

    def test_lists_with_none(self):
        """Test when some lists are None."""
        l1 = list_to_linkedlist([1, 2, 3])
        l2 = None
        l3 = list_to_linkedlist([4, 5, 6])

        result = merge_k_lists([l1, l2, l3])
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_all_none_lists(self):
        """Test when all lists are None."""
        result = merge_k_lists([None, None, None])
        assert result is None

    def test_single_element_lists(self):
        """Test with lists containing single elements."""
        l1 = list_to_linkedlist([1])
        l2 = list_to_linkedlist([0])
        l3 = list_to_linkedlist([2])

        result = merge_k_lists([l1, l2, l3])
        assert linkedlist_to_list(result) == [0, 1, 2]

    def test_duplicate_values(self):
        """Test with duplicate values across lists."""
        l1 = list_to_linkedlist([1, 1, 1])
        l2 = list_to_linkedlist([1, 1, 1])
        l3 = list_to_linkedlist([1, 1, 1])

        result = merge_k_lists([l1, l2, l3])
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1, 1, 1, 1]

    def test_already_sorted_single_list(self):
        """Test when all elements form a single sorted list."""
        l1 = list_to_linkedlist([1, 2, 3, 4, 5])
        l2 = list_to_linkedlist([])
        l3 = None

        result = merge_k_lists([l1, l2, l3])
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5]

    def test_descending_sorted_input(self):
        """Test with descending sorted input lists (not valid input - test error case).

        Note: The problem assumes input lists are sorted in ascending order.
        This test documents what happens with unsorted input.
        """
        l1 = list_to_linkedlist([5, 4, 3, 2, 1])
        l2 = list_to_linkedlist([10, 9, 8, 7, 6])

        result = merge_k_lists([l1, l2])
        # With unsorted input, output preserves internal order within each list
        assert linkedlist_to_list(result) == [5, 4, 3, 2, 1, 10, 9, 8, 7, 6]

    def test_large_k_small_lists(self):
        """Test with many small lists (k=1000, 1 element each)."""
        lists = [list_to_linkedlist([i]) for i in range(1000)]
        result = merge_k_lists(lists)
        expected = list(range(1000))
        assert linkedlist_to_list(result) == expected

    def test_negative_values(self):
        """Test with negative numbers."""
        l1 = list_to_linkedlist([-5, -3, -1])
        l2 = list_to_linkedlist([-4, -2, 0])
        l3 = list_to_linkedlist([2, 4, 6])

        result = merge_k_lists([l1, l2, l3])
        assert linkedlist_to_list(result) == [-5, -4, -3, -2, -1, 0, 2, 4, 6]

    def test_mixed_lengths(self):
        """Test with lists of varying lengths."""
        l1 = list_to_linkedlist([1])
        l2 = list_to_linkedlist([2, 3])
        l3 = list_to_linkedlist([4, 5, 6])
        l4 = list_to_linkedlist([7, 8, 9, 10])

        result = merge_k_lists([l1, l2, l3, l4])
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


class TestListNode:
    """Test cases for ListNode class."""

    def test_listnode_creation(self):
        """Test basic ListNode creation."""
        node = ListNode(5)
        assert node.val == 5
        assert node.next is None

    def test_listnode_with_next(self):
        """Test ListNode with next pointer."""
        node1 = ListNode(1)
        node2 = ListNode(2, node1)
        assert node2.val == 2
        assert node2.next == node1


class TestHelperFunctions:
    """Test helper functions."""

    def test_list_to_linkedlist(self):
        """Test converting list to linked list."""
        head = list_to_linkedlist([1, 2, 3, 4, 5])
        assert linkedlist_to_list(head) == [1, 2, 3, 4, 5]

    def test_list_to_linkedlist_empty(self):
        """Test converting empty list."""
        head = list_to_linkedlist([])
        assert head is None

    def test_linkedlist_to_list(self):
        """Test converting linked list to list."""
        head = ListNode(1, ListNode(2, ListNode(3)))
        assert linkedlist_to_list(head) == [1, 2, 3]

    def test_linkedlist_to_list_empty(self):
        """Test converting None to list."""
        assert linkedlist_to_list(None) == []
