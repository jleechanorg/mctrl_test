"""
Tests for LeetCode 23 - Merge k Sorted Lists

Comprehensive test suite covering:
- Basic merge operations
- Edge cases (empty lists, single list, all empty)
- Duplicate values
- Negative numbers
- Large inputs
- Both heap and divide-and-conquer approaches
"""
from __future__ import annotations

import pytest
from merge_k_sorted_lists import (
    Solution,
    ListNode,
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
    merge_two_lists,
    list_to_linkedlist,
    linkedlist_to_list,
)


class TestMergeTwoLists:
    """Tests for merging two sorted lists."""

    def test_merge_two_basic(self):
        l1 = list_to_linkedlist([1, 2, 4])
        l2 = list_to_linkedlist([1, 3, 4])
        result = merge_two_lists(l1, l2)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4]

    def test_merge_two_empty(self):
        l1 = list_to_linkedlist([])
        l2 = list_to_linkedlist([])
        result = merge_two_lists(l1, l2)
        assert linkedlist_to_list(result) == []

    def test_merge_two_one_empty(self):
        l1 = list_to_linkedlist([1, 2, 3])
        l2 = list_to_linkedlist([])
        result = merge_two_lists(l1, l2)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_merge_two_duplicates(self):
        l1 = list_to_linkedlist([1, 1, 1])
        l2 = list_to_linkedlist([1, 1, 1])
        result = merge_two_lists(l1, l2)
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1]

    def test_merge_two_negative(self):
        l1 = list_to_linkedlist([-3, -1, 0])
        l2 = list_to_linkedlist([-2, 2, 4])
        result = merge_two_lists(l1, l2)
        assert linkedlist_to_list(result) == [-3, -2, -1, 0, 2, 4]


class TestMergeKListsHeap:
    """Tests for heap-based k-way merge."""

    def test_example_1(self):
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_example_2(self):
        lists = []
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == []

    def test_example_3(self):
        lists = [list_to_linkedlist([])]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == []

    def test_single_list(self):
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_lists(self):
        lists = [
            list_to_linkedlist([1, 3, 5]),
            list_to_linkedlist([2, 4, 6]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_with_duplicates(self):
        lists = [
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1]),
            list_to_linkedlist([1]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1]

    def test_negative_numbers(self):
        lists = [
            list_to_linkedlist([-5, -3, 0]),
            list_to_linkedlist([-2, 2, 4]),
            list_to_linkedlist([-10, -1]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [-10, -5, -3, -2, -1, 0, 2, 4]

    def test_mixed_positive_negative(self):
        lists = [
            list_to_linkedlist([-100, 0, 100]),
            list_to_linkedlist([-50, 50]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [-100, -50, 0, 50, 100]

    def test_all_empty_except_one(self):
        lists = [
            list_to_linkedlist([]),
            list_to_linkedlist([]),
            list_to_linkedlist([1]),
            list_to_linkedlist([]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1]


class TestMergeKListsDivideConquer:
    """Tests for divide-and-conquer k-way merge."""

    def test_example_1(self):
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty(self):
        lists = []
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == []

    def test_single_list(self):
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]


class TestSolution:
    """Tests for the LeetCode Solution class interface."""

    def test_solution_interface(self):
        """Test that Solution class works as LeetCode expects."""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        solution = Solution()
        result = solution.mergeKLists(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_solution_empty(self):
        """Test Solution with empty input."""
        lists = []
        solution = Solution()
        result = solution.mergeKLists(lists)
        assert linkedlist_to_list(result) == []


class TestHelperFunctions:
    """Tests for helper conversion functions."""

    def test_list_to_linkedlist_empty(self):
        assert list_to_linkedlist([]) is None

    def test_linkedlist_to_list_empty(self):
        assert linkedlist_to_list(None) == []

    def test_roundtrip(self):
        original = [1, 2, 3, 4, 5]
        linked = list_to_linkedlist(original)
        result = linkedlist_to_list(linked)
        assert result == original


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
