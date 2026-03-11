from __future__ import annotations

from merge_k_sorted_lists import ListNode, build_list, merge_k_lists, to_list


# ---------- LeetCode examples ----------

def test_example_1():
    lists = [build_list([1, 4, 5]), build_list([1, 3, 4]), build_list([2, 6])]
    assert to_list(merge_k_lists(lists)) == [1, 1, 2, 3, 4, 4, 5, 6]


def test_example_2_empty_input():
    assert merge_k_lists([]) is None


def test_example_3_single_empty_list():
    assert merge_k_lists([None]) is None


# ---------- edge cases ----------

def test_single_list():
    lists = [build_list([1, 2, 3])]
    assert to_list(merge_k_lists(lists)) == [1, 2, 3]


def test_all_empty_lists():
    assert merge_k_lists([None, None, None]) is None


def test_mix_of_empty_and_nonempty():
    lists = [None, build_list([1]), None, build_list([0])]
    assert to_list(merge_k_lists(lists)) == [0, 1]


def test_single_element_lists():
    lists = [build_list([5]), build_list([2]), build_list([8])]
    assert to_list(merge_k_lists(lists)) == [2, 5, 8]


def test_duplicate_values():
    lists = [build_list([1, 1, 1]), build_list([1, 1])]
    assert to_list(merge_k_lists(lists)) == [1, 1, 1, 1, 1]


def test_negative_values():
    lists = [build_list([-3, -1, 5]), build_list([-2, 0, 4])]
    assert to_list(merge_k_lists(lists)) == [-3, -2, -1, 0, 4, 5]


def test_large_k():
    lists = [build_list([i]) for i in range(100, 0, -1)]
    assert to_list(merge_k_lists(lists)) == list(range(1, 101))
