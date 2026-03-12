"""
Tests for Merge k Sorted Lists solution.
"""

from __future__ import annotations

from merge_k_lists import (
    ListNode,
    merge_two_lists,
    merge_k_lists,
    create_linked_list,
    linked_list_to_list,
)


class TestMergeTwoLists:
    """Tests for merging two sorted lists."""

    def test_merge_two_empty(self):
        assert merge_two_lists(None, None) is None

    def test_merge_one_empty(self):
        l1 = create_linked_list([1, 2, 3])
        result = merge_two_lists(l1, None)
        assert linked_list_to_list(result) == [1, 2, 3]

    def test_merge_both_empty_one_element(self):
        l1 = create_linked_list([1])
        l2 = create_linked_list([2])
        result = merge_two_lists(l1, l2)
        assert linked_list_to_list(result) == [1, 2]

    def test_merge_interleaved(self):
        l1 = create_linked_list([1, 3, 5])
        l2 = create_linked_list([2, 4, 6])
        result = merge_two_lists(l1, l2)
        assert linked_list_to_list(result) == [1, 2, 3, 4, 5, 6]

    def test_merge_duplicates(self):
        l1 = create_linked_list([1, 2, 3])
        l2 = create_linked_list([2, 3, 4])
        result = merge_two_lists(l1, l2)
        assert linked_list_to_list(result) == [1, 2, 2, 3, 3, 4]


class TestMergeKLists:
    """Tests for merging k sorted lists."""

    def test_k_empty_lists(self):
        result = merge_k_lists([])
        assert result is None

    def test_k_single_empty_list(self):
        result = merge_k_lists([None])
        assert result is None

    def test_k_one_list(self):
        lists = [create_linked_list([1, 2, 3])]
        result = merge_k_lists(lists)
        assert linked_list_to_list(result) == [1, 2, 3]

    def test_k_two_lists(self):
        lists = [
            create_linked_list([1, 4, 7]),
            create_linked_list([2, 5, 8]),
        ]
        result = merge_k_lists(lists)
        assert linked_list_to_list(result) == [1, 2, 4, 5, 7, 8]

    def test_k_three_lists(self):
        lists = [
            create_linked_list([1, 3, 5]),
            create_linked_list([2, 4, 6]),
            create_linked_list([0, 7, 8]),
        ]
        result = merge_k_lists(lists)
        assert linked_list_to_list(result) == [0, 1, 2, 3, 4, 5, 6, 7, 8]

    def test_k_four_lists(self):
        lists = [
            create_linked_list([1, 3, 5]),
            create_linked_list([2, 4, 6]),
            create_linked_list([0, 7, 8]),
            create_linked_list([10, 11, 12]),
        ]
        result = merge_k_lists(lists)
        assert linked_list_to_list(result) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12]

    def test_k_lists_with_empty(self):
        lists = [
            create_linked_list([1, 4, 7]),
            None,
            create_linked_list([2, 5, 8]),
        ]
        result = merge_k_lists(lists)
        assert linked_list_to_list(result) == [1, 2, 4, 5, 7, 8]

    def test_duplicates_across_lists(self):
        lists = [
            create_linked_list([1, 1, 3]),
            create_linked_list([1, 1, 2]),
        ]
        result = merge_k_lists(lists)
        assert linked_list_to_list(result) == [1, 1, 1, 1, 2, 3]

    def test_single_element_in_each_list(self):
        lists = [
            create_linked_list([3]),
            create_linked_list([1]),
            create_linked_list([2]),
        ]
        result = merge_k_lists(lists)
        assert linked_list_to_list(result) == [1, 2, 3]

    def test_large_values(self):
        lists = [
            create_linked_list([1000, 2000]),
            create_linked_list([500, 1500]),
            create_linked_list([100, 3000]),
        ]
        result = merge_k_lists(lists)
        assert linked_list_to_list(result) == [100, 500, 1000, 1500, 2000, 3000]
