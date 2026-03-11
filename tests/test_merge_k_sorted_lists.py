"""Tests for LeetCode #23 - Merge k Sorted Lists."""
from __future__ import annotations

from leetcode.merge_k_sorted_lists import ListNode, build_list, merge_k_lists, to_list


class TestMergeKSortedLists:
    def test_example_case(self) -> None:
        lists = [build_list([1, 4, 5]), build_list([1, 3, 4]), build_list([2, 6])]
        assert to_list(merge_k_lists(lists)) == [1, 1, 2, 3, 4, 4, 5, 6]

    def test_empty_input(self) -> None:
        assert merge_k_lists([]) is None

    def test_all_empty_lists(self) -> None:
        assert merge_k_lists([None, None, None]) is None

    def test_single_list(self) -> None:
        lists = [build_list([1, 2, 3])]
        assert to_list(merge_k_lists(lists)) == [1, 2, 3]

    def test_single_element_lists(self) -> None:
        lists = [build_list([5]), build_list([1]), build_list([3])]
        assert to_list(merge_k_lists(lists)) == [1, 3, 5]

    def test_mixed_empty_and_nonempty(self) -> None:
        lists = [None, build_list([1, 3]), None, build_list([2, 4])]
        assert to_list(merge_k_lists(lists)) == [1, 2, 3, 4]

    def test_duplicate_values(self) -> None:
        lists = [build_list([1, 1, 1]), build_list([1, 1])]
        assert to_list(merge_k_lists(lists)) == [1, 1, 1, 1, 1]

    def test_negative_values(self) -> None:
        lists = [build_list([-3, -1, 5]), build_list([-2, 0, 4])]
        assert to_list(merge_k_lists(lists)) == [-3, -2, -1, 0, 4, 5]

    def test_large_k(self) -> None:
        lists = [build_list([i]) for i in range(100, 0, -1)]
        result = to_list(merge_k_lists(lists))
        assert result == list(range(1, 101))

    def test_varying_lengths(self) -> None:
        lists = [build_list([1]), build_list([2, 3, 4, 5, 6]), build_list([3, 7])]
        assert to_list(merge_k_lists(lists)) == [1, 2, 3, 3, 4, 5, 6, 7]


class TestHelpers:
    def test_build_list_empty(self) -> None:
        assert build_list([]) is None

    def test_to_list_none(self) -> None:
        assert to_list(None) == []

    def test_roundtrip(self) -> None:
        values = [1, 2, 3, 4, 5]
        assert to_list(build_list(values)) == values
