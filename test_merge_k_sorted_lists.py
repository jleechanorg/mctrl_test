"""
Tests for Merge k Sorted Lists solution.
"""
from __future__ import annotations

import pytest
from merge_k_sorted_lists import (
    ListNode,
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
    merge_k_lists_naive,
    merge_two_lists,
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

    def test_to_list_single_node(self):
        node = ListNode(42)
        assert node.to_list() == [42]


class TestMergeTwoLists:
    """Tests for merging two sorted lists."""

    def test_merge_two_empty(self):
        result = merge_two_lists(None, None)
        assert result is None

    def test_merge_one_empty(self):
        l1 = ListNode.from_list([1, 2, 3])
        result = merge_two_lists(l1, None)
        assert result.to_list() == [1, 2, 3]

    def test_merge_both_empty(self):
        result = merge_two_lists(ListNode.from_list([]), ListNode.from_list([]))
        assert result is None

    def test_merge_interleaved(self):
        l1 = ListNode.from_list([1, 3, 5])
        l2 = ListNode.from_list([2, 4, 6])
        result = merge_two_lists(l1, l2)
        assert result.to_list() == [1, 2, 3, 4, 5, 6]

    def test_merge_duplicate_values(self):
        l1 = ListNode.from_list([1, 2, 3])
        l2 = ListNode.from_list([2, 3, 4])
        result = merge_two_lists(l1, l2)
        assert result.to_list() == [1, 2, 2, 3, 3, 4]


class TestMergeKListsHeap:
    """Tests for heap-based k-way merge."""

    def test_example1(self):
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_input(self):
        result = merge_k_lists_heap([])
        assert result is None

    def test_single_empty_list(self):
        lists = [[]]
        result = merge_k_lists_heap([ListNode.from_list(l) for l in lists])
        assert result is None

    def test_single_list(self):
        lists = [ListNode.from_list([1, 2, 3])]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 2, 3]

    def test_two_lists(self):
        lists = [
            ListNode.from_list([1, 3, 5]),
            ListNode.from_list([2, 4, 6]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6]

    def test_already_sorted(self):
        lists = [
            ListNode.from_list([1, 2, 3]),
            ListNode.from_list([4, 5, 6]),
            ListNode.from_list([7, 8, 9]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_reverse_sorted(self):
        # Each list is sorted in ascending order (as per problem constraints)
        # Test with non-overlapping ranges that need merging
        lists = [
            ListNode.from_list([3, 6, 9]),
            ListNode.from_list([2, 5, 8]),
            ListNode.from_list([1, 4, 7]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_with_negative_numbers(self):
        lists = [
            ListNode.from_list([-3, -1, 0]),
            ListNode.from_list([-2, 2]),
            ListNode.from_list([1, 3]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [-3, -2, -1, 0, 1, 2, 3]

    def test_single_element_lists(self):
        lists = [
            ListNode.from_list([5]),
            ListNode.from_list([3]),
            ListNode.from_list([7]),
            ListNode.from_list([1]),
        ]
        result = merge_k_lists_heap(lists)
        assert result.to_list() == [1, 3, 5, 7]


class TestMergeKListsDivideConquer:
    """Tests for divide-and-conquer k-way merge."""

    def test_example1(self):
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

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


class TestMergeKListsNaive:
    """Tests for naive one-by-one merge."""

    def test_example1(self):
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6]),
        ]
        result = merge_k_lists_naive(lists)
        assert result.to_list() == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_input(self):
        result = merge_k_lists_naive([])
        assert result is None


class TestAllMethodsConsistent:
    """Verify all three methods produce the same results."""

    @pytest.mark.parametrize(
        "lists",
        [
            [
                [1, 4, 5],
                [1, 3, 4],
                [2, 6],
            ],
            [
                [1, 2, 3],
                [4, 5, 6],
            ],
            [
                [1],
                [2],
                [3],
            ],
            [
                [1, 1, 1],
                [1, 1, 1],
            ],
        ],
    )
    def test_all_methods_equal(self, lists):
        result_heap = merge_k_lists_heap([ListNode.from_list(l) for l in lists])
        result_dc = merge_k_lists_divide_conquer([ListNode.from_list(l) for l in lists])
        result_naive = merge_k_lists_naive([ListNode.from_list(l) for l in lists])

        assert result_heap.to_list() == result_dc.to_list()
        assert result_heap.to_list() == result_naive.to_list()
