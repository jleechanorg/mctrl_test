import pytest
from merge_k_sorted_lists import (
    ListNode,
    merge_k_lists,
    list_to_linked,
)


class TestListNode:
    """Test ListNode class functionality."""

    def test_to_list_empty(self):
        node = ListNode(5)
        assert node.to_list() == [5]

    def test_to_list_multiple(self):
        head = list_to_linked([1, 2, 3, 4, 5])
        assert head.to_list() == [1, 2, 3, 4, 5]

    def test_equality_same(self):
        l1 = list_to_linked([1, 2, 3])
        l2 = list_to_linked([1, 2, 3])
        assert l1 == l2

    def test_equality_different(self):
        l1 = list_to_linked([1, 2, 3])
        l2 = list_to_linked([1, 2, 4])
        assert l1 != l2


class TestListToLinked:
    """Test list_to_linked helper function."""

    def test_empty_list(self):
        assert list_to_linked([]) is None

    def test_single_element(self):
        result = list_to_linked([1])
        assert result.val == 1
        assert result.next is None

    def test_multiple_elements(self):
        result = list_to_linked([1, 2, 3, 4, 5])
        assert result.to_list() == [1, 2, 3, 4, 5]


class TestMergeKSortedLists:
    """Test merge_k_lists function."""

    def test_empty_list_of_lists(self):
        result = merge_k_lists([])
        assert result is None

    def test_all_empty_lists(self):
        result = merge_k_lists([None, None, None])
        assert result is None

    def test_single_list(self):
        lists = [list_to_linked([1, 2, 3])]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3]

    def test_two_sorted_lists(self):
        lists = [
            list_to_linked([1, 4, 5]),
            list_to_linked([1, 3, 4]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 1, 3, 4, 4, 5]

    def test_three_sorted_lists(self):
        lists = [
            list_to_linked([1, 4, 7, 10]),
            list_to_linked([2, 5, 8]),
            list_to_linked([3, 6, 9]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_lists_with_duplicates(self):
        lists = [
            list_to_linked([1, 1, 1]),
            list_to_linked([1, 1]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 1, 1, 1, 1]

    def test_some_empty_lists(self):
        lists = [
            list_to_linked([1, 4, 5]),
            None,
            list_to_linked([2, 3, 6]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6]

    def test_single_element_lists(self):
        lists = [
            list_to_linked([1]),
            list_to_linked([2]),
            list_to_linked([3]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3]

    def test_already_sorted_single_list(self):
        lists = [list_to_linked([1, 2, 3, 4, 5])]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3, 4, 5]

    def test_reverse_order_input(self):
        lists = [
            list_to_linked([5, 6, 7]),
            list_to_linked([2, 3, 4]),
            list_to_linked([1]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3, 4, 5, 6, 7]

    def test_negative_numbers(self):
        lists = [
            list_to_linked([-3, -1, 2]),
            list_to_linked([-5, -2, 0, 1]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [-5, -3, -2, -1, 0, 1, 2]

    def test_large_gap_values(self):
        lists = [
            list_to_linked([1, 1000]),
            list_to_linked([500, 2000]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 500, 1000, 2000]

    def test_k_equals_one(self):
        lists = [list_to_linked([1, 2, 3])]
        result = merge_k_lists(lists)
        assert result.to_list() == [1, 2, 3]

    def test_interleaved_values(self):
        # Test with values that interleave across lists
        lists = [
            list_to_linked([1, 10, 20, 30]),
            list_to_linked([2, 11, 21, 31]),
            list_to_linked([3, 12, 22, 32]),
        ]
        result = merge_k_lists(lists)
        assert result.to_list() == [
            1, 2, 3, 10, 11, 12, 20, 21, 22, 30, 31, 32
        ]
