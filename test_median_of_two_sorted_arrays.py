"""Tests for Median of Two Sorted Arrays."""
from __future__ import annotations

from median_of_two_sorted_arrays import find_median_sorted_arrays


class TestFindMedianSortedArrays:
    """Test cases for the median of two sorted arrays solution."""

    def test_example1_odd_total(self) -> None:
        assert find_median_sorted_arrays([1, 3], [2]) == 2.0

    def test_example2_even_total(self) -> None:
        assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5

    def test_first_array_empty(self) -> None:
        assert find_median_sorted_arrays([], [1]) == 1.0

    def test_second_array_empty(self) -> None:
        assert find_median_sorted_arrays([2], []) == 2.0

    def test_single_elements(self) -> None:
        assert find_median_sorted_arrays([1], [2]) == 1.5

    def test_same_elements(self) -> None:
        assert find_median_sorted_arrays([1, 1], [1, 1]) == 1.0

    def test_non_overlapping_first_smaller(self) -> None:
        assert find_median_sorted_arrays([1, 2], [3, 4, 5]) == 3.0

    def test_non_overlapping_second_smaller(self) -> None:
        assert find_median_sorted_arrays([3, 4, 5], [1, 2]) == 3.0

    def test_negative_numbers(self) -> None:
        assert find_median_sorted_arrays([-5, -3, -1], [-2, 0, 2]) == -1.5

    def test_large_difference_in_sizes(self) -> None:
        assert find_median_sorted_arrays([1], [2, 3, 4, 5, 6, 7, 8]) == 4.5

    def test_larger_arrays(self) -> None:
        nums1 = list(range(1, 101, 2))   # [1,3,5,...,99] -- 50 elements
        nums2 = list(range(2, 102, 2))   # [2,4,6,...,100] -- 50 elements
        # merged = [1..100], median = (50+51)/2 = 50.5
        assert find_median_sorted_arrays(nums1, nums2) == 50.5

    def test_duplicates_across_arrays(self) -> None:
        assert find_median_sorted_arrays([1, 2, 2], [2, 3, 3]) == 2.0

    def test_single_element_each(self) -> None:
        assert find_median_sorted_arrays([100], [-100]) == 0.0
