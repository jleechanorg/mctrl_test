from __future__ import annotations

from merge_k_sorted_lists import (
    ListNode,
    count_nodes,
    linkedlist_to_list,
    list_to_linkedlist,
    merge_k_lists,
)


def test_merge_two_empty():
    """Test merging empty lists."""
    assert merge_k_lists([]) is None
    assert merge_k_lists([None, None]) is None


def test_merge_single_list():
    """Test merging a single list."""
    head = list_to_linkedlist([1, 2, 3])
    result = merge_k_lists([head])
    assert linkedlist_to_list(result) == [1, 2, 3]


def test_merge_with_none_in_middle():
    """Test with None entry in the middle of the list."""
    l1 = list_to_linkedlist([1, 3, 5])
    l2 = None
    l3 = list_to_linkedlist([2, 4, 6])
    result = merge_k_lists([l1, l2, l3])
    assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]


def test_merge_three_sorted_lists():
    """Test merging three sorted lists."""
    l1 = list_to_linkedlist([1, 4, 5])
    l2 = list_to_linkedlist([1, 3, 4])
    l3 = list_to_linkedlist([2, 6])
    result = merge_k_lists([l1, l2, l3])
    assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]


def test_merge_with_duplicates():
    """Test merging lists with duplicate values."""
    l1 = list_to_linkedlist([1, 1, 1])
    l2 = list_to_linkedlist([1, 1])
    result = merge_k_lists([l1, l2])
    assert linkedlist_to_list(result) == [1, 1, 1, 1, 1]


def test_merge_single_element_lists():
    """Test merging lists each with single element."""
    l1 = list_to_linkedlist([1])
    l2 = list_to_linkedlist([0])
    l3 = list_to_linkedlist([2])
    result = merge_k_lists([l1, l2, l3])
    assert linkedlist_to_list(result) == [0, 1, 2]


def test_list_to_linkedlist_empty():
    """Test converting empty list to linked list."""
    assert list_to_linkedlist([]) is None


def test_linkedlist_to_list_empty():
    """Test converting None to list."""
    assert linkedlist_to_list(None) == []


def test_merge_already_sorted():
    """Test merging lists that are already in order."""
    l1 = list_to_linkedlist([1, 2, 3])
    l2 = list_to_linkedlist([4, 5, 6])
    l3 = list_to_linkedlist([7, 8, 9])
    result = merge_k_lists([l1, l2, l3])
    assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_merge_reverse_sorted():
    """Test merging lists in different order - first list is reverse sorted (invalid input)."""
    # Note: merge_k_lists expects sorted inputs, this test shows behavior with unsorted
    l1 = list_to_linkedlist([3, 2, 1])
    l2 = list_to_linkedlist([6, 5, 4])
    result = merge_k_lists([l1, l2])
    # With unsorted input, output is just concatenated in heap order
    assert linkedlist_to_list(result) == [3, 2, 1, 6, 5, 4]


def test_merge_interleaved():
    """Test merging interleaved lists."""
    l1 = list_to_linkedlist([1, 5, 9])
    l2 = list_to_linkedlist([2, 6, 10])
    l3 = list_to_linkedlist([3, 7, 11])
    l4 = list_to_linkedlist([4, 8, 12])
    result = merge_k_lists([l1, l2, l3, l4])
    assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]


def test_merge_negative_values():
    """Test merging lists with negative values."""
    l1 = list_to_linkedlist([-3, -1, 1])
    l2 = list_to_linkedlist([-2, 0, 2])
    result = merge_k_lists([l1, l2])
    assert linkedlist_to_list(result) == [-3, -2, -1, 0, 1, 2]


def test_count_nodes_empty():
    """Test counting nodes in an empty list."""
    assert count_nodes(None) == 0
    assert count_nodes(list_to_linkedlist([])) == 0


def test_count_nodes_single():
    """Test counting nodes in a single node list."""
    head = list_to_linkedlist([1])
    assert count_nodes(head) == 1


def test_count_nodes_multiple():
    """Test counting nodes in a multi-node list."""
    head = list_to_linkedlist([1, 2, 3, 4, 5])
    assert count_nodes(head) == 5
