from __future__ import annotations

import pytest
from merge_k_sorted_lists import (
    ListNode,
    merge_k_lists,
    list_to_linked_list,
    linked_list_to_list,
)


def test_merge_k_lists_leetcode_example():
    """LeetCode example: [[1,4,5],[1,3,4],[2,6]] -> [1,1,2,3,4,4,5,6]"""
    lists = [
        list_to_linked_list([1, 4, 5]),
        list_to_linked_list([1, 3, 4]),
        list_to_linked_list([2, 6]),
    ]
    result = merge_k_lists(lists)
    assert linked_list_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]


def test_merge_k_lists_empty_input():
    """Empty list of lists should return None."""
    assert merge_k_lists([]) is None


def test_merge_k_lists_with_empty_lists():
    """Lists containing empty lists should work."""
    lists = [
        list_to_linked_list([]),
        list_to_linked_list([1, 3, 4]),
        list_to_linked_list([]),
    ]
    result = merge_k_lists(lists)
    assert linked_list_to_list(result) == [1, 3, 4]


def test_merge_k_lists_single_list():
    """Single list should be returned as-is."""
    lists = [list_to_linked_list([1, 2, 3])]
    result = merge_k_lists(lists)
    assert linked_list_to_list(result) == [1, 2, 3]


def test_merge_k_lists_single_element():
    """Single element in each list."""
    lists = [
        list_to_linked_list([1]),
        list_to_linked_list([0]),
    ]
    result = merge_k_lists(lists)
    assert linked_list_to_list(result) == [0, 1]


def test_merge_k_lists_already_sorted():
    """Already sorted lists should merge correctly."""
    lists = [
        list_to_linked_list([1, 2, 3]),
        list_to_linked_list([4, 5, 6]),
        list_to_linked_list([7, 8, 9]),
    ]
    result = merge_k_lists(lists)
    assert linked_list_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_merge_k_lists_interleaved():
    """Interleaved sorted input."""
    lists = [
        list_to_linked_list([1, 5, 9]),
        list_to_linked_list([2, 6]),
        list_to_linked_list([3, 7, 8]),
    ]
    result = merge_k_lists(lists)
    assert linked_list_to_list(result) == [1, 2, 3, 5, 6, 7, 8, 9]
