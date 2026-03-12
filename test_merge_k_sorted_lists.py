"""Tests for Merge k Sorted Lists solution."""

from __future__ import annotations

import pytest
from merge_k_sorted_lists import (
    ListNode,
    merge_two_lists,
    merge_k_lists,
    merge_k_lists_heap,
    merge_k_lists_brute_force,
    merge_k_lists_divide_conquer,
)


class TestListNode:
    """Tests for ListNode utility methods."""

    def test_from_list_empty(self):
        assert ListNode.from_list([]) is None

    def test_from_list_single(self):
        node = ListNode.from_list([1])
        assert node.val == 1
        assert node.next is None

    def test_from_list_multiple(self):
        node = ListNode.from_list([1, 2, 3])
        assert node.to_list() == [1, 2, 3]

    def test_to_list_empty(self):
        # Empty list represented as None
        assert ListNode(None).to_list() == [] if ListNode(None) else True


class TestMergeTwoLists:
    """Tests for merging two sorted lists."""

    def test_both_empty(self):
        assert merge_two_lists(None, None) is None

    def test_one_empty(self):
        l1 = ListNode.from_list([1, 2, 3])
        result = merge_two_lists(l1, None)
        assert result.to_list() == [1, 2, 3]

    def test_merge_ascending(self):
        l1 = ListNode.from_list([1, 3, 5])
        l2 = ListNode.from_list([2, 4, 6])
        result = merge_two_lists(l1, l2)
        assert result.to_list() == [1, 2, 3, 4, 5, 6]

    def test_merge_with_duplicates(self):
        l1 = ListNode.from_list([1, 1, 3])
        l2 = ListNode.from_list([1, 2, 3])
        result = merge_two_lists(l1, l2)
        assert result.to_list() == [1, 1, 1, 2, 3, 3]

    def test_merge_one_element_lists(self):
        l1 = ListNode.from_list([1])
        l2 = ListNode.from_list([2])
        result = merge_two_lists(l1, l2)
        assert result.to_list() == [1, 2]


class TestMergeKListsDivideConquer:
    """Tests for divide and conquer merge approach."""

    def test_empty_input(self):
        result = merge_k_lists_divide_conquer([])
        assert result is None

    def test_single_list(self):
        lists = [ListNode.from_list([1, 2, 3])]
        result = merge_k_lists_divide_conquer(lists)
        assert result.to_list() == [1, 2, 3]

    def test_two_lists(self):
        lists = [
            ListNode.from_list([1, 3, 5]),
            ListNode.from_list([2, 4, 6]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6]

    def test_three_lists(self):
        lists = [
            ListNode.from_list([1, 4, 7]),
            ListNode.from_list([2, 5, 8]),
            ListNode.from_list([3, 6, 9]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_lists_with_different_lengths(self):
        lists = [
            ListNode.from_list([1]),
            ListNode.from_list([2, 3, 4, 5]),
            ListNode.from_list([6, 7, 8, 9, 10]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_empty_lists_in_middle(self):
        lists = [
            ListNode.from_list([1, 2]),
            None,
            ListNode.from_list([3, 4]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert result.to_list() == [1, 2, 3, 4]

    def test_many_empty_lists(self):
        lists = [None, None, None]
        result = merge_k_lists_divide_conquer(lists)
        assert result is None

    def test_duplicates_across_lists(self):
        lists = [
            ListNode.from_list([1, 1, 1]),
            ListNode.from_list([1, 1]),
            ListNode.from_list([1]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert result.to_list() == [1, 1, 1, 1, 1, 1]


class TestMergeKListsHeap:
    """Tests for heap-based merge approach."""

    def test_empty_input(self):
        result = merge_k_lists_heap([])
        assert result is None

    def test_single_list(self):
        lists = [ListNode.from_list([1, 2, 3])]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 2, 3]

    def test_three_lists(self):
        lists = [
            ListNode.from_list([1, 4, 7]),
            ListNode.from_list([2, 5, 8]),
            ListNode.from_list([3, 6, 9]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_with_none_in_middle(self):
        lists = [
            ListNode.from_list([1]),
            None,
            ListNode.from_list([2]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 2]


class TestMergeKListsBruteForce:
    """Tests for brute force approach."""

    def test_three_lists(self):
        lists = [
            ListNode.from_list([1, 4, 7]),
            ListNode.from_list([2, 5, 8]),
            ListNode.from_list([3, 6, 9]),
        ]
        result = merge_k_lists_brute_force(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6, 7, 8, 9]


class TestAllAlgorithmsEquivalent:
    """Verify all algorithms produce same results."""

    @pytest.fixture
    def test_lists(self):
        return [
            ListNode.from_list([1, 4, 7, 10]),
            ListNode.from_list([2, 5, 8]),
            ListNode.from_list([3, 6, 9, 11, 12]),
            None,
            ListNode.from_list([0]),
        ]

    def test_all_produce_same_result(self, test_lists):
        result_dc = merge_k_lists_divide_conquer(test_lists)
        result_heap = merge_k_lists_heap(test_lists)
        result_brute = merge_k_lists_brute_force(test_lists)

        assert result_dc.to_list() == result_heap.to_list()
        assert result_dc.to_list() == result_brute.to_list()
        assert result_dc.to_list() == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]


class TestEdgeCases:
    """Edge case tests."""

    def test_large_values(self):
        lists = [
            ListNode.from_list([10**9]),
            ListNode.from_list([10**9 + 1]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [10**9, 10**9 + 1]

    def test_negative_numbers(self):
        lists = [
            ListNode.from_list([-3, -1, 0]),
            ListNode.from_list([-2, 2]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [-3, -2, -1, 0, 2]

    def test_single_element_each(self):
        lists = [ListNode.from_list([i]) for i in range(5)]
        result = merge_k_lists(lists)
        assert result.to_list() == [0, 1, 2, 3, 4]
