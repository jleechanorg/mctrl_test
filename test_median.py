"""
Tests for LeetCode #4: Median of Two Sorted Arrays
"""
from __future__ import annotations

import math
import pytest

from median_of_two_sorted_arrays import find_median_sorted_arrays


def float_equals(a: float, b: float, tolerance: float = 1e-5) -> bool:
    """Compare floats with tolerance for floating point precision."""
    return abs(a - b) < tolerance


class TestMedianOfTwoSortedArrays:
    """Test cases for median of two sorted arrays."""

    def test_example_1(self):
        """Example 1: [1,3], [2] -> 2.0"""
        result = find_median_sorted_arrays([1, 3], [2])
        assert float_equals(result, 2.0)

    def test_example_2(self):
        """Example 2: [1,2], [3,4] -> 2.5"""
        result = find_median_sorted_arrays([1, 2], [3, 4])
        assert float_equals(result, 2.5)

    def test_odd_total_length(self):
        """Test with odd total merged length."""
        result = find_median_sorted_arrays([1, 2], [3])
        assert float_equals(result, 2.0)

    def test_empty_first_array(self):
        """Test with empty first array."""
        result = find_median_sorted_arrays([], [1])
        assert float_equals(result, 1.0)

    def test_empty_second_array(self):
        """Test with empty second array."""
        result = find_median_sorted_arrays([2], [])
        assert float_equals(result, 2.0)

    def test_very_small_first(self):
        """Test with single element in first array."""
        result = find_median_sorted_arrays([1], [2, 3, 4])
        assert float_equals(result, 2.5)

    def test_single_element_each(self):
        """Test with single element in each array."""
        result = find_median_sorted_arrays([1], [2])
        assert float_equals(result, 1.5)

    def test_larger_first_array(self):
        """Test when first array is larger."""
        result = find_median_sorted_arrays([1, 2, 3], [4, 5])
        assert float_equals(result, 3.0)

    def test_larger_second_array(self):
        """Test when second array is larger."""
        result = find_median_sorted_arrays([1, 2], [3, 4, 5])
        assert float_equals(result, 3.0)

    def test_overlapping_values(self):
        """Test with overlapping values."""
        result = find_median_sorted_arrays([1, 1, 3], [1, 2])
        assert float_equals(result, 1.0)

    def test_negative_numbers(self):
        """Test with negative numbers."""
        result = find_median_sorted_arrays([-5, -3, -1], [-4, -2, 0])
        assert float_equals(result, -2.5)

    def test_large_gap_values(self):
        """Test with large gap between arrays."""
        # [1, 2, 100, 200] -> median = (2+100)/2 = 51.0
        result = find_median_sorted_arrays([1, 2], [100, 200])
        assert float_equals(result, 51.0)

    def test_duplicates(self):
        """Test with duplicate values."""
        result = find_median_sorted_arrays([1, 1, 1], [1, 1])
        assert float_equals(result, 1.0)

    def test_unbalanced_odd(self):
        """Test unbalanced arrays with odd total."""
        # [1, 2, 3, 4, 5, 6] -> 6 elements, median = (3+4)/2 = 3.5
        result = find_median_sorted_arrays([1], [2, 3, 4, 5, 6])
        assert float_equals(result, 3.5)

    def test_unbalanced_even(self):
        """Test unbalanced arrays with even total."""
        result = find_median_sorted_arrays([1, 2], [3, 4, 5, 6, 7])
        assert float_equals(result, 4.0)

    def test_alternating_elements(self):
        """Test with alternating elements from each array."""
        result = find_median_sorted_arrays([1, 3, 5], [2, 4, 6])
        assert float_equals(result, 3.5)

    def test_returns_float(self):
        """Test that result is always a float."""
        result = find_median_sorted_arrays([1], [2])
        assert isinstance(result, float)
