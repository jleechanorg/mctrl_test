from __future__ import annotations

import pytest

from median_two_sorted_arrays import find_median_sorted_arrays


class TestMedianTwoSortedArrays:
    """Tests for LeetCode #4 - Median of Two Sorted Arrays."""

    # --- LeetCode examples ---

    def test_example1(self) -> None:
        assert find_median_sorted_arrays([1, 3], [2]) == 2.0

    def test_example2(self) -> None:
        assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5

    # --- Edge cases ---

    def test_first_array_empty(self) -> None:
        assert find_median_sorted_arrays([], [1]) == 1.0

    def test_second_array_empty(self) -> None:
        assert find_median_sorted_arrays([2], []) == 2.0

    def test_both_single_element(self) -> None:
        assert find_median_sorted_arrays([1], [2]) == 1.5

    def test_single_element_total(self) -> None:
        assert find_median_sorted_arrays([], [5]) == 5.0

    # --- Odd vs even total length ---

    def test_odd_total(self) -> None:
        assert find_median_sorted_arrays([1, 2], [3, 4, 5]) == 3.0

    def test_even_total(self) -> None:
        assert find_median_sorted_arrays([1, 2, 3], [4, 5, 6]) == 3.5

    # --- Non-overlapping ranges ---

    def test_first_all_smaller(self) -> None:
        assert find_median_sorted_arrays([1, 2], [3, 4, 5, 6]) == 3.5

    def test_first_all_larger(self) -> None:
        assert find_median_sorted_arrays([5, 6], [1, 2, 3, 4]) == 3.5

    # --- Duplicates ---

    def test_all_same(self) -> None:
        assert find_median_sorted_arrays([2, 2, 2], [2, 2]) == 2.0

    def test_duplicates_across_arrays(self) -> None:
        assert find_median_sorted_arrays([1, 1, 3], [1, 1, 3]) == 1.0

    # --- Negative numbers ---

    def test_negative_numbers(self) -> None:
        assert find_median_sorted_arrays([-5, -3, -1], [0, 2, 4]) == -0.5

    # --- Large arrays (correctness check) ---

    def test_large_arrays(self) -> None:
        a = list(range(0, 1000, 2))   # 500 even numbers
        b = list(range(1, 1001, 2))   # 500 odd numbers
        # merged = 0..999, median = (499 + 500) / 2
        assert find_median_sorted_arrays(a, b) == 499.5

    # --- Asymmetric sizes ---

    def test_one_element_vs_many(self) -> None:
        assert find_median_sorted_arrays([5], [1, 2, 3, 4, 6, 7, 8]) == 4.5
