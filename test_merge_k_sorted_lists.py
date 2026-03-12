"""
Tests for Merge k Sorted Lists solution.
"""

from __future__ import annotations

import pytest
from merge_k_sorted_lists import (
    ListNode,
    merge_k_lists,
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
    merge_two_lists,
)


class TestListNode:
    """Tests for ListNode utility class."""

    def test_from_list_empty(self):
        assert ListNode.from_list([]) is None

    def test_from_list_single(self):
        result = ListNode.from_list([1])
        assert result.val == 1
        assert result.next is None

    def test_from_list_multiple(self):
        result = ListNode.from_list([1, 2, 3])
        assert result.to_list() == [1, 2, 3]

    def test_to_list(self):
        head = ListNode.from_list([1, 4, 5])
        assert head.to_list() == [1, 4, 5]


class TestMergeTwoLists:
    """Tests for merging two sorted lists."""

    def test_merge_both_empty(self):
        assert merge_two_lists(None, None) is None

    def test_merge_one_empty(self):
        l1 = ListNode.from_list([1, 2, 3])
        result = merge_two_lists(l1, None)
        assert result.to_list() == [1, 2, 3]

    def test_merge_interleaved(self):
        l1 = ListNode.from_list([1, 3, 5])
        l2 = ListNode.from_list([2, 4, 6])
        result = merge_two_lists(l1, l2)
        assert result.to_list() == [1, 2, 3, 4, 5, 6]

    def test_merge_unequal_length(self):
        l1 = ListNode.from_list([1, 3])
        l2 = ListNode.from_list([2, 4, 6, 8])
        result = merge_two_lists(l1, l2)
        assert result.to_list() == [1, 2, 3, 4, 6, 8]


class TestMergeKLists:
    """Comprehensive tests for merge k sorted lists."""

    def test_example_1(self):
        """Example from LeetCode: [[1,4,5],[1,3,4],[2,6]] -> [1,1,2,3,4,4,5,6]"""
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_example_2_empty_input(self):
        """Example: [] -> []"""
        lists = []
        result = merge_k_lists(lists)
        assert result is None

    def test_example_3_empty_lists(self):
        """Example: [[]] -> []"""
        lists = [None]
        result = merge_k_lists(lists)
        assert result is None

    def test_single_list(self):
        """Test with single non-empty list."""
        lists = [ListNode.from_list([1, 2, 3])]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3]

    def test_multiple_empty_lists(self):
        """Test with multiple empty lists."""
        lists = [None, None, None]
        result = merge_k_lists(lists)
        assert result is None

    def test_single_element_each(self):
        """Test with single element in each list."""
        lists = [
            ListNode.from_list([1]),
            ListNode.from_list([0]),
            ListNode.from_list([2]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [0, 1, 2]

    def test_already_sorted_single_list(self):
        """Test with lists that are already merged."""
        lists = [
            ListNode.from_list([1, 2, 3]),
            ListNode.from_list([4, 5, 6]),
            ListNode.from_list([7, 8, 9]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_reverse_sorted_input(self):
        """Test with lists in reverse order."""
        lists = [
            ListNode.from_list([7, 8, 9]),
            ListNode.from_list([4, 5, 6]),
            ListNode.from_list([1, 2, 3]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_with_negative_numbers(self):
        """Test with negative numbers."""
        lists = [
            ListNode.from_list([-3, -1, 0]),
            ListNode.from_list([-5, -2]),
            ListNode.from_list([-4, 2, 5]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [-5, -4, -3, -2, -1, 0, 2, 5]

    def test_with_duplicates(self):
        """Test with duplicate values across lists."""
        lists = [
            ListNode.from_list([1, 1, 1]),
            ListNode.from_list([1, 1]),
            ListNode.from_list([1]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 1, 1, 1, 1, 1]

    def test_many_small_lists(self):
        """Test with multiple small lists."""
        lists = [
            ListNode.from_list([1]),
            ListNode.from_list([0]),
            ListNode.from_list([2]),
            ListNode.from_list([5]),
            ListNode.from_list([3]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [0, 1, 2, 3, 5]

    def test_mixed_empty_and_non_empty(self):
        """Test with mix of empty and non-empty lists."""
        lists = [
            None,
            ListNode.from_list([1, 3]),
            None,
            ListNode.from_list([2, 4]),
            None,
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3, 4]


class TestDivideConquer:
    """Tests for divide and conquer approach."""

    def test_same_as_heap(self):
        """Verify divide conquer produces same results as heap approach."""
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6]),
        ]
        dc_result = merge_k_lists_divide_conquer(lists)
        assert dc_result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
