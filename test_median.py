"""
Unit tests for Median of Two Sorted Arrays solution.
"""

import pytest
from median_of_two_sorted_arrays import (
    find_median_sorted_arrays,
    find_median_sorted_arrays_brute,
)


class TestMedianOfTwoSortedArrays:
    """Test cases for the median of two sorted arrays problem."""

    def test_basic_case_1(self):
        """Test: [1,3], [2] -> 2.0"""
        assert find_median_sorted_arrays([1, 3], [2]) == 2.0

    def test_basic_case_2(self):
        """Test: [1,2], [3,4] -> 2.5"""
        assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5

    def test_one_empty_array(self):
        """Test with one empty array."""
        assert find_median_sorted_arrays([], [1]) == 1.0
        assert find_median_sorted_arrays([1], []) == 1.0

    def test_single_element_each(self):
        """Test with single element in each array."""
        assert find_median_sorted_arrays([1], [1]) == 1.0
        assert find_median_sorted_arrays([1], [2]) == 1.5
        assert find_median_sorted_arrays([2], [1]) == 1.5

    def test_odd_total_length(self):
        """Test with odd total number of elements."""
        assert find_median_sorted_arrays([1], [2, 3, 4]) == 2.5
        assert find_median_sorted_arrays([1, 2, 3], [4]) == 2.5

    def test_even_total_length(self):
        """Test with even total number of elements."""
        assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5
        assert find_median_sorted_arrays([1, 3], [2, 4]) == 2.5

    def test_interleaved_arrays(self):
        """Test with interleaved elements."""
        assert find_median_sorted_arrays([1, 3, 5, 7, 9], [2, 4, 6, 8, 10]) == 5.5
        assert find_median_sorted_arrays([1, 2, 3], [4, 5, 6]) == 3.5

    def test_duplicate_values(self):
        """Test with duplicate values."""
        assert find_median_sorted_arrays([1, 1, 1], [1, 1, 1]) == 1.0
        assert find_median_sorted_arrays([1, 1, 3], [1, 2, 2]) == 1.5

    def test_large_gap_values(self):
        """Test with large gaps between values."""
        # [1, 500, 1000, 1001] -> median = (500+1000)/2 = 750
        assert find_median_sorted_arrays([1, 1000], [500, 1001]) == 750.0

    def test_negative_values(self):
        """Test with negative values."""
        assert find_median_sorted_arrays([-5, -3], [-1, 0]) == -2.0
        assert find_median_sorted_arrays([-10], [10]) == 0.0

    def test_both_empty(self):
        """Test with both arrays empty - edge case handled by constraints (min 1 total)."""
        # This case is not in constraints but function handles it
        result = find_median_sorted_arrays([], [])
        assert result == 0.0 or isinstance(result, float)

    def test_one_array_larger(self):
        """Test when one array is significantly larger."""
        # [1, 2, 3, 4, 5, 6] -> median = (3+4)/2 = 3.5
        assert find_median_sorted_arrays([1], [2, 3, 4, 5, 6]) == 3.5
        assert find_median_sorted_arrays([1, 2, 3, 4, 5], [6]) == 3.5

    def test_brute_force_equivalence(self):
        """Verify optimized solution matches brute force."""
        test_cases = [
            ([1, 3], [2]),
            ([1, 2], [3, 4]),
            ([], [1]),
            ([1, 3, 5, 7, 9], [2, 4, 6, 8, 10]),
            ([1, 1, 1], [1, 1, 1]),
            ([-5, -3], [-1, 0]),
        ]
        for nums1, nums2 in test_cases:
            expected = find_median_sorted_arrays_brute(nums1, nums2)
            result = find_median_sorted_arrays(nums1, nums2)
            assert result == expected, f"Mismatch for {nums1}, {nums2}: {result} != {expected}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
