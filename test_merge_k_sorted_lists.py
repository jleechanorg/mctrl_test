"""
Test cases for Merge k Sorted Lists solution.
"""

from __future__ import annotations

import pytest

from merge_k_sorted_lists import (
    ListNode,
    merge_k_sorted_lists,
    merge_k_sorted_lists_optimized,
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
        assert node.to_list() == [1, 2, 3]

    def test_to_list_single(self):
        node = ListNode(5)
        assert node.to_list() == [5]

    def test_to_list_multiple(self):
        node = ListNode(1, ListNode(2, ListNode(3)))
        assert node.to_list() == [1, 2, 3]


class TestMergeKSortedLists:
    """Tests for merge_k_sorted_lists function."""

    def test_example_case(self):
        """Example from LeetCode: [[1,4,5],[1,3,4],[2,6]] -> [1,1,2,3,4,4,5,6]"""
        list1 = ListNode.from_list([1, 4, 5])
        list2 = ListNode.from_list([1, 3, 4])
        list3 = ListNode.from_list([2, 6])

        result = merge_k_sorted_lists([list1, list2, list3])
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_single_empty_list(self):
        """Single empty list returns None."""
        result = merge_k_sorted_lists([None])
        assert result is None

    def test_all_empty_lists(self):
        """All empty lists returns None."""
        result = merge_k_sorted_lists([None, None, None])
        assert result is None

    def test_single_list(self):
        """Single non-empty list returns that list."""
        node = ListNode.from_list([1, 2, 3])
        result = merge_k_sorted_lists([node])
        assert result.to_list() == [1, 2, 3]

    def test_two_lists(self):
        """Two sorted lists merged correctly."""
        list1 = ListNode.from_list([1, 3, 5])
        list2 = ListNode.from_list([2, 4, 6])

        result = merge_k_sorted_lists([list1, list2])
        assert result.to_list() == [1, 2, 3, 4, 5, 6]

    def test_two_lists_one_empty(self):
        """One empty list, one non-empty."""
        list1 = ListNode.from_list([1, 2, 3])
        list2 = None

        result = merge_k_sorted_lists([list1, list2])
        assert result.to_list() == [1, 2, 3]

    def test_lists_with_duplicates(self):
        """Lists with duplicate values."""
        list1 = ListNode.from_list([1, 1, 1])
        list2 = ListNode.from_list([1, 1, 1])
        list3 = ListNode.from_list([1, 1, 1])

        result = merge_k_sorted_lists([list1, list2, list3])
        assert result.to_list() == [1, 1, 1, 1, 1, 1, 1, 1, 1]

    def test_lists_different_lengths(self):
        """Lists of varying lengths."""
        list1 = ListNode.from_list([1])
        list2 = ListNode.from_list([2, 3])
        list3 = ListNode.from_list([4, 5, 6, 7])

        result = merge_k_sorted_lists([list1, list2, list3])
        assert result.to_list() == [1, 2, 3, 4, 5, 6, 7]

    def test_negative_numbers(self):
        """Lists with negative numbers."""
        list1 = ListNode.from_list([-3, -1, 0])
        list2 = ListNode.from_list([-2, 2])
        list3 = ListNode.from_list([1, 4])

        result = merge_k_sorted_lists([list1, list2, list3])
        assert result.to_list() == [-3, -2, -1, 0, 1, 2, 4]

    def test_single_element_each(self):
        """Single element in each of k lists."""
        lists = [ListNode(i) for i in range(5, 0, -1)]  # [5,4,3,2,1]

        result = merge_k_sorted_lists(lists)
        assert result.to_list() == [1, 2, 3, 4, 5]

    def test_large_k_small_lists(self):
        """Many lists with few elements each."""
        lists = [ListNode(i) for i in range(100)]

        result = merge_k_sorted_lists(lists)
        assert result.to_list() == list(range(100))

    def test_mixed_empty_and_non_empty(self):
        """Mix of empty and non-empty lists."""
        lists = [
            ListNode.from_list([1, 5]),
            None,
            ListNode.from_list([2, 3, 4]),
            None,
            None,
        ]

        result = merge_k_sorted_lists(lists)
        assert result.to_list() == [1, 2, 3, 4, 5]


class TestMergeKSortedListsOptimized:
    """Tests for the optimized version."""

    def test_example_case(self):
        """Example from LeetCode."""
        list1 = ListNode.from_list([1, 4, 5])
        list2 = ListNode.from_list([1, 3, 4])
        list3 = ListNode.from_list([2, 6])

        result = merge_k_sorted_lists_optimized([list1, list2, list3])
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_input(self):
        """Empty input returns None."""
        result = merge_k_sorted_lists_optimized([])
        assert result is None

    def test_single_list(self):
        """Single list returns that list."""
        node = ListNode.from_list([1, 2, 3])
        result = merge_k_sorted_lists_optimized([node])
        assert result.to_list() == [1, 2, 3]

    def test_two_lists(self):
        """Two lists merged correctly."""
        list1 = ListNode.from_list([1, 3, 5])
        list2 = ListNode.from_list([2, 4, 6])

        result = merge_k_sorted_lists_optimized([list1, list2])
        assert result.to_list() == [1, 2, 3, 4, 5, 6]


# Parameterized tests comparing both implementations
class TestBothImplementations:
    """Verify both implementations produce same results."""

    @pytest.mark.parametrize("func", [merge_k_sorted_lists, merge_k_sorted_lists_optimized])
    def test_compare_empty(self, func):
        assert func([None, None]) is None

    @pytest.mark.parametrize("func", [merge_k_sorted_lists, merge_k_sorted_lists_optimized])
    def test_compare_basic(self, func):
        list1 = ListNode.from_list([1, 3, 5])
        list2 = ListNode.from_list([2, 4, 6])
        result = func([list1, list2])
        assert result.to_list() == [1, 2, 3, 4, 5, 6]

    @pytest.mark.parametrize("func", [merge_k_sorted_lists, merge_k_sorted_lists_optimized])
    def test_compare_three_lists(self, func):
        lists = [ListNode.from_list([i]) for i in range(5)]
        result = func(lists)
        assert result.to_list() == [0, 1, 2, 3, 4]
