"""
Unit tests for Median of Two Sorted Arrays solution.
"""
from __future__ import annotations

import math

import pytest

from median_of_two_sorted_arrays import (
    find_median_sorted_arrays,
    find_median_sorted_arrays_brute,
)


class TestFindMedianSortedArrays:
    """Test cases for the median of two sorted arrays solution."""

    # Basic examples from LeetCode
    def test_example1(self):
        assert find_median_sorted_arrays([1, 3], [2]) == 2.0

    def test_example2(self):
        result = find_median_sorted_arrays([1, 2], [3, 4])
        assert math.isclose(result, 2.5)

    # Edge cases with empty arrays
    def test_first_array_empty(self):
        assert find_median_sorted_arrays([], [1]) == 1.0

    def test_second_array_empty(self):
        assert find_median_sorted_arrays([1], []) == 1.0

    def test_both_arrays_empty(self):
        # Constraint says m + n >= 1, so this is technically invalid input
        # The function returns 0.0 for this edge case (not meaningful)
        result = find_median_sorted_arrays([], [])
        assert isinstance(result, float)

    def test_first_array_empty_even_merged(self):
        assert find_median_sorted_arrays([], [2, 3]) == 2.5

    # Single element arrays
    def test_single_element_both(self):
        assert find_median_sorted_arrays([1], [2]) == 1.5

    def test_single_element_first(self):
        assert find_median_sorted_arrays([1], [2, 3]) == 2.0

    def test_single_element_second(self):
        assert find_median_sorted_arrays([2, 3], [1]) == 2.0

    # Odd total length (median is single element)
    def test_odd_total_three_elements(self):
        assert find_median_sorted_arrays([1], [2, 3]) == 2.0

    def test_odd_total_five_elements(self):
        result = find_median_sorted_arrays([1, 2], [3, 4, 5])
        assert result == 3.0

    # Even total length (median is average)
    def test_even_total_four_elements(self):
        result = find_median_sorted_arrays([1, 2], [3, 4])
        assert math.isclose(result, 2.5)

    def test_even_total_six_elements(self):
        result = find_median_sorted_arrays([1, 2, 3], [4, 5, 6])
        assert math.isclose(result, 3.5)

    # Overlapping ranges
    def test_overlapping_ranges(self):
        result = find_median_sorted_arrays([1, 4, 7, 10], [2, 5, 6, 8])
        assert result == 5.5

    # Duplicate values
    def test_with_duplicates(self):
        result = find_median_sorted_arrays([1, 1], [1, 2])
        assert result == 1.0

    def test_all_duplicates(self):
        result = find_median_sorted_arrays([1, 1, 1], [1, 1])
        assert result == 1.0

    def test_duplicates_even_total(self):
        result = find_median_sorted_arrays([1, 2, 2], [2, 3, 3])
        assert result == 2.0

    # Negative numbers (merged: [-5, -3, -2, -1, 0, 2], median of 6 = avg of positions 2,3)
    def test_negative_numbers(self):
        result = find_median_sorted_arrays([-5, -3, -1], [-2, 0, 2])
        assert result == -1.5

    def test_all_negative(self):
        result = find_median_sorted_arrays([-10, -5, 0], [-3, -2, -1])
        assert math.isclose(result, -2.5)

    # Large numbers
    def test_large_numbers(self):
        result = find_median_sorted_arrays([1000000], [500000])
        assert result == 750000.0

    # First array larger than second
    def test_first_larger_than_second(self):
        result = find_median_sorted_arrays([1, 2, 3, 4, 5], [6])
        assert result == 3.5

    # Second array larger than first
    def test_second_larger_than_first(self):
        result = find_median_sorted_arrays([1], [2, 3, 4, 5, 6])
        assert result == 3.5

    # Compare with brute force solution
    def test_equivalence_with_brute_force(self):
        test_cases = [
            ([1, 3], [2]),
            ([1, 2], [3, 4]),
            ([], [1]),
            ([1], []),
            ([1, 2], [3]),
            ([1], [2, 3]),
            ([1, 1, 1], [1, 1, 1]),
            ([-5, -3, -1], [-2, 0, 2]),
            ([1000000], [500000]),
        ]

        for nums1, nums2 in test_cases:
            if len(nums1) + len(nums2) == 0:
                continue
            expected = find_median_sorted_arrays_brute(nums1, nums2)
            result = find_median_sorted_arrays(nums1, nums2)
            assert math.isclose(
                result, expected, rel_tol=1e-9
            ), f"Failed for {nums1}, {nums2}: expected {expected}, got {result}"


class TestFindMedianSortedArraysBrute:
    """Test cases for the brute force solution."""

    def test_basic_cases(self):
        assert find_median_sorted_arrays_brute([1, 3], [2]) == 2.0
        assert find_median_sorted_arrays_brute([1, 2], [3, 4]) == 2.5

    def test_empty_first(self):
        assert find_median_sorted_arrays_brute([], [1]) == 1.0

    def test_empty_second(self):
        assert find_median_sorted_arrays_brute([1], []) == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
