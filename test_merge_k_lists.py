from __future__ import annotations

import pytest

from merge_k_lists import (
    ListNode,
    list_to_linked,
    linked_to_list,
    merge_k_sorted_lists,
)


def test_merge_k_lists_example_1():
    """Test example 1 from LeetCode."""
    l1 = list_to_linked([1, 4, 5])
    l2 = list_to_linked([1, 3, 4])
    l3 = list_to_linked([2, 6])
    result = merge_k_sorted_lists([l1, l2, l3])
    assert linked_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]


def test_merge_k_lists_example_2():
    """Test empty input."""
    result = merge_k_sorted_lists([])
    assert linked_to_list(result) == []


def test_merge_k_lists_example_3():
    """Test list with empty list."""
    result = merge_k_sorted_lists([[]])
    assert linked_to_list(result) == []


def test_merge_single_list():
    """Test merging a single list."""
    l1 = list_to_linked([1, 2, 3])
    result = merge_k_sorted_lists([l1])
    assert linked_to_list(result) == [1, 2, 3]


def test_merge_two_lists():
    """Test merging two lists."""
    l1 = list_to_linked([1, 3, 5])
    l2 = list_to_linked([2, 4, 6])
    result = merge_k_sorted_lists([l1, l2])
    assert linked_to_list(result) == [1, 2, 3, 4, 5, 6]


def test_merge_lists_different_lengths():
    """Test merging lists of different lengths."""
    l1 = list_to_linked([1, 2, 3, 4, 5])
    l2 = list_to_linked([1, 2])
    l3 = list_to_linked([6])
    result = merge_k_sorted_lists([l1, l2, l3])
    assert linked_to_list(result) == [1, 1, 2, 2, 3, 4, 5, 6]


def test_merge_lists_with_duplicates():
    """Test merging lists with many duplicates."""
    l1 = list_to_linked([1, 1, 1])
    l2 = list_to_linked([1, 1, 1])
    l3 = list_to_linked([1, 1, 1])
    result = merge_k_sorted_lists([l1, l2, l3])
    assert linked_to_list(result) == [1, 1, 1, 1, 1, 1, 1, 1, 1]


def test_merge_negative_numbers():
    """Test merging lists with negative numbers."""
    l1 = list_to_linked([-3, -2, -1])
    l2 = list_to_linked([-5, -4, -3])
    l3 = list_to_linked([0, 1, 2])
    result = merge_k_sorted_lists([l1, l2, l3])
    assert linked_to_list(result) == [-5, -4, -3, -3, -2, -1, 0, 1, 2]


def test_merge_lists_with_none():
    """Test merging lists where some are None."""
    l1 = list_to_linked([1, 2, 3])
    l2 = None
    l3 = list_to_linked([4, 5, 6])
    result = merge_k_sorted_lists([l1, l2, l3])
    assert linked_to_list(result) == [1, 2, 3, 4, 5, 6]


def test_merge_all_none():
    """Test merging when all lists are None."""
    result = merge_k_sorted_lists([None, None])
    assert linked_to_list(result) == []


def test_merge_large_k():
    """Test merging with large k (many small lists)."""
    lists = [list_to_linked([i]) for i in range(100)]
    result = merge_k_sorted_lists(lists)
    assert linked_to_list(result) == list(range(100))


def test_list_node_structure():
    """Test that ListNode has correct structure."""
    node = ListNode(5, ListNode(10))
    assert node.val == 5
    assert node.next.val == 10
    assert node.next.next is None


def test_list_to_linked_conversion():
    """Test list to linked list conversion."""
    arr = [1, 2, 3, 4, 5]
    head = list_to_linked(arr)
    assert linked_to_list(head) == arr


def test_list_to_linked_empty():
    """Test list to linked list conversion with empty list."""
    head = list_to_linked([])
    assert head is None


def test_linked_to_list_empty():
    """Test linked to list conversion with None."""
    result = linked_to_list(None)
    assert result == []
