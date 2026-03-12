"""
Tests for Merge k Sorted Lists (LeetCode #23)
"""

from __future__ import annotations

import pytest
from merge_k_sorted_lists import (
    ListNode,
    merge_k_lists,
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
    merge_two_lists,
    list_to_linkedlist,
    linkedlist_to_list,
)


class TestMergeTwoLists:
    """Tests for merging two sorted lists."""

    def test_merge_two_empty(self):
        assert merge_two_lists(None, None) is None

    def test_merge_two_one_empty(self):
        result = merge_two_lists(list_to_linkedlist([1, 2, 3]), None)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_merge_two_both_empty(self):
        result = merge_two_lists(None, list_to_linkedlist([1, 2, 3]))
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_merge_two_basic(self):
        l1 = list_to_linkedlist([1, 2, 4])
        l2 = list_to_linkedlist([1, 3, 4])
        result = merge_two_lists(l1, l2)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4]

    def test_merge_two_non_overlapping(self):
        l1 = list_to_linkedlist([1, 2, 3])
        l2 = list_to_linkedlist([4, 5, 6])
        result = merge_two_lists(l1, l2)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_merge_two_duplicates(self):
        l1 = list_to_linkedlist([1, 1, 1])
        l2 = list_to_linkedlist([1, 1, 1])
        result = merge_two_lists(l1, l2)
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1]


class TestMergeKListsHeap:
    """Tests for heap-based merge k lists solution."""

    def test_empty_list(self):
        result = merge_k_lists_heap([])
        assert result is None

    def test_single_empty_list(self):
        result = merge_k_lists_heap([None])
        assert result is None

    def test_single_list(self):
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_lists(self):
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 1, 3, 4, 4, 5]

    def test_three_lists(self):
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_lists_with_empty(self):
        lists = [
            list_to_linkedlist([1, 4, 5]),
            None,
            list_to_linkedlist([1, 3, 4]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 1, 3, 4, 4, 5]

    def test_all_empty_lists(self):
        lists = [None, None, None]
        result = merge_k_lists_heap(lists)
        assert result is None

    def test_single_element_each(self):
        lists = [
            list_to_linkedlist([1]),
            list_to_linkedlist([0]),
            list_to_linkedlist([2]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [0, 1, 2]

    def test_negative_numbers(self):
        lists = [
            list_to_linkedlist([-3, -1, 0]),
            list_to_linkedlist([-5, -2, 3]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [-5, -3, -2, -1, 0, 3]

    def test_large_values(self):
        lists = [
            list_to_linkedlist([10000]),
            list_to_linkedlist([-10000]),
            list_to_linkedlist([0]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [-10000, 0, 10000]

    def test_duplicates_across_lists(self):
        lists = [
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1]),
            list_to_linkedlist([1]),
        ]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1]


class TestMergeKListsDivideConquer:
    """Tests for divide-and-conquer merge k lists solution."""

    def test_empty_list(self):
        result = merge_k_lists_divide_conquer([])
        assert result is None

    def test_single_list(self):
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_lists(self):
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 1, 3, 4, 4, 5]

    def test_three_lists(self):
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_lists_with_empty(self):
        lists = [
            list_to_linkedlist([1, 4, 5]),
            None,
            list_to_linkedlist([1, 3, 4]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 1, 3, 4, 4, 5]


class TestMainMergeKLists:
    """Tests for main merge_k_lists function."""

    def test_example_1(self):
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_example_2(self):
        result = merge_k_lists([])
        assert result is None

    def test_example_3(self):
        result = merge_k_lists([[]])
        assert result is None


class TestEdgeCases:
    """Edge case tests."""

    def test_mixed_empty_and_non_empty(self):
        lists = [
            None,
            list_to_linkedlist([1]),
            None,
            list_to_linkedlist([0]),
            None,
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [0, 1]

    def test_large_k(self):
        # Create k lists with 1 element each
        lists = [list_to_linkedlist([i]) for i in range(100)]
        result = merge_k_lists(lists)
        expected = list(range(100))
        assert linkedlist_to_list(result) == expected

    def test_already_sorted_single_list(self):
        lists = [list_to_linkedlist([1, 2, 3, 4, 5])]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5]

    def test_reverse_order_input(self):
        lists = [
            list_to_linkedlist([6]),
            list_to_linkedlist([5]),
            list_to_linkedlist([4]),
            list_to_linkedlist([3]),
            list_to_linkedlist([2]),
            list_to_linkedlist([1]),
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
