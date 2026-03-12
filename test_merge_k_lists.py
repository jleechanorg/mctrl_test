"""
Tests for Merge k Sorted Lists LeetCode Hard problem.
"""

from __future__ import annotations

import pytest
from merge_k_lists import (
    merge_k_lists,
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
    list_to_linkedlist,
    linkedlist_to_list,
    ListNode,
)


class TestMergeKLists:
    """Test cases for merge k sorted lists solution."""

    def test_example_1(self):
        """Test example 1 from LeetCode."""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = merge_k_lists(lists)
        expected = [1, 1, 2, 3, 4, 4, 5, 6]
        assert linkedlist_to_list(result) == expected

    def test_empty_list_of_lists(self):
        """Test with empty list of lists."""
        lists = []
        result = merge_k_lists(lists)
        assert result is None

    def test_single_empty_list(self):
        """Test with single empty linked list."""
        lists = [None]
        result = merge_k_lists(lists)
        assert result is None

    def test_single_list(self):
        """Test with single linked list."""
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_lists(self):
        """Test with two linked lists."""
        lists = [
            list_to_linkedlist([1, 3, 5]),
            list_to_linkedlist([2, 4, 6]),
        ]
        result = merge_k_lists(lists)
        expected = [1, 2, 3, 4, 5, 6]
        assert linkedlist_to_list(result) == expected

    def test_all_empty_lists(self):
        """Test with all empty linked lists."""
        lists = [None, None, None]
        result = merge_k_lists(lists)
        assert result is None

    def test_negative_numbers(self):
        """Test with negative numbers."""
        lists = [
            list_to_linkedlist([-3, -1, 0]),
            list_to_linkedlist([-5, -2]),
        ]
        result = merge_k_lists(lists)
        expected = [-5, -3, -2, -1, 0]
        assert linkedlist_to_list(result) == expected

    def test_duplicates_across_lists(self):
        """Test with duplicate values across different lists."""
        lists = [
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1]),
        ]
        result = merge_k_lists(lists)
        expected = [1, 1, 1, 1, 1]
        assert linkedlist_to_list(result) == expected

    # Intentionally failing tests - will be fixed after initial push
    def test_large_input(self):
        """Test with larger input - intentionally expects wrong result."""
        lists = [
            list_to_linkedlist([1, 2, 3, 4, 5]),
            list_to_linkedlist([6, 7, 8, 9, 10]),
            list_to_linkedlist([11, 12, 13, 14, 15]),
        ]
        result = merge_k_lists(lists)
        # Intentionally wrong expected value - will fail initially
        expected = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        assert linkedlist_to_list(result) == expected

    def test_unsorted_input_behavior(self):
        """Test behavior with unsorted input - intentionally expects wrong."""
        # The algorithm assumes sorted input - let's see what happens
        lists = [
            list_to_linkedlist([5, 3, 1]),  # Not sorted!
            list_to_linkedlist([6, 2]),
        ]
        result = merge_k_lists(lists)
        # Intentionally expects sorted output despite unsorted input
        expected = [1, 2, 3, 5, 6]
        assert linkedlist_to_list(result) == expected


class TestListNode:
    """Test ListNode class."""

    def test_listnode_creation(self):
        """Test ListNode creation."""
        node = ListNode(5)
        assert node.val == 5
        assert node.next is None

    def test_listnode_with_next(self):
        """Test ListNode with next node."""
        node1 = ListNode(1)
        node2 = ListNode(2)
        node1.next = node2
        assert node1.val == 1
        assert node1.next.val == 2


class TestHelperFunctions:
    """Test helper functions."""

    def test_list_to_linkedlist(self):
        """Test conversion from list to linked list."""
        head = list_to_linkedlist([1, 2, 3])
        assert linkedlist_to_list(head) == [1, 2, 3]

    def test_list_to_linkedlist_empty(self):
        """Test conversion from empty list."""
        head = list_to_linkedlist([])
        assert head is None

    def test_linkedlist_to_list(self):
        """Test conversion from linked list to list."""
        head = list_to_linkedlist([1, 2, 3])
        assert linkedlist_to_list(head) == [1, 2, 3]

    def test_linkedlist_to_list_empty(self):
        """Test conversion from empty linked list."""
        assert linkedlist_to_list(None) == []
