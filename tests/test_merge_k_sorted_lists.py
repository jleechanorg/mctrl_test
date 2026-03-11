"""Tests for LeetCode #23 - Merge k Sorted Lists."""
from solutions.merge_k_sorted_lists import (
    list_to_linked,
    linked_to_list,
    merge_k_lists,
)


class TestMergeKSortedLists:
    def test_example1(self) -> None:
        lists = [
            list_to_linked([1, 4, 5]),
            list_to_linked([1, 3, 4]),
            list_to_linked([2, 6]),
        ]
        assert linked_to_list(merge_k_lists(lists)) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_input(self) -> None:
        assert merge_k_lists([]) is None

    def test_all_empty_lists(self) -> None:
        assert merge_k_lists([None, None]) is None

    def test_single_list(self) -> None:
        lists = [list_to_linked([1, 2, 3])]
        assert linked_to_list(merge_k_lists(lists)) == [1, 2, 3]

    def test_single_element_lists(self) -> None:
        lists = [list_to_linked([5]), list_to_linked([1]), list_to_linked([3])]
        assert linked_to_list(merge_k_lists(lists)) == [1, 3, 5]

    def test_negative_values(self) -> None:
        lists = [
            list_to_linked([-3, -1, 2]),
            list_to_linked([-2, 0, 4]),
        ]
        assert linked_to_list(merge_k_lists(lists)) == [-3, -2, -1, 0, 2, 4]

    def test_duplicate_values(self) -> None:
        lists = [
            list_to_linked([1, 1, 1]),
            list_to_linked([1, 1]),
        ]
        assert linked_to_list(merge_k_lists(lists)) == [1, 1, 1, 1, 1]

    def test_mixed_empty_and_nonempty(self) -> None:
        lists = [None, list_to_linked([1, 2]), None, list_to_linked([3])]
        assert linked_to_list(merge_k_lists(lists)) == [1, 2, 3]
