"""
Test suite for Merge k Sorted Lists solution.

Comprehensive tests covering:
- Basic cases
- Edge cases (empty lists, single list, single element)
- Duplicate values
- Already sorted lists
- Reverse sorted inputs
- Large inputs
"""

from __future__ import annotations

import pytest

from merge_k_sorted_lists import (
    merge_k_lists,
    merge_k_lists_divide_and_conquer,
    merge_k_lists_heap,
    merge_two_lists,
    ListNode,
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

    def test_to_list(self):
        node = ListNode.from_list([1, 2, 3])
        assert node.to_list() == [1, 2, 3]

    def test_to_list_empty(self):
        node = ListNode.from_list([])
        assert node is None or node.to_list() == []


class TestMergeTwoLists:
    """Tests for merge_two_lists helper function."""

    def test_merge_both_empty(self):
        result = merge_two_lists(None, None)
        assert result is None

    def test_merge_one_empty(self):
        l1 = ListNode.from_list([1, 2, 3])
        result = merge_two_lists(l1, None)
        assert result.to_list() == [1, 2, 3]

    def test_merge_second_empty(self):
        l2 = ListNode.from_list([1, 2, 3])
        result = merge_two_lists(None, l2)
        assert result.to_list() == [1, 2, 3]

    def test_merge_simple(self):
        l1 = ListNode.from_list([1, 2, 4])
        l2 = ListNode.from_list([1, 3, 4])
        result = merge_two_lists(l1, l2)
        assert result.to_list() == [1, 1, 2, 3, 4, 4]

    def test_merge_non_overlapping(self):
        l1 = ListNode.from_list([1, 2, 3])
        l2 = ListNode.from_list([4, 5, 6])
        result = merge_two_lists(l1, l2)
        assert result.to_list() == [1, 2, 3, 4, 5, 6]

    def test_merge_duplicates(self):
        l1 = ListNode.from_list([1, 1, 1])
        l2 = ListNode.from_list([1, 1, 1])
        result = merge_two_lists(l1, l2)
        assert result.to_list() == [1, 1, 1, 1, 1, 1]


class TestMergeKListsDivideAndConquer:
    """Tests for divide and conquer solution."""

    def test_example_case(self):
        """Example from LeetCode: [[1,4,5],[1,3,4],[2,6]] -> [1,1,2,3,4,4,5,6]"""
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6])
        ]
        result = merge_k_lists_divide_and_conquer(lists)
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_list_of_lists(self):
        result = merge_k_lists_divide_and_conquer([])
        assert result is None

    def test_list_with_none(self):
        lists = [None, None]
        result = merge_k_lists_divide_and_conquer(lists)
        assert result is None

    def test_single_list(self):
        lists = [ListNode.from_list([1, 2, 3])]
        result = merge_k_lists_divide_and_conquer(lists)
        assert result.to_list() == [1, 2, 3]

    def test_two_lists(self):
        lists = [
            ListNode.from_list([1, 3, 5]),
            ListNode.from_list([2, 4, 6])
        ]
        result = merge_k_lists_divide_and_conquer(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6]

    def test_already_sorted(self):
        lists = [
            ListNode.from_list([1]),
            ListNode.from_list([2]),
            ListNode.from_list([3])
        ]
        result = merge_k_lists_divide_and_conquer(lists)
        assert result.to_list() == [1, 2, 3]

    def test_duplicates(self):
        lists = [
            ListNode.from_list([1, 1, 1]),
            ListNode.from_list([1, 1, 1]),
            ListNode.from_list([1, 1, 1])
        ]
        result = merge_k_lists_divide_and_conquer(lists)
        assert result.to_list() == [1, 1, 1, 1, 1, 1, 1, 1, 1]

    def test_negative_values(self):
        lists = [
            ListNode.from_list([-3, -1, 0]),
            ListNode.from_list([-2, 2]),
            ListNode.from_list([1, 5])
        ]
        result = merge_k_lists_divide_and_conquer(lists)
        assert result.to_list() == [-3, -2, -1, 0, 1, 2, 5]

    def test_mixed_empty_and_non_empty(self):
        lists = [
            ListNode.from_list([1, 2]),
            None,
            ListNode.from_list([3, 4])
        ]
        result = merge_k_lists_divide_and_conquer(lists)
        assert result.to_list() == [1, 2, 3, 4]


class TestMergeKListsHeap:
    """Tests for heap-based solution."""

    def test_example_case(self):
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6])
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_list_of_lists(self):
        result = merge_k_lists_heap([])
        assert result is None

    def test_single_list(self):
        lists = [ListNode.from_list([1, 2, 3])]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 2, 3]

    def test_two_lists(self):
        lists = [
            ListNode.from_list([1, 3, 5]),
            ListNode.from_list([2, 4, 6])
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6]

    def test_duplicates(self):
        lists = [
            ListNode.from_list([1, 1, 1]),
            ListNode.from_list([1, 1, 1])
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 1, 1, 1, 1, 1]


class TestMergeKLists:
    """Tests for the main merge_k_lists function (default implementation)."""

    def test_example_case(self):
        """LeetCode example case."""
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6])
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_input(self):
        result = merge_k_lists([])
        assert result is None

    def test_all_empty_lists(self):
        result = merge_k_lists([None, None, None])
        assert result is None

    def test_single_list(self):
        result = merge_k_lists([ListNode.from_list([1, 2, 3])])
        assert result.to_list() == [1, 2, 3]

    def test_single_element_lists(self):
        lists = [
            ListNode.from_list([1]),
            ListNode.from_list([0]),
            ListNode.from_list([2])
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [0, 1, 2]

    def test_large_values(self):
        lists = [
            ListNode.from_list([1000000, 1000001]),
            ListNode.from_list([999999]),
            ListNode.from_list([-1000000, 0])
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [-1000000, 0, 999999, 1000000, 1000001]

    def test_all_same_values(self):
        lists = [
            ListNode.from_list([5, 5]),
            ListNode.from_list([5, 5]),
            ListNode.from_list([5, 5])
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [5, 5, 5, 5, 5, 5]

    def test_already_sorted_input(self):
        """Already sorted across all lists."""
        lists = [
            ListNode.from_list([1, 10, 20]),
            ListNode.from_list([2, 11, 21]),
            ListNode.from_list([3, 12, 22])
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3, 10, 11, 12, 20, 21, 22]

    def test_reverse_sorted_input(self):
        """Reverse sorted within each list - should still work (input is sorted asc)."""
        lists = [
            ListNode.from_list([1, 3, 5]),
            ListNode.from_list([2, 4, 6]),
            ListNode.from_list([3, 5, 7])
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3, 3, 4, 5, 5, 6, 7]

    def test_with_none_in_middle(self):
        lists = [
            ListNode.from_list([1, 4]),
            None,
            ListNode.from_list([2, 3])
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3, 4]

    def test_ten_lists(self):
        """Test with more lists."""
        lists = [ListNode.from_list([i]) for i in range(10)]
        result = merge_k_lists(lists)
        assert result.to_list() == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
