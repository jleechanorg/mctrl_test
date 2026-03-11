"""
Tests for LeetCode 4 - Median of Two Sorted Arrays
"""

from __future__ import annotations

import pytest
from median_of_two_sorted_arrays import find_median_sorted_arrays


class TestMedianOfTwoSortedArrays:
    """Test cases for find_median_sorted_arrays."""

    def test_example1(self):
        assert find_median_sorted_arrays([1, 3], [2]) == 2.0

    def test_example2(self):
        assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5

    def test_first_array_larger(self):
        assert find_median_sorted_arrays([1, 2], [3]) == 2.0

    def test_second_array_larger(self):
        assert find_median_sorted_arrays([1, 3], [2, 4, 5]) == 3.0

    def test_both_single_elements(self):
        assert find_median_sorted_arrays([1], [2]) == 1.5

    def test_with_duplicates(self):
        assert find_median_sorted_arrays([1, 1, 2], [1, 2, 3]) == 1.5

    def test_empty_first_array(self):
        assert find_median_sorted_arrays([], [1]) == 1.0

    def test_empty_second_array(self):
        assert find_median_sorted_arrays([1], []) == 1.0

    def test_both_empty(self):
        assert find_median_sorted_arrays([], []) == 0.0

    def test_even_total_length(self):
        assert find_median_sorted_arrays([1, 2, 3, 4], [5, 6]) == 3.5

    def test_odd_total_length(self):
        assert find_median_sorted_arrays([1, 2, 3], [4, 5]) == 3.0

    def test_large_values(self):
        assert find_median_sorted_arrays([100000], [100001]) == 100000.5

    def test_negative_numbers(self):
        assert find_median_sorted_arrays([-5, -3, -1], [-4, -2, 0]) == -2.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
