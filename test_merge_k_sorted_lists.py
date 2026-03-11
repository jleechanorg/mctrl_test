"""
Tests for LeetCode 23 - Merge k Sorted Lists
"""

from __future__ import annotations

import pytest
from merge_k_sorted_lists import (
    merge_k_sorted_lists,
    merge_k_sorted_lists_divide_conquer,
    ListNode,
    list_to_linkedlist,
    linkedlist_to_list,
)


class TestMergeKSortedLists:
    """Test cases for merge_k_sorted_lists."""

    def test_example(self):
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_lists(self):
        result = merge_k_sorted_lists([])
        assert result is None

    def test_single_empty_list(self):
        result = merge_k_sorted_lists([None])
        assert result is None

    def test_single_list(self):
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_lists(self):
        lists = [list_to_linkedlist([1, 3, 5]), list_to_linkedlist([2, 4, 6])]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_with_duplicates(self):
        lists = [
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1, 2]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 2]

    def test_uneven_lists(self):
        lists = [
            list_to_linkedlist([1]),
            list_to_linkedlist([2, 3, 4, 5, 6]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_negative_numbers(self):
        lists = [
            list_to_linkedlist([-3, -2, -1]),
            list_to_linkedlist([0, 1, 2]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [-3, -2, -1, 0, 1, 2]


class TestMergeKSortedListsDivideConquer:
    """Test cases for divide and conquer approach."""

    def test_same_as_heap_method(self):
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6]),
        ]
        result = merge_k_sorted_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty(self):
        result = merge_k_sorted_lists_divide_conquer([])
        assert result is None

    def test_single_list(self):
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_sorted_lists_divide_conquer(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
