"""Tests for LeetCode #4: Median of Two Sorted Arrays."""
from __future__ import annotations

import pytest

from leetcode.median_two_sorted_arrays import find_median_sorted_arrays


class TestMedianTwoSortedArrays:
    """Core correctness tests."""

    def test_example1(self) -> None:
        assert find_median_sorted_arrays([1, 3], [2]) == 2.0

    def test_example2(self) -> None:
        assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5

    def test_both_empty_raises(self) -> None:
        # Two empty arrays have no median; binary search never finds partition.
        with pytest.raises(ValueError):
            find_median_sorted_arrays([], [])

    def test_one_empty(self) -> None:
        assert find_median_sorted_arrays([], [1]) == 1.0
        assert find_median_sorted_arrays([2], []) == 2.0

    def test_one_empty_even(self) -> None:
        assert find_median_sorted_arrays([], [1, 2, 3, 4]) == 2.5

    def test_single_elements(self) -> None:
        assert find_median_sorted_arrays([1], [2]) == 1.5

    def test_disjoint_arrays(self) -> None:
        assert find_median_sorted_arrays([1, 2], [3, 4, 5, 6]) == 3.5

    def test_interleaved(self) -> None:
        assert find_median_sorted_arrays([1, 3, 5], [2, 4, 6]) == 3.5

    def test_duplicates(self) -> None:
        assert find_median_sorted_arrays([1, 1, 1], [1, 1, 1]) == 1.0

    def test_negatives(self) -> None:
        assert find_median_sorted_arrays([-5, -3, -1], [0, 2, 4]) == -0.5

    def test_large_difference_in_size(self) -> None:
        assert find_median_sorted_arrays([1], [2, 3, 4, 5, 6, 7, 8]) == 4.5

    def test_same_elements_odd_total(self) -> None:
        assert find_median_sorted_arrays([3, 3], [3]) == 3.0

    def test_longer_arrays(self) -> None:
        a = list(range(0, 100, 2))   # [0,2,4,...,98]  50 elements
        b = list(range(1, 100, 2))   # [1,3,5,...,99]  50 elements
        assert find_median_sorted_arrays(a, b) == 49.5
