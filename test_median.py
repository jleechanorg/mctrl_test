"""
Tests for Median of Two Sorted Arrays solution.
"""
import pytest
from median_of_two_arrays import find_median_sorted_arrays


class TestMedianOfTwoSortedArrays:
    """Test cases for the median of two sorted arrays problem."""

    def test_basic_case_1(self):
        """Test [1,3] and [2] -> 2.0"""
        result = find_median_sorted_arrays([1, 3], [2])
        assert result == 2.0

    def test_basic_case_2(self):
        """Test [1,2] and [3,4] -> 2.5"""
        result = find_median_sorted_arrays([1, 2], [3, 4])
        assert result == 2.5

    def test_empty_first_array(self):
        """Test [] and [1] -> 1.0"""
        result = find_median_sorted_arrays([], [1])
        assert result == 1.0

    def test_empty_second_array(self):
        """Test [1] and [] -> 1.0"""
        result = find_median_sorted_arrays([1], [])
        assert result == 1.0

    def test_single_element_both(self):
        """Test [1] and [2] -> 1.5"""
        result = find_median_sorted_arrays([1], [2])
        assert result == 1.5

    def test_identical_arrays(self):
        """Test [1,1,1] and [1,1,1] -> 1.0"""
        result = find_median_sorted_arrays([1, 1, 1], [1, 1, 1])
        assert result == 1.0

    def test_negative_numbers(self):
        """Test [-5, -3, -1] and [-2, 0, 2] -> -1.5"""
        result = find_median_sorted_arrays([-5, -3, -1], [-2, 0, 2])
        assert result == -1.5
