"""
Unit tests for Merge k Sorted Lists solution.
"""
import pytest
from merge_k_lists import (
    ListNode,
    merge_k_sorted_lists,
    merge_k_lists_heap,
    merge_k_lists_divide_conquer,
    list_to_linkedlist,
    linkedlist_to_list,
)


class TestListNode:
    """Test ListNode class and helper functions."""

    def test_list_to_linkedlist_empty(self):
        assert list_to_linkedlist([]) is None

    def test_list_to_linkedlist_single(self):
        head = list_to_linkedlist([1])
        assert head.val == 1
        assert head.next is None

    def test_list_to_linkedlist_multiple(self):
        head = list_to_linkedlist([1, 2, 3])
        assert head.val == 1
        assert head.next.val == 2
        assert head.next.next.val == 3
        assert head.next.next.next is None

    def test_linkedlist_to_list_empty(self):
        assert linkedlist_to_list(None) == []

    def test_linkedlist_to_list_multiple(self):
        head = list_to_linkedlist([1, 2, 3])
        assert linkedlist_to_list(head) == [1, 2, 3]


class TestMergeKSortedLists:
    """Test merge_k_sorted_lists function."""

    def test_example_1(self):
        """Example 1 from LeetCode."""
        lists = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6])
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_example_2_empty(self):
        """Example 2: Empty list of lists."""
        lists = []
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == []

    def test_example_3_single_empty_list(self):
        """Example 3: List containing one empty list."""
        lists = [list_to_linkedlist([])]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == []

    def test_single_list(self):
        """Test with a single non-empty list."""
        lists = [list_to_linkedlist([1, 2, 3])]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3]

    def test_two_lists(self):
        """Test with two lists."""
        lists = [
            list_to_linkedlist([1, 3, 5]),
            list_to_linkedlist([2, 4, 6])
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_lists_with_duplicates(self):
        """Test with duplicate values across lists."""
        lists = [
            list_to_linkedlist([1, 1, 1]),
            list_to_linkedlist([1, 1, 1]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [1, 1, 1, 1, 1, 1]

    def test_negative_numbers(self):
        """Test with negative numbers."""
        lists = [
            list_to_linkedlist([-3, -1, 0]),
            list_to_linkedlist([-2, 2]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [-3, -2, -1, 0, 2]

    def test_mixed_positive_negative(self):
        """Test with mixed positive and negative numbers."""
        lists = [
            list_to_linkedlist([-5, 5]),
            list_to_linkedlist([-3, 3]),
            list_to_linkedlist([-1, 1]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [-5, -3, -1, 1, 3, 5]

    def test_single_element_each(self):
        """Test with single element in each list."""
        lists = [
            list_to_linkedlist([5]),
            list_to_linkedlist([1]),
            list_to_linkedlist([3]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [1, 3, 5]

    def test_already_sorted(self):
        """Test with lists that are already sorted individually."""
        lists = [
            list_to_linkedlist([1, 2, 3]),
            list_to_linkedlist([4, 5, 6]),
            list_to_linkedlist([7, 8, 9]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linkedlist_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9]


class TestDivideAndConquer:
    """Test the divide and conquer approach."""

    def test_same_as_heap(self):
        """Verify divide and conquer produces same results as heap approach."""
        lists_heap = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6])
        ]
        lists_dc = [
            list_to_linkedlist([1, 4, 5]),
            list_to_linkedlist([1, 3, 4]),
            list_to_linkedlist([2, 6])
        ]
        heap_result = merge_k_lists_heap(lists_heap)
        dc_result = merge_k_lists_divide_conquer(lists_dc)
        assert linkedlist_to_list(heap_result) == linkedlist_to_list(dc_result)

    def test_empty_and_none(self):
        """Test edge cases for divide and conquer."""
        lists = []
        assert merge_k_lists_divide_conquer(lists) is None

        lists = [None]
        assert merge_k_lists_divide_conquer(lists) is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
