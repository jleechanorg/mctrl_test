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
    list_to_linkedlist,
    linkedlist_to_list,
)


class TestListToLinkedList:
    """Tests for list_to_linkedlist helper."""

    def test_empty_list(self):
        assert list_to_linkedlist([]) is None

    def test_single_element(self):
        node = list_to_linkedlist([1])
        assert node.val == 1
        assert node.next is None

    def test_multiple_elements(self):
        node = list_to_linkedlist([1, 2, 3])
        assert node.val == 1
        assert node.next.val == 2
        assert node.next.next.val == 3
        assert node.next.next.next is None


class TestLinkedListToList:
    """Tests for linkedlist_to_list helper."""

    def test_empty_list(self):
        assert linkedlist_to_list(None) == []

    def test_single_node(self):
        node = ListNode(1)
        assert linkedlist_to_list(node) == [1]

    def test_multiple_nodes(self):
        node = list_to_linkedlist([1, 2, 3, 4, 5])
        assert linkedlist_to_list(node) == [1, 2, 3, 4, 5]


class TestMergeKSortedLists:
    """Tests for merge_k_lists solution."""

    # Basic test cases from LeetCode
    def test_example1(self):
        """Example 1: [[1,4,5],[1,3,4],[2,6]] -> [1,1,2,3,4,4,5,6]"""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6])
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_example2(self):
        """Example 2: [] -> []"""
        lists = []
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == []

    def test_example3(self):
        """Example 3: [[]] -> []"""
        lists = [None]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == []

    # Edge cases
    def test_single_empty_list(self):
        """Single empty list returns empty result."""
        lists = []
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == []

    def test_single_list(self):
        """Single non-empty list returns same list."""
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_lists(self):
        """Two lists merge correctly."""
        lists = [
            list_to_linkedlist([1, 3, 5]),
            list_to_linkedlist([2, 4, 6])
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_lists_with_duplicates(self):
        """Lists with duplicate values merge correctly."""
        lists = [
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1]),
            list_to_linkedlist([1])
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1]

    def test_negative_numbers(self):
        """Lists with negative numbers work correctly."""
        lists = [
            list_to_linkedlist([-3, -1, 0]),
            list_to_linkedlist([-5, -2, 3])
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [-5, -3, -2, -1, 0, 3]

    def test_all_empty_lists(self):
        """Multiple empty lists return empty result."""
        lists = [None, None, None]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == []

    def test_mixed_empty_and_non_empty(self):
        """Mixed empty and non-empty lists work correctly."""
        lists = [
            None,
            list_to_linkedlist([1, 2]),
            None,
            list_to_linkedlist([3, 4])
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4]

    def test_large_gap_values(self):
        """Lists with large gaps in values work correctly."""
        lists = [
            list_to_linkedlist([1, 1000]),
            list_to_linkedlist([500, 1500])
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 500, 1000, 1500]

    def test_alternating_interleave(self):
        """Interleaved values merge correctly."""
        lists = [
            list_to_linkedlist([1, 3, 5, 7]),
            list_to_linkedlist([2, 4, 6, 8])
        ]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8]

    def test_many_small_lists(self):
        """Many small lists merge correctly."""
        lists = [list_to_linkedlist([i]) for i in range(10, 0, -1)]
        result = merge_k_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


class TestMergeKSortedListsHeap:
    """Tests for heap-based solution - should produce same results."""

    def test_same_as_divide_conquer(self):
        """Heap solution produces same result as divide-conquer."""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6])
        ]
        result_heap = merge_k_lists_heap(lists[:])

        lists2 = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6])
        ]
        result_dc = merge_k_lists_divide_conquer(lists2)

        assert linkedlist_to_list(result_heap) == linkedlist_to_list(result_dc)

    def test_empty_input(self):
        """Heap solution handles empty input."""
        lists = []
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == []

    def test_single_list(self):
        """Heap solution handles single list."""
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_lists_heap(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
