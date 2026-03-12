"""
Test cases for Median of Two Sorted Arrays solution.
"""
from __future__ import annotations

import pytest

from median_of_two_sorted_arrays import (
    find_median_sorted_arrays,
    find_median_sorted_arrays_simple,
)


class TestFindMedianSortedArrays:
    """Test cases for the binary search solution."""

    def test_example1(self):
        """Example 1: nums1 = [1,3], nums2 = [2] -> 2.0"""
        assert find_median_sorted_arrays([1, 3], [2]) == 2.0

    def test_example2(self):
        """Example 2: nums1 = [1,2], nums2 = [3,4] -> 2.5"""
        assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5

    def test_example3(self):
        """nums1 = [1], nums2 = [2, 3, 4] -> 2.5"""
        assert find_median_sorted_arrays([1], [2, 3, 4]) == 2.5

    def test_both_empty(self):
        """Both arrays empty -> should handle gracefully (but per constraints, min 1 total)"""
        # Edge case: both empty results in empty merged, but constraint says m+n >= 1
        # So we test with at least one non-empty
        pass

    def test_one_empty_array(self):
        """One array is empty - should return median of other."""
        assert find_median_sorted_arrays([], [1]) == 1.0
        assert find_median_sorted_arrays([1], []) == 1.0
        assert find_median_sorted_arrays([], [1, 2, 3, 4, 5]) == 3.0

    def test_single_element_both(self):
        """Both arrays have single element."""
        assert find_median_sorted_arrays([1], [2]) == 1.5

    def test_identical_elements(self):
        """Arrays with identical elements."""
        assert find_median_sorted_arrays([1, 1, 1], [1, 1, 1]) == 1.0

    def test_odd_total_elements(self):
        """Odd total number of elements."""
        assert find_median_sorted_arrays([1, 2, 3], [4, 5]) == 3.0
        assert find_median_sorted_arrays([1, 2], [3, 4, 5]) == 3.0

    def test_even_total_elements(self):
        """Even total number of elements."""
        assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5
        assert find_median_sorted_arrays([1, 2, 3], [4, 5, 6]) == 3.5

    def test_nums1_larger_than_nums2(self):
        """First array is larger than second."""
        assert find_median_sorted_arrays([1, 2, 3, 4, 5], [6, 7]) == 4.0

    def test_nums2_larger_than_nums1(self):
        """Second array is larger than first."""
        assert find_median_sorted_arrays([1, 2], [3, 4, 5, 6, 7]) == 4.0

    def test_negative_numbers(self):
        """Arrays with negative numbers."""
        # Merged: [-5, -3, -2, -1, 0, 2] -> median = (-2 + -1) / 2 = -1.5
        assert find_median_sorted_arrays([-5, -3, -1], [-2, 0, 2]) == -1.5

    def test_overlapping_ranges(self):
        """Arrays with overlapping value ranges."""
        assert find_median_sorted_arrays([1, 4, 5, 8, 10], [2, 3, 6, 7, 9]) == 5.5

    def test_large_gap(self):
        """Arrays with large gap between values."""
        # Merged: [1, 2, 3, 100, 200, 300] -> median = (3 + 100) / 2 = 51.5
        assert find_median_sorted_arrays([1, 2, 3], [100, 200, 300]) == 51.5

    def test_already_sorted_merged(self):
        """Arrays that would form a consecutive range when merged."""
        assert find_median_sorted_arrays([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], []) == 5.5


class TestFindMedianSortedArraysSimple:
    """Test cases for the simple merge solution."""

    def test_basic_cases(self):
        """Basic test cases comparing both implementations."""
        test_cases = [
            ([1, 3], [2], 2.0),
            ([1, 2], [3, 4], 2.5),
            ([1], [2, 3, 4], 2.5),
            ([], [1], 1.0),
            ([1, 2], [3, 4], 2.5),
            ([-5, -3, -1], [-2, 0, 2], -1.5),
        ]

        for nums1, nums2, expected in test_cases:
            result = find_median_sorted_arrays_simple(nums1, nums2)
            assert result == expected, f"Failed for {nums1}, {nums2}"


class TestConsistency:
    """Test that both implementations produce the same results."""

    @pytest.mark.parametrize(
        "nums1,nums2",
        [
            ([1, 3], [2]),
            ([1, 2], [3, 4]),
            ([1], [2, 3, 4]),
            ([], [1, 2, 3]),
            ([1, 2, 3], [4, 5]),
            ([1, 4, 5, 8, 10], [2, 3, 6, 7, 9]),
            ([-10, -5, 0], [0, 5, 10]),
            ([1, 1, 3, 3], [1, 1, 1, 1]),
        ],
    )
    def test_both_implementations_match(self, nums1, nums2):
        """Both implementations should produce identical results."""
        binary_search_result = find_median_sorted_arrays(nums1, nums2)
        simple_result = find_median_sorted_arrays_simple(nums1, nums2)
        assert binary_search_result == simple_result
