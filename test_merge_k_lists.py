"""
Tests for Merge k Sorted Lists solution.
"""
from __future__ import annotations

import pytest

from merge_k_lists import (
    ListNode,
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
    create_linked_list,
    linked_list_to_list,
)


class TestListNode:
    """Tests for ListNode and helper functions."""

    def test_create_linked_list_empty(self):
        assert create_linked_list([]) is None

    def test_create_linked_list_single(self):
        head = create_linked_list([1])
        assert head.val == 1
        assert head.next is None

    def test_create_linked_list_multiple(self):
        head = create_linked_list([1, 2, 3])
        assert head.val == 1
        assert head.next.val == 2
        assert head.next.next.val == 3
        assert head.next.next.next is None

    def test_linked_list_to_list_empty(self):
        assert linked_list_to_list(None) == []

    def test_linked_list_to_list_single(self):
        assert linked_list_to_list(ListNode(5)) == [5]

    def test_linked_list_to_list_multiple(self):
        head = create_linked_list([1, 2, 3])
        assert linked_list_to_list(head) == [1, 2, 3]


class TestMergeKListsHeap:
    """Tests for heap-based merge implementation."""

    def test_empty_list(self):
        result = merge_k_lists_heap([])
        assert result is None

    def test_single_empty_list(self):
        result = merge_k_lists_heap([None])
        assert result is None

    def test_single_list(self):
        lists = [create_linked_list([1, 2, 3])]
        result = merge_k_lists_heap(lists)
        assert linked_list_to_list(result) == [1, 2, 3]

    def test_two_lists(self):
        lists = [create_linked_list([1, 3, 5]), create_linked_list([2, 4, 6])]
        result = merge_k_lists_heap(lists)
        assert linked_list_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_three_lists(self):
        lists = [
            create_linked_list([1, 4, 5]),
            create_linked_list([1, 3, 4]),
            create_linked_list([2, 6]),
        ]
        result = merge_k_lists_heap(lists)
        assert linked_list_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_with_duplicates(self):
        lists = [create_linked_list([1, 1, 1]), create_linked_list([1, 1])]
        result = merge_k_lists_heap(lists)
        assert linked_list_to_list(result) == [1, 1, 1, 1, 1]

    def test_already_sorted_single_element(self):
        lists = [create_linked_list([1]), create_linked_list([2]), create_linked_list([3])]
        result = merge_k_lists_heap(lists)
        assert linked_list_to_list(result) == [1, 2, 3]

    def test_negative_numbers(self):
        lists = [create_linked_list([-3, -1, 0]), create_linked_list([-2, 2])]
        result = merge_k_lists_heap(lists)
        assert linked_list_to_list(result) == [-3, -2, -1, 0, 2]

    def test_large_numbers(self):
        lists = [create_linked_list([10**9]), create_linked_list([10**8])]
        result = merge_k_lists_heap(lists)
        assert linked_list_to_list(result) == [10**8, 10**9]

    def test_one_list_empty(self):
        lists = [create_linked_list([]), create_linked_list([1, 2])]
        result = merge_k_lists_heap(lists)
        assert linked_list_to_list(result) == [1, 2]

    def test_all_empty_lists(self):
        lists = [create_linked_list([]), create_linked_list([])]
        result = merge_k_lists_heap(lists)
        assert result is None


class TestMergeKListsDivideConquer:
    """Tests for divide-and-conquer merge implementation."""

    def test_empty_list(self):
        result = merge_k_lists_divide_conquer([])
        assert result is None

    def test_single_empty_list(self):
        result = merge_k_lists_divide_conquer([None])
        assert result is None

    def test_single_list(self):
        lists = [create_linked_list([1, 2, 3])]
        result = merge_k_lists_divide_conquer(lists)
        assert linked_list_to_list(result) == [1, 2, 3]

    def test_two_lists(self):
        lists = [create_linked_list([1, 3, 5]), create_linked_list([2, 4, 6])]
        result = merge_k_lists_divide_conquer(lists)
        assert linked_list_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_three_lists(self):
        lists = [
            create_linked_list([1, 4, 5]),
            create_linked_list([1, 3, 4]),
            create_linked_list([2, 6]),
        ]
        result = merge_k_lists_divide_conquer(lists)
        assert linked_list_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_with_duplicates(self):
        lists = [create_linked_list([1, 1, 1]), create_linked_list([1, 1])]
        result = merge_k_lists_divide_conquer(lists)
        assert linked_list_to_list(result) == [1, 1, 1, 1, 1]

    def test_negative_numbers(self):
        lists = [create_linked_list([-3, -1, 0]), create_linked_list([-2, 2])]
        result = merge_k_lists_divide_conquer(lists)
        assert linked_list_to_list(result) == [-3, -2, -1, 0, 2]

    def test_one_list_empty(self):
        lists = [create_linked_list([]), create_linked_list([1, 2])]
        result = merge_k_lists_divide_conquer(lists)
        assert linked_list_to_list(result) == [1, 2]

    def test_all_empty_lists(self):
        lists = [create_linked_list([]), create_linked_list([])]
        result = merge_k_lists_divide_conquer(lists)
        assert result is None


class TestBothImplementations:
    """Verify both implementations produce the same results."""

    @pytest.mark.parametrize("implementation", [merge_k_lists_heap, merge_k_lists_divide_conquer])
    def test_same_results(self, implementation):
        lists = [
            create_linked_list([1, 4, 5]),
            create_linked_list([1, 3, 4]),
            create_linked_list([2, 6]),
        ]
        result = implementation(lists)
        assert linked_list_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    @pytest.mark.parametrize("implementation", [merge_k_lists_heap, merge_k_lists_divide_conquer])
    def test_large_k(self, implementation):
        # Test with many small lists
        lists = [create_linked_list([i]) for i in range(10, 0, -1)]
        result = implementation(lists)
        assert linked_list_to_list(result) == list(range(1, 11))

    @pytest.mark.parametrize("implementation", [merge_k_lists_heap, merge_k_lists_divide_conquer])
    def test_already_merged(self, implementation):
        # All lists already contain elements in order
        lists = [create_linked_list([1]), create_linked_list([2, 3]), create_linked_list([4, 5, 6])]
        result = implementation(lists)
        assert linked_list_to_list(result) == [1, 2, 3, 4, 5, 6]
