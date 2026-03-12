"""
Tests for Merge k Sorted Lists solution.

Comprehensive test suite covering:
- Basic merging of multiple sorted lists
- Edge cases: empty input, single list, lists with single element
- Lists with negative numbers
- Large inputs
- Verifies both heap-based and divide-and-conquer approaches
"""

import pytest
from merge_k_sorted_lists import (
    merge_k_lists_heap,
    merge_k_lists_linkedlists,
    merge_k_lists_divide_conquer,
    ListNode,
    Solution,
)


class TestListNode:
    """Tests for ListNode helper class."""

    def test_from_list_empty(self):
        assert ListNode.from_list([]) is None

    def test_from_list_single(self):
        node = ListNode.from_list([1])
        assert node.val == 1
        assert node.next is None

    def test_from_list_multiple(self):
        node = ListNode.from_list([1, 2, 3])
        assert node.val == 1
        assert node.next.val == 2
        assert node.next.next.val == 3

    def test_to_list_empty(self):
        # Empty list returns None, not a ListNode
        assert ListNode.from_list([]) is None

    def test_to_list_roundtrip(self):
        original = [1, 4, 5, 8, 9]
        node = ListNode.from_list(original)
        assert node.to_list() == original


class TestMergeKListsHeap:
    """Tests for heap-based array merging."""

    def test_basic_merge(self):
        arrays = [[1, 4, 5], [1, 3, 4], [2, 6]]
        expected = [1, 1, 2, 3, 4, 4, 5, 6]
        assert merge_k_lists_heap(arrays) == expected

    def test_empty_input(self):
        assert merge_k_lists_heap([]) == []

    def test_single_list(self):
        arrays = [[1, 2, 3]]
        assert merge_k_lists_heap(arrays) == [1, 2, 3]

    def test_with_empty_lists(self):
        arrays = [[1, 2], [], [3, 4]]
        expected = [1, 2, 3, 4]
        assert merge_k_lists_heap(arrays) == expected

    def test_negative_numbers(self):
        arrays = [[-3, -1, 0], [-5, -2, 4]]
        expected = [-5, -3, -2, -1, 0, 4]
        assert merge_k_lists_heap(arrays) == expected

    def test_single_element_lists(self):
        arrays = [[3], [1], [2]]
        expected = [1, 2, 3]
        assert merge_k_lists_heap(arrays) == expected


class TestMergeKListsLinkedLists:
    """Tests for heap-based linked list merging."""

    def test_basic_merge(self):
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6])
        ]
        expected = [1, 1, 2, 3, 4, 4, 5, 6]
        result = merge_k_lists_linkedlists(lists)
        assert result.to_list() == expected

    def test_empty_input(self):
        assert merge_k_lists_linkedlists([]) is None

    def test_single_list(self):
        lists = [ListNode.from_list([1, 2, 3])]
        expected = [1, 2, 3]
        result = merge_k_lists_linkedlists(lists)
        assert result.to_list() == expected

    def test_with_none_in_list(self):
        # First list is empty (None), second has values
        lists = [None, ListNode.from_list([1, 2])]
        expected = [1, 2]
        result = merge_k_lists_linkedlists(lists)
        assert result.to_list() == expected

    def test_all_empty(self):
        lists = [None, None]
        assert merge_k_lists_linkedlists(lists) is None

    def test_negative_numbers(self):
        lists = [
            ListNode.from_list([-3, -1, 0]),
            ListNode.from_list([-5, -2, 4])
        ]
        expected = [-5, -3, -2, -1, 0, 4]
        result = merge_k_lists_linkedlists(lists)
        assert result.to_list() == expected

    def test_duplicates(self):
        lists = [
            ListNode.from_list([1, 1, 1]),
            ListNode.from_list([1, 1]),
        ]
        expected = [1, 1, 1, 1, 1]
        result = merge_k_lists_linkedlists(lists)
        assert result.to_list() == expected


class TestMergeKListsDivideConquer:
    """Tests for divide-and-conquer linked list merging."""

    def test_basic_merge(self):
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6])
        ]
        expected = [1, 1, 2, 3, 4, 4, 5, 6]
        result = merge_k_lists_divide_conquer(lists)
        assert result.to_list() == expected

    def test_empty_input(self):
        assert merge_k_lists_divide_conquer([]) is None

    def test_single_list(self):
        lists = [ListNode.from_list([1, 2, 3])]
        expected = [1, 2, 3]
        result = merge_k_lists_divide_conquer(lists)
        assert result.to_list() == expected

    def test_odd_number_of_lists(self):
        lists = [
            ListNode.from_list([1, 5]),
            ListNode.from_list([2, 4]),
            ListNode.from_list([3, 6])
        ]
        expected = [1, 2, 3, 4, 5, 6]
        result = merge_k_lists_divide_conquer(lists)
        assert result.to_list() == expected


class TestSolutionClass:
    """Tests for the LeetCode Solution class."""

    def test_leetcode_format(self):
        """Test using the exact LeetCode input format."""
        lists = [
            ListNode.from_list([1, 4, 5]),
            ListNode.from_list([1, 3, 4]),
            ListNode.from_list([2, 6])
        ]
        solution = Solution()
        result = solution.mergeKLists(lists)
        expected = [1, 1, 2, 3, 4, 4, 5, 6]
        assert result.to_list() == expected

    def test_leetcode_empty(self):
        solution = Solution()
        assert solution.mergeKLists([]) is None


class TestEdgeCases:
    """Additional edge case tests."""

    def test_large_values(self):
        arrays = [[10000], [9999], [-10000]]
        expected = [-10000, 9999, 10000]
        assert merge_k_lists_heap(arrays) == expected

    def test_already_sorted(self):
        arrays = [[1], [2], [3], [4]]
        expected = [1, 2, 3, 4]
        assert merge_k_lists_heap(arrays) == expected

    def test_already_merged_input(self):
        # All elements in one list, others empty
        arrays = [[1, 2, 3, 4, 5, 6], [], []]
        expected = [1, 2, 3, 4, 5, 6]
        assert merge_k_lists_heap(arrays) == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
