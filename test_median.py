"""
Test cases for Median of Two Sorted Arrays solution.
"""
from __future__ import annotations

import pytest

from median_of_two_sorted_arrays import find_median_sorted_arrays


class TestFindMedianSortedArrays:
    """Test cases for the median of two sorted arrays problem."""

    def test_example1(self):
        """Example 1: nums1 = [1,3], nums2 = [2]"""
        result = find_median_sorted_arrays([1, 3], [2])
        assert result == 2.0

    def test_example2(self):
        """Example 2: nums1 = [1,2], nums2 = [3,4]"""
        result = find_median_sorted_arrays([1, 2], [3, 4])
        assert result == 2.5

    def test_one_empty_array(self):
        """One array is empty"""
        assert find_median_sorted_arrays([], [1]) == 1.0
        assert find_median_sorted_arrays([1], []) == 1.0
        assert find_median_sorted_arrays([], [1, 2, 3]) == 2.0

    def test_single_element_both(self):
        """Both arrays have single elements"""
        assert find_median_sorted_arrays([1], [2]) == 1.5

    def test_even_total_length(self):
        """Even total number of elements"""
        assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5
        assert find_median_sorted_arrays([1, 3], [2, 4]) == 2.5

    def test_odd_total_length(self):
        """Odd total number of elements"""
        assert find_median_sorted_arrays([1], [2, 3]) == 2.0
        assert find_median_sorted_arrays([1, 2, 3], [4]) == 2.5  # 3+1=4 even
        assert find_median_sorted_arrays([1, 2], [3]) == 2.0

    def test_overlapping_values(self):
        """Arrays with overlapping values"""
        assert find_median_sorted_arrays([1, 1], [1, 1]) == 1.0
        assert find_median_sorted_arrays([1, 2, 3], [2, 3, 4]) == 2.5

    def test_first_array_longer(self):
        """First array is longer"""
        assert find_median_sorted_arrays([1, 2, 3], [4, 5]) == 3.0

    def test_second_array_longer(self):
        """Second array is longer"""
        assert find_median_sorted_arrays([4, 5], [1, 2, 3]) == 3.0

    def test_negative_numbers(self):
        """Arrays with negative numbers"""
        assert find_median_sorted_arrays([-5, -3], [-2, -1]) == -2.5
        assert find_median_sorted_arrays([-10, 0], [0, 10]) == 0.0

    def test_large_gap_values(self):
        """Arrays with large gap between values"""
        assert find_median_sorted_arrays([1, 1000], [2, 3]) == 2.5
        assert find_median_sorted_arrays([1], [1000]) == 500.5

    def test_duplicate_values(self):
        """Arrays with many duplicate values"""
        assert find_median_sorted_arrays([1, 1, 1], [1, 1]) == 1.0
        assert find_median_sorted_arrays([1, 2, 2], [2, 2, 2]) == 2.0

    def test_very_different_lengths(self):
        """Arrays with very different lengths"""
        assert find_median_sorted_arrays([1], [1, 2, 3, 4]) == 2.0
        # [1, 2, 3, 4] + [5] = [1, 2, 3, 4, 5], median = 3.0
        assert find_median_sorted_arrays([1, 2, 3, 4], [5]) == 3.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
