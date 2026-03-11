"""Tests for LeetCode #4 - Median of Two Sorted Arrays."""
from solutions.median_two_sorted_arrays import find_median_sorted_arrays


class TestMedianTwoSortedArrays:
    def test_example1(self) -> None:
        assert find_median_sorted_arrays([1, 3], [2]) == 2.0

    def test_example2(self) -> None:
        assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5

    def test_one_empty(self) -> None:
        assert find_median_sorted_arrays([], [1]) == 1.0

    def test_both_single(self) -> None:
        assert find_median_sorted_arrays([2], [1]) == 1.5

    def test_same_elements(self) -> None:
        assert find_median_sorted_arrays([1, 1], [1, 1]) == 1.0

    def test_large_arrays(self) -> None:
        a = list(range(0, 1000, 2))   # evens
        b = list(range(1, 1000, 2))   # odds
        assert find_median_sorted_arrays(a, b) == 499.5

    def test_negative_numbers(self) -> None:
        assert find_median_sorted_arrays([-5, -3, -1], [0, 2, 4]) == -0.5

    def test_first_empty(self) -> None:
        assert find_median_sorted_arrays([], [2, 3]) == 2.5

    def test_disjoint_ranges(self) -> None:
        assert find_median_sorted_arrays([1, 2], [3, 4, 5, 6]) == 3.5
