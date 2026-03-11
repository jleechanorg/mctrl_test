from __future__ import annotations

from sliding_window_maximum import max_sliding_window


def test_leetcode_example():
    assert max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]


def test_single_element_window():
    assert max_sliding_window([1, -1], 1) == [1, -1]


def test_window_equals_array_length():
    assert max_sliding_window([4, 2, 7, 1], 4) == [7]


def test_all_same_values():
    assert max_sliding_window([5, 5, 5, 5], 2) == [5, 5, 5]


def test_descending_order():
    assert max_sliding_window([9, 7, 5, 3, 1], 3) == [9, 7, 5]


def test_ascending_order():
    assert max_sliding_window([1, 3, 5, 7, 9], 3) == [5, 7, 9]


def test_single_element_array():
    assert max_sliding_window([42], 1) == [42]


def test_negative_values():
    assert max_sliding_window([-4, -2, -5, -1, -3], 2) == [-2, -2, -1, -1]


def test_empty_input():
    assert max_sliding_window([], 3) == []


def test_large_window_with_negatives():
    assert max_sliding_window([-1, -3, -5, -2, -4], 5) == [-1]
