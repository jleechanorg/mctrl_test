"""
Comprehensive tests for Merge k Sorted Lists solution.
"""

from __future__ import annotations

import pytest

from merge_k_sorted_lists import (
    ListNode,
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
    merge_two_lists,
    list_to_linkedlist,
    linkedlist_to_list,
    Solution,
)


class TestListNode:
    """Test ListNode class."""

    def test_listnode_creation(self):
        node = ListNode(5)
        assert node.val == 5
        assert node.next is None

    def test_listnode_with_next(self):
        node1 = ListNode(1)
        node2 = ListNode(2)
        node1.next = node2
        assert node1.next.val == 2


class TestListConversion:
    """Test conversion functions."""

    def test_empty_list_to_linkedlist(self):
        assert list_to_linkedlist([]) is None

    def test_single_element(self):
        result = list_to_linkedlist([1])
        assert linkedlist_to_list(result) == [1]

    def test_multiple_elements(self):
        result = list_to_linkedlist([1, 2, 3, 4, 5])
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5]


class TestMergeTwoLists:
    """Test merge_two_lists helper function."""

    def test_merge_two_empty(self):
        assert merge_two_lists(None, None) is None

    def test_merge_one_empty(self):
        l1 = list_to_linkedlist([1, 2, 3])
        result = merge_two_lists(l1, None)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_merge_both_empty(self):
        result = merge_two_lists(None, list_to_linkedlist([1, 2]))
        assert linkedlist_to_list(result) == [1, 2]

    def test_merge_interleaved(self):
        l1 = list_to_linkedlist([1, 3, 5])
        l2 = list_to_linkedlist([2, 4, 6])
        result = merge_two_lists(l1, l2)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_merge_all_from_l1(self):
        l1 = list_to_linkedlist([1, 2, 3])
        l2 = list_to_linkedlist([4, 5, 6])
        result = merge_two_lists(l1, l2)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_merge_all_from_l2(self):
        l1 = list_to_linkedlist([4, 5, 6])
        l2 = list_to_linkedlist([1, 2, 3])
        result = merge_two_lists(l1, l2)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_merge_with_duplicates(self):
        l1 = list_to_linkedlist([1, 1, 3])
        l2 = list_to_linkedlist([1, 2, 3])
        result = merge_two_lists(l1, l2)
        assert linkedlist_to_list(result) == [1, 1, 1, 2, 3, 3]


class TestMergeKListsHeap:
    """Test heap-based merge_k_lists function."""

    def test_example_1(self):
        """Example from LeetCode: [[1,4,5],[1,3,4],[2,6]]"""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_example_2(self):
        """Empty input lists."""
        lists: list = []
        result = merge_k_lists_heap(lists)
        assert result is None

    def test_example_3(self):
        """List with empty list."""
        lists = [[]]
        result = merge_k_lists_heap(lists)
        assert result is None

    def test_single_list(self):
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_lists(self):
        lists = [
            list_to_linkedlist([1, 4, 6]),
            list_to_linkedlist([2, 3, 5]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_multiple_empty_lists(self):
        lists = [None, None, list_to_linkedlist([1])]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1]

    def test_all_empty_lists(self):
        lists = [None, None, None]
        result = merge_k_lists_heap(lists)
        assert result is None

    def test_single_element_each(self):
        lists = [
            list_to_linkedlist([1]),
            list_to_linkedlist([2]),
            list_to_linkedlist([3]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_already_sorted(self):
        lists = [
            list_to_linkedlist([1, 2, 3]),
            list_to_linkedlist([4, 5, 6]),
            list_to_linkedlist([7, 8, 9]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_reverse_sorted(self):
        """Input lists are sorted in ascending order - this tests merging already sorted lists."""
        lists = [
            list_to_linkedlist([1, 2, 3]),
            list_to_linkedlist([4, 5, 6]),
            list_to_linkedlist([7, 8, 9]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_with_duplicates(self):
        lists = [
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1, 2]),
            list_to_linkedlist([1, 2, 2]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1, 2, 2, 2]

    def test_negative_numbers(self):
        lists = [
            list_to_linkedlist([-3, -2, -1]),
            list_to_linkedlist([0, 1, 2]),
            list_to_linkedlist([-1, 0, 1]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [-3, -2, -1, -1, 0, 0, 1, 1, 2]

    def test_large_gap_values(self):
        lists = [
            list_to_linkedlist([-10000, 0]),
            list_to_linkedlist([10000]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [-10000, 0, 10000]

    def test_k_equals_1(self):
        """Edge case: k = 1"""
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]


class TestMergeKListsDivideConquer:
    """Test divide-and-conquer merge_k_lists function."""

    def test_example_1(self):
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty(self):
        lists: list = []
        result = merge_k_lists_divide_conquer(lists)
        assert result is None

    def test_single_list(self):
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_lists(self):
        lists = [
            list_to_linkedlist([1, 4, 6]),
            list_to_linkedlist([2, 3, 5]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_three_lists(self):
        lists = [
            list_to_linkedlist([1, 5, 9]),
            list_to_linkedlist([2, 6, 10]),
            list_to_linkedlist([3, 7, 11]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 5, 6, 7, 9, 10, 11]


class TestDefaultSolution:
    """Test the default exported Solution (heap approach)."""

    def test_default_is_heap(self):
        """Verify default Solution is the heap implementation."""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = Solution(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
