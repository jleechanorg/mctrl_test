"""
Unit tests for Merge k Sorted Lists solution.
"""
from __future__ import annotations

import pytest
from merge_k_sorted import (
    ListNode,
    merge_k_sorted_lists,
    merge_k_sorted_lists_divide_conquer,
    merge_k_sorted_arrays,
)


class TestListNode:
    """Test ListNode functionality."""

    def test_listnode_creation(self):
        node = ListNode(1)
        assert node.val == 1
        assert node.next is None

    def test_listnode_with_next(self):
        node1 = ListNode(1)
        node2 = ListNode(2)
        node1.next = node2
        assert node1.val == 1
        assert node1.next.val == 2

    def test_listnode_lt_comparison(self):
        node1 = ListNode(1)
        node2 = ListNode(2)
        assert node1 < node2
        assert not (node2 < node1)


def list_to_array(head: ListNode | None) -> list[int]:
    """Convert linked list to array for easy testing."""
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result


def array_to_list(arr: list[int]) -> ListNode | None:
    """Convert array to linked list."""
    if not arr:
        return None
    dummy = ListNode(-1)
    current = dummy
    for val in arr:
        current.next = ListNode(val)
        current = current.next
    return dummy.next


class TestMergeKSortedLists:
    """Test cases for merge_k_sorted_lists."""

    def test_empty_list(self):
        result = merge_k_sorted_lists([])
        assert result is None

    def test_single_empty_list(self):
        result = merge_k_sorted_lists([None])
        assert result is None

    def test_single_list(self):
        lists = [array_to_list([1, 2, 3])]
        result = merge_k_sorted_lists(lists)
        assert list_to_array(result) == [1, 2, 3]

    def test_two_sorted_lists(self):
        lists = [array_to_list([1, 4, 5]), array_to_list([1, 3, 4])]
        result = merge_k_sorted_lists(lists)
        assert list_to_array(result) == [1, 1, 3, 4, 4, 5]

    def test_three_sorted_lists(self):
        lists = [
            array_to_list([1, 4, 5]),
            array_to_list([1, 3, 4]),
            array_to_list([2, 6]),
        ]
        result = merge_k_sorted_lists(lists)
        assert list_to_array(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_lists_with_duplicates(self):
        lists = [
            array_to_list([1, 1, 1]),
            array_to_list([1, 1]),
        ]
        result = merge_k_sorted_lists(lists)
        assert list_to_array(result) == [1, 1, 1, 1, 1]

    def test_single_element_lists(self):
        lists = [array_to_list([1]), array_to_list([2]), array_to_list([3])]
        result = merge_k_sorted_lists(lists)
        assert list_to_array(result) == [1, 2, 3]

    def test_already_sorted_list(self):
        lists = [array_to_list([1, 2, 3, 4, 5])]
        result = merge_k_sorted_lists(lists)
        assert list_to_array(result) == [1, 2, 3, 4, 5]

    def test_reverse_sorted_input(self):
        # One list is reverse sorted but we still get correct merge
        lists = [array_to_list([5, 4, 3, 2, 1])]
        result = merge_k_sorted_lists(lists)
        assert list_to_array(result) == [5, 4, 3, 2, 1]

    def test_mixed_empty_and_non_empty(self):
        lists = [None, array_to_list([1, 2, 3]), None, array_to_list([4, 5])]
        result = merge_k_sorted_lists(lists)
        assert list_to_array(result) == [1, 2, 3, 4, 5]

    def test_large_values(self):
        lists = [
            array_to_list([10**9, 10**9 + 1]),
            array_to_list([-10**9, -10**9 + 1]),
        ]
        result = merge_k_sorted_lists(lists)
        assert list_to_array(result) == [-10**9, -10**9 + 1, 10**9, 10**9 + 1]

    def test_negative_numbers(self):
        lists = [array_to_list([-3, -1, 0]), array_to_list([-2, 1])]
        result = merge_k_sorted_lists(lists)
        assert list_to_array(result) == [-3, -2, -1, 0, 1]


class TestMergeKSortedListsDivideConquer:
    """Test cases for divide and conquer approach."""

    def test_empty(self):
        result = merge_k_sorted_lists_divide_conquer([])
        assert result is None

    def test_single_list(self):
        lists = [array_to_list([1, 2, 3])]
        result = merge_k_sorted_lists_divide_conquer(lists)
        assert list_to_array(result) == [1, 2, 3]

    def test_two_lists(self):
        lists = [array_to_list([1, 4, 5]), array_to_list([1, 3, 4])]
        result = merge_k_sorted_lists_divide_conquer(lists)
        assert list_to_array(result) == [1, 1, 3, 4, 4, 5]

    def test_three_lists(self):
        lists = [
            array_to_list([1, 4, 5]),
            array_to_list([1, 3, 4]),
            array_to_list([2, 6]),
        ]
        result = merge_k_sorted_lists_divide_conquer(lists)
        assert list_to_array(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_mixed_empty(self):
        lists = [None, array_to_list([1, 2]), None]
        result = merge_k_sorted_lists_divide_conquer(lists)
        assert list_to_array(result) == [1, 2]


class TestMergeKSortedArrays:
    """Test cases for array-based solution."""

    def test_empty_arrays(self):
        result = merge_k_sorted_arrays([])
        assert result == []

    def test_single_array(self):
        result = merge_k_sorted_arrays([[1, 2, 3]])
        assert result == [1, 2, 3]

    def test_two_arrays(self):
        result = merge_k_sorted_arrays([[1, 4, 5], [1, 3, 4]])
        assert result == [1, 1, 3, 4, 4, 5]

    def test_three_arrays(self):
        result = merge_k_sorted_arrays([[1, 4, 5], [1, 3, 4], [2, 6]])
        assert result == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_mixed_empty_arrays(self):
        result = merge_k_sorted_arrays([[], [1, 2], [], [3]])
        assert result == [1, 2, 3]

    def test_arrays_with_duplicates(self):
        result = merge_k_sorted_arrays([[1, 1], [1], [1, 1, 1]])
        assert result == [1, 1, 1, 1, 1, 1]


class TestBothAlgorithms:
    """Verify both algorithms produce same results."""

    @pytest.mark.parametrize(
        "lists",
        [
            [[1, 4, 5], [1, 3, 4], [2, 6]],
            [[], [1, 2], []],
            [[1]],
            [[1], [2], [3], [4]],
            [[1, 1, 1], [1, 1], [1]],
        ],
    )
    def test_algorithms_match(self, lists):
        """Both heap and divide-conquer should produce identical results."""
        # Test with linked lists
        list_nodes = [array_to_list(arr) if arr else None for arr in lists]

        heap_result = merge_k_sorted_lists(list_nodes)
        dc_result = merge_k_sorted_lists_divide_conquer(list_nodes)

        assert list_to_array(heap_result) == list_to_array(dc_result)

        # Test with arrays
        array_result = merge_k_sorted_arrays(lists)
        assert list_to_array(heap_result) == array_result
