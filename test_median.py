"""
Test cases for Median of Two Sorted Arrays (LeetCode #4).
"""
from __future__ import annotations

import pytest

from median_of_two_sorted_arrays import (
    find_median_sorted_arrays,
    find_median_sorted_arrays_brute,
)


class TestFindMedianSortedArrays:
    """Test suite for the median of two sorted arrays solution."""

    def test_example1(self):
        """Example 1: nums1 = [1,3], nums2 = [2] -> 2.0"""
        result = find_median_sorted_arrays([1, 3], [2])
        assert result == 2.0

    def test_example2(self):
        """Example 2: nums1 = [1,2], nums2 = [3,4] -> 2.5"""
        result = find_median_sorted_arrays([1, 2], [3, 4])
        assert result == 2.5

    def test_single_element_both(self):
        """Both arrays have single elements."""
        assert find_median_sorted_arrays([1], [2]) == 1.5
        assert find_median_sorted_arrays([2], [1]) == 1.5

    def test_one_empty_array(self):
        """One array is empty."""
        assert find_median_sorted_arrays([], [1]) == 1.0
        assert find_median_sorted_arrays([1], []) == 1.0
        assert find_median_sorted_arrays([], [1, 2]) == 1.5
        assert find_median_sorted_arrays([1, 2], []) == 1.5

    def test_equal_length_odd(self):
        """Equal length arrays with odd total elements."""
        assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5

    def test_equal_length_even(self):
        """Equal length arrays with even total elements."""
        result = find_median_sorted_arrays([1, 1], [1, 1])
        assert result == 1.0

    def test_duplicate_values(self):
        """Arrays with duplicate values."""
        assert find_median_sorted_arrays([1, 1, 3, 3], [1, 1, 3, 3]) == 2.0
        assert find_median_sorted_arrays([1, 2, 2], [1, 2, 3]) == 2.0

    def test_negative_numbers(self):
        """Arrays with negative numbers."""
        assert find_median_sorted_arrays([-5, -3, -1], [-2, 0, 2]) == -1.5
        assert find_median_sorted_arrays([-10], [0]) == -5.0

    def test_large_gap_values(self):
        """Arrays with large gaps between values."""
        # merged = [1, 2, 500, 1000], median = (2 + 500) / 2 = 251.0
        assert find_median_sorted_arrays([1, 1000], [2, 500]) == 251.0

    def test_first_array_longer(self):
        """First array is longer than second."""
        result = find_median_sorted_arrays([1, 2, 3, 4, 5], [6, 7])
        assert result == 4.0

    def test_second_array_longer(self):
        """Second array is longer than first."""
        result = find_median_sorted_arrays([1, 2], [3, 4, 5, 6, 7])
        assert result == 4.0

    def test_large_numbers(self):
        """Large integer values."""
        result = find_median_sorted_arrays([10**9], [10**9])
        assert result == 10**9

    def test_very_different_sizes(self):
        """Arrays with very different sizes."""
        result = find_median_sorted_arrays([1], [2, 3, 4, 5, 6, 7, 8, 9, 10])
        assert result == 5.5


class TestFindMedianSortedArraysBrute:
    """Test suite for the brute force solution."""

    def test_agrees_with_binary_search(self):
        """Verify brute force matches binary search solution."""
        test_cases = [
            ([1, 3], [2]),
            ([1, 2], [3, 4]),
            ([], [1]),
            ([1], []),
            ([-5, -3, -1], [-2, 0, 2]),
            ([1, 1, 3, 3], [1, 1, 3, 3]),
            ([1, 2, 3, 4, 5], [6, 7]),
            ([1], [2, 3, 4, 5]),
        ]

        for nums1, nums2 in test_cases:
            binary_result = find_median_sorted_arrays(nums1, nums2)
            brute_result = find_median_sorted_arrays_brute(nums1, nums2)
            assert binary_result == brute_result, f"Failed for {nums1}, {nums2}"
