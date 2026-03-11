from __future__ import annotations

import pytest

from median_of_two_sorted_arrays import find_median_sorted_arrays


# --- Basic / LeetCode examples ---

def test_example1():
    assert find_median_sorted_arrays([1, 3], [2]) == 2.0


def test_example2():
    assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5


# --- Edge cases: empty arrays ---

def test_first_array_empty():
    assert find_median_sorted_arrays([], [1]) == 1.0


def test_second_array_empty():
    assert find_median_sorted_arrays([2], []) == 2.0


def test_first_empty_even_length():
    assert find_median_sorted_arrays([], [1, 2, 3, 4]) == 2.5


# --- Single-element arrays ---

def test_single_elements():
    assert find_median_sorted_arrays([1], [2]) == 1.5


def test_single_and_multiple():
    assert find_median_sorted_arrays([3], [1, 2, 4, 5]) == 3.0


# --- Arrays of different lengths ---

def test_unequal_lengths():
    assert find_median_sorted_arrays([1, 2], [3, 4, 5, 6, 7]) == 4.0


# --- Negative numbers ---

def test_negative_numbers():
    assert find_median_sorted_arrays([-5, -3, -1], [-2, 0, 2]) == -1.5


# --- Duplicates ---

def test_all_same():
    assert find_median_sorted_arrays([1, 1, 1], [1, 1, 1]) == 1.0


def test_duplicates_across():
    assert find_median_sorted_arrays([1, 1, 3], [1, 1, 3]) == 1.0


# --- Non-overlapping ranges ---

def test_non_overlapping_left():
    assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5


def test_non_overlapping_right():
    assert find_median_sorted_arrays([3, 4], [1, 2]) == 2.5


# --- Large values ---

def test_large_values():
    assert find_median_sorted_arrays([10**9], [10**9]) == float(10**9)


# --- Odd vs even total length ---

def test_odd_total():
    assert find_median_sorted_arrays([1, 3, 5], [2, 4]) == 3.0


def test_even_total():
    assert find_median_sorted_arrays([1, 3], [2, 4]) == 2.5
