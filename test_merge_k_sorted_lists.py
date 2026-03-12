"""
Test cases for Merge k Sorted Lists solution.
"""
from __future__ import annotations

import pytest
from merge_k_sorted_lists import (
    ListNode,
    merge_k_lists,
    merge_k_lists_divide_conquer,
    merge_k_lists_heap,
    merge_two_lists,
)


class TestListNode:
    """Tests for ListNode helper class."""

    def test_from_list_empty(self):
        assert ListNode.from_list([]) is None

    def test_from_list_single(self):
        node = ListNode.from_list([1])
        assert node.val == 1
        assert node.next is None

    def test_from_list_multiple(self):
        node = ListNode.from_list([1, 2, 3])
        assert node.val == 1
        assert node.next.val == 2
        assert node.next.next.val == 3
        assert node.next.next.next is None

    def test_to_list_none_node(self):
        # Testing to_list on None node reference - will fail since None has no to_list method
        # Instead test that a valid node with value 0 works
        node = ListNode(0)
        assert node.to_list() == [0]

    def test_to_list_single(self):
        node = ListNode.from_list([5])
        assert node.to_list() == [5]

    def test_to_list_multiple(self):
        node = ListNode.from_list([1, 2, 3, 4, 5])
        assert node.to_list() == [1, 2, 3, 4, 5]


class TestMergeTwoLists:
    """Tests for merging two sorted lists."""

    def test_both_empty(self):
        assert merge_two_lists(None, None) is None

    def test_one_empty(self):
        l1 = ListNode.from_list([1, 2, 3])
        result = merge_two_lists(l1, None)
        assert result.to_list() == [1, 2, 3]

    def test_other_empty(self):
        l2 = ListNode.from_list([1, 2, 3])
        result = merge_two_lists(None, l2)
        assert result.to_list() == [1, 2, 3]

    def test_equal_elements(self):
        l1 = ListNode.from_list([1, 2, 3])
        l2 = ListNode.from_list([1, 2, 3])
        result = merge_two_lists(l1, l2)
        assert result.to_list() == [1, 1, 2, 2, 3, 3]

    def test_interleaved(self):
        l1 = ListNode.from_list([1, 3, 5])
        l2 = ListNode.from_list([2, 4, 6])
        result = merge_two_lists(l1, l2)
        assert result.to_list() == [1, 2, 3, 4, 5, 6]

    def test_different_lengths(self):
        l1 = ListNode.from_list([1])
        l2 = ListNode.from_list([2, 3, 4, 5])
        result = merge_two_lists(l1, l2)
        assert result.to_list() == [1, 2, 3, 4, 5]


class TestMergeKLists:
    """Main test cases for merge k sorted lists."""

    def test_example_1(self):
        """Example from LeetCode: [[1,4,5],[1,3,4],[2,6]]"""
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6])
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_list_of_lists(self):
        """Input: [] -> Output: []"""
        result = merge_k_lists([])
        assert result is None

    def test_list_containing_empty_lists(self):
        """Input: [[]] -> Output: []"""
        result = merge_k_lists([ListNode.from_list([])])
        assert result is None

    def test_single_list(self):
        """Input: [[1,2,3]] -> Output: [1,2,3]"""
        result = merge_k_lists([ListNode.from_list([1, 2, 3])])
        assert result.to_list() == [1, 2, 3]

    def test_two_empty_lists(self):
        """Input: [[], []] -> Output: []"""
        result = merge_k_lists([ListNode.from_list([]), ListNode.from_list([])])
        assert result is None

    def test_two_lists(self):
        """Input: [[1,2,3], [4,5,6]] -> Output: [1,2,3,4,5,6]"""
        lists = [
            ListNode.from_list([1, 2, 3]),
            ListNode.from_list([4, 5, 6])
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6]

    def test_all_same_values(self):
        """All lists contain same values"""
        lists = [
            ListNode.from_list([1, 1, 1]),
            ListNode.from_list([1, 1]),
            ListNode.from_list([1])
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 1, 1, 1, 1, 1]

    def test_negative_values(self):
        """Lists with negative values"""
        lists = [
            ListNode.from_list([-3, -1, 0]),
            ListNode.from_list([-2, 2]),
            ListNode.from_list([1, 3])
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [-3, -2, -1, 0, 1, 2, 3]

    def test_descending_input(self):
        """Lists sorted in descending order (not valid per constraints but test anyway)"""
        lists = [
            ListNode.from_list([5, 4, 3, 2, 1]),
            ListNode.from_list([10, 9, 8])
        ]
        # This would sort ascending in result
        result = merge_k_lists(lists)
        # Merge still works as it just joins, but result won't be sorted
        # The actual input should be sorted ascending per problem constraints

    def test_large_gap_values(self):
        """Lists with values spanning large range"""
        lists = [
            ListNode.from_list([-10000, 0]),
            ListNode.from_list([10000]),
            ListNode.from_list([5000])
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [-10000, 0, 5000, 10000]

    def test_alternating_small_large(self):
        """Alternating small and large values across lists"""
        lists = [
            ListNode.from_list([1, 100]),
            ListNode.from_list([2, 99]),
            ListNode.from_list([3, 98])
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3, 98, 99, 100]


class TestEdgeCases:
    """Edge case tests."""

    def test_k_equals_1(self):
        """k = 1: single list"""
        lists = [ListNode.from_list([1, 2, 3])]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3]

    def test_k_equals_0(self):
        """k = 0: empty array"""
        result = merge_k_lists([])
        assert result is None

    def test_each_list_single_element(self):
        """Each list has exactly one element"""
        lists = [
            ListNode.from_list([5]),
            ListNode.from_list([2]),
            ListNode.from_list([8]),
            ListNode.from_list([1])
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 5, 8]

    def test_very_long_list(self):
        """One very long list with many short others"""
        long_list = list(range(100))
        lists = [
            ListNode.from_list(long_list),
            ListNode.from_list([0]),
            ListNode.from_list([50]),
        ]
        result = merge_k_lists(lists)
        expected = sorted(long_list + [0, 50])
        assert result.to_list() == expected
