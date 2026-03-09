"""
Comprehensive tests for Merge K Sorted Lists solution.
Tests both heap-based and divide-and-conquer approaches.
"""
from __future__ import annotations

import pytest
from merge_k_sorted_lists import (
    ListNode,
    merge_k_sorted_lists,
    merge_k_sorted_lists_divide_conquer,
    create_linked_list,
    linked_list_to_list,
)


class TestMergeKSortedLists:
    """Test cases for merge_k_sorted_lists function."""

    def test_example_1(self):
        """Test case from LeetCode example."""
        lists = [
            create_linked_list([1, 4, 5]),
            create_linked_list([1, 3, 4]),
            create_linked_list([2, 6]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linked_list_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_example_1_divide_conquer(self):
        """Test divide and conquer approach."""
        lists = [
            create_linked_list([1, 4, 5]),
            create_linked_list([1, 3, 4]),
            create_linked_list([2, 6]),
        ]
        result = merge_k_sorted_lists_divide_conquer(lists)
        assert linked_list_to_list(result) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_list_of_lists(self):
        """Test with empty list of lists."""
        lists = []
        result = merge_k_sorted_lists(lists)
        assert result is None

    def test_empty_list_of_lists_divide_conquer(self):
        """Test divide and conquer with empty list."""
        lists = []
        result = merge_k_sorted_lists_divide_conquer(lists)
        assert result is None

    def test_lists_containing_empty_lists(self):
        """Test with lists containing empty linked lists."""
        lists = [
            create_linked_list([1, 4, 5]),
            None,
            create_linked_list([2, 6]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linked_list_to_list(result) == [1, 2, 4, 5, 6]

    def test_single_list(self):
        """Test with a single linked list."""
        lists = [create_linked_list([1, 2, 3])]
        result = merge_k_sorted_lists(lists)
        assert linked_list_to_list(result) == [1, 2, 3]

    def test_single_element_each(self):
        """Test with single element in each list."""
        lists = [
            create_linked_list([1]),
            create_linked_list([0]),
            create_linked_list([2]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linked_list_to_list(result) == [0, 1, 2]

    def test_negative_numbers(self):
        """Test with negative numbers."""
        lists = [
            create_linked_list([-5, -3, 0]),
            create_linked_list([-2, 2]),
            create_linked_list([-10, -1, 5]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linked_list_to_list(result) == [-10, -5, -3, -2, -1, 0, 2, 5]

    def test_already_sorted(self):
        """Test with already sorted input."""
        lists = [
            create_linked_list([1, 2, 3]),
            create_linked_list([4, 5, 6]),
            create_linked_list([7, 8, 9]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linked_list_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_reverse_sorted(self):
        """Test with reverse sorted input."""
        lists = [
            create_linked_list([9, 8, 7]),
            create_linked_list([6, 5, 4]),
            create_linked_list([3, 2, 1]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linked_list_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_duplicates_in_multiple_lists(self):
        """Test with duplicate values across lists."""
        lists = [
            create_linked_list([1, 1, 1]),
            create_linked_list([1, 1, 2]),
            create_linked_list([1, 2, 2]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linked_list_to_list(result) == [1, 1, 1, 1, 1, 1, 2, 2, 2]

    def test_large_values(self):
        """Test with large values."""
        lists = [
            create_linked_list([10000, 20000]),
            create_linked_list([-10000, 0]),
            create_linked_list([5000, 15000]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linked_list_to_list(result) == [-10000, 0, 5000, 10000, 15000, 20000]

    def test_two_lists(self):
        """Test with exactly two lists."""
        lists = [
            create_linked_list([1, 3, 5]),
            create_linked_list([2, 4, 6]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linked_list_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_very_uneven_lists(self):
        """Test with very different length lists."""
        lists = [
            create_linked_list([1]),
            create_linked_list([2, 3, 4, 5, 6, 7, 8, 9, 10]),
            create_linked_list([]),
        ]
        result = merge_k_sorted_lists(lists)
        assert linked_list_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_all_none_except_one(self):
        """Test with only one non-None list."""
        lists = [None, None, create_linked_list([1, 2, 3]), None]
        result = merge_k_sorted_lists(lists)
        assert linked_list_to_list(result) == [1, 2, 3]


class TestDivideAndConquer:
    """Test cases specifically for divide and conquer approach."""

    def test_equivalence_with_heap(self):
        """Verify both approaches produce same results."""
        test_cases = [
            [
                create_linked_list([1, 4, 5]),
                create_linked_list([1, 3, 4]),
                create_linked_list([2, 6]),
            ],
            [create_linked_list([1, 2, 3]), create_linked_list([4, 5, 6])],
            [None, create_linked_list([1]), None],
            [],
            [create_linked_list([5])],
        ]

        for lists in test_cases:
            heap_result = merge_k_sorted_lists([l for l in lists])
            dc_result = merge_k_sorted_lists_divide_conquer([l for l in lists])
            assert linked_list_to_list(heap_result) == linked_list_to_list(dc_result)

    def test_power_of_two_lists(self):
        """Test with power of two number of lists."""
        lists = [
            create_linked_list([1, 4]),
            create_linked_list([2, 5]),
            create_linked_list([3, 6]),
            create_linked_list([7, 8]),
        ]
        result = merge_k_sorted_lists_divide_conquer(lists)
        assert linked_list_to_list(result) == [1, 2, 3, 4, 5, 6, 7, 8]


class TestHelperFunctions:
    """Test helper functions."""

    def test_create_linked_list_empty(self):
        """Test creating empty linked list."""
        assert create_linked_list([]) is None

    def test_create_linked_list_single(self):
        """Test creating single element list."""
        node = create_linked_list([5])
        assert node.val == 5
        assert node.next is None

    def test_linked_list_to_list_empty(self):
        """Test converting empty linked list."""
        assert linked_list_to_list(None) == []

    def test_roundtrip(self):
        """Test create -> convert roundtrip."""
        original = [1, 2, 3, 4, 5]
        node = create_linked_list(original)
        result = linked_list_to_list(node)
        assert result == original


class TestListNode:
    """Test ListNode dataclass."""

    def test_list_node_creation(self):
        """Test ListNode creation."""
        node = ListNode(5)
        assert node.val == 5
        assert node.next is None

    def test_list_node_with_next(self):
        """Test ListNode with next pointer."""
        node1 = ListNode(1)
        node2 = ListNode(2, node1)
        assert node2.val == 2
        assert node2.next == node1
        assert node1.next is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
