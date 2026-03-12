"""
Unit tests for LeetCode 41 - First Missing Positive
"""

import pytest
from first_missing_positive import first_missing_positive


class TestFirstMissingPositive:
    """Test cases for first_missing_positive function."""

    def test_basic_cases(self):
        """Test basic cases from problem description."""
        assert first_missing_positive([1, 2, 0]) == 3
        assert first_missing_positive([3, 4, -1, 1]) == 2
        assert first_missing_positive([7, 8, 9, 11, 12]) == 1

    def test_duplicates(self):
        """Test handling of duplicate values."""
        assert first_missing_positive([1, 1, 0, -1, 2]) == 3

    def test_empty_list(self):
        """Test empty list returns 1."""
        assert first_missing_positive([]) == 1

    def test_single_element(self):
        """Test single element cases."""
        assert first_missing_positive([1]) == 2
        assert first_missing_positive([2]) == 1
        assert first_missing_positive([0]) == 1

    def test_already_complete(self):
        """Test when array contains 1 to n consecutively."""
        assert first_missing_positive([1, 2, 3, 4, 5]) == 6
        assert first_missing_positive([1, 2, 3]) == 4

    def test_reverse_order(self):
        """Test reverse sorted array."""
        assert first_missing_positive([5, 4, 3, 2, 1]) == 6

    def test_all_negative(self):
        """Test array with all negative numbers."""
        assert first_missing_positive([-1, -2, -3]) == 1

    def test_large_gap(self):
        """Test array with large gap in values."""
        assert first_missing_positive([1, 100, 200]) == 2
        assert first_missing_positive([2, 100, 200]) == 1
