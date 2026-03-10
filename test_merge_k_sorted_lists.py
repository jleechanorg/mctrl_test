from __future__ import annotations

import pytest

from merge_k_sorted_lists import (
    ListNode,
    merge_k_sorted_lists,
    merge_k_sorted_lists_divide_conquer,
)


def _to_list(head: ListNode | None) -> list[int]:
    """Convert linked list to Python list for easy comparison."""
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result


def test_merge_k_sorted_lists_leetcode_example():
    """Test the LeetCode example: [[1,4,5],[1,3,4],[2,6]]"""
    list1 = ListNode.from_list([1, 4, 5])
    list2 = ListNode.from_list([1, 3, 4])
    list3 = ListNode.from_list([2, 6])

    result = merge_k_sorted_lists([list1, list2, list3])
    assert _to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]


def test_merge_k_sorted_lists_divide_conquer_leetcode():
    """Test divide and conquer approach on LeetCode example."""
    list1 = ListNode.from_list([1, 4, 5])
    list2 = ListNode.from_list([1, 3, 4])
    list3 = ListNode.from_list([2, 6])

    result = merge_k_sorted_lists_divide_conquer([list1, list2, list3])
    assert _to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]


def test_merge_k_sorted_lists_empty_input():
    """Test with empty list of lists."""
    assert merge_k_sorted_lists([]) is None


def test_merge_k_sorted_lists_all_empty():
    """Test with all None lists."""
    assert merge_k_sorted_lists([None, None, None]) is None


def test_merge_k_sorted_lists_single_list():
    """Test with a single non-empty list."""
    list1 = ListNode.from_list([1, 2, 3])
    result = merge_k_sorted_lists([list1])
    assert _to_list(result) == [1, 2, 3]


def test_merge_k_sorted_lists_two_lists():
    """Test with two lists."""
    list1 = ListNode.from_list([1, 4, 6])
    list2 = ListNode.from_list([2, 5, 7])
    result = merge_k_sorted_lists([list1, list2])
    assert _to_list(result) == [1, 2, 4, 5, 6, 7]


def test_merge_k_sorted_lists_already_sorted():
    """Test with already sorted large list."""
    lists = [ListNode.from_list([i]) for i in range(100)]
    result = merge_k_sorted_lists(lists)
    assert _to_list(result) == list(range(100))


def test_merge_k_sorted_lists_reverse_sorted():
    """Test with reverse sorted input (smallest at end)."""
    # [100-i for i in range(100)] = [100,99,98,...,1]
    lists = [ListNode.from_list([100 - i]) for i in range(100)]
    result = merge_k_sorted_lists(lists)
    # Merged result should be [1,2,3,...,100]
    assert _to_list(result) == list(range(1, 101))


def test_merge_k_sorted_lists_with_duplicates():
    """Test with lists containing duplicate values."""
    list1 = ListNode.from_list([1, 1, 1])
    list2 = ListNode.from_list([1, 1, 1])
    list3 = ListNode.from_list([1, 1, 1])
    result = merge_k_sorted_lists([list1, list2, list3])
    assert _to_list(result) == [1] * 9


def test_merge_k_sorted_lists_interleaved():
    """Test with interleaved values across lists."""
    list1 = ListNode.from_list([1, 10, 20, 30])
    list2 = ListNode.from_list([2, 12, 22, 32])
    list3 = ListNode.from_list([3, 13, 23, 33])
    result = merge_k_sorted_lists([list1, list2, list3])
    assert _to_list(result) == [
        1, 2, 3, 10, 12, 13, 20, 22, 23, 30, 32, 33
    ]


def test_merge_k_sorted_lists_one_empty():
    """Test when one list is empty but others aren't."""
    list1 = ListNode.from_list([1, 2, 3])
    list2 = None
    list3 = ListNode.from_list([4, 5, 6])
    result = merge_k_sorted_lists([list1, list2, list3])
    assert _to_list(result) == [1, 2, 3, 4, 5, 6]


def test_merge_k_sorted_lists_single_node_each():
    """Test with single node in each list."""
    lists = [ListNode.from_list([i]) for i in [5, 3, 1, 4, 2]]
    result = merge_k_sorted_lists(lists)
    assert _to_list(result) == [1, 2, 3, 4, 5]


def test_merge_k_sorted_lists_divide_conquer_empty():
    """Test divide and conquer with empty input."""
    assert merge_k_sorted_lists_divide_conquer([]) is None


def test_merge_k_sorted_lists_divide_conquer_single():
    """Test divide and conquer with single list."""
    list1 = ListNode.from_list([1, 2, 3])
    result = merge_k_sorted_lists_divide_conquer([list1])
    assert _to_list(result) == [1, 2, 3]


def test_merge_k_sorted_lists_divide_conquer_various():
    """Test divide and conquer with various inputs."""
    list1 = ListNode.from_list([1, 4, 7, 10])
    list2 = ListNode.from_list([2, 5, 8])
    list3 = ListNode.from_list([3, 6, 9, 11, 12])

    result = merge_k_sorted_lists_divide_conquer([list1, list2, list3])
    assert _to_list(result) == [
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
    ]


def test_merge_k_sorted_lists_large_values():
    """Test with large values."""
    list1 = ListNode.from_list([10**9])
    list2 = ListNode.from_list([10**8])
    list3 = ListNode.from_list([10**7])
    result = merge_k_sorted_lists([list1, list2, list3])
    assert _to_list(result) == [10**7, 10**8, 10**9]


def test_merge_k_sorted_lists_negative_values():
    """Test with negative values."""
    list1 = ListNode.from_list([-3, -1, 0, 2])
    list2 = ListNode.from_list([-2, 1, 3])
    result = merge_k_sorted_lists([list1, list2])
    assert _to_list(result) == [-3, -2, -1, 0, 1, 2, 3]
