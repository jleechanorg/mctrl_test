"""
Test cases for MedianFinder (LeetCode Problem 295)
"""

from __future__ import annotations
import pytest
from median_finder import MedianFinder


class TestMedianFinder:
    """Test suite for MedianFinder data structure."""

    def test_example_from_problem(self):
        """Test the exact example from LeetCode problem."""
        mf = MedianFinder()

        # Expected: [null, null, null, 1.5, null, 2.0]
        # Per LeetCode: findMedian will only be called after at least one number is added
        mf.addNum(1)
        mf.addNum(2)
        assert mf.findMedian() == 1.5

        mf.addNum(3)
        assert mf.findMedian() == 2.0

    def test_single_element(self):
        """Test median with single element."""
        mf = MedianFinder()
        mf.addNum(1)
        assert mf.findMedian() == 1.0

    def test_two_elements(self):
        """Test median with two elements."""
        mf = MedianFinder()
        mf.addNum(1)
        mf.addNum(2)
        assert mf.findMedian() == 1.5

    def test_three_elements_odd(self):
        """Test median with odd number of elements."""
        mf = MedianFinder()
        mf.addNum(1)
        mf.addNum(2)
        mf.addNum(3)
        assert mf.findMedian() == 2.0

    def test_four_elements_even(self):
        """Test median with even number of elements."""
        mf = MedianFinder()
        mf.addNum(1)
        mf.addNum(2)
        mf.addNum(3)
        mf.addNum(4)
        assert mf.findMedian() == 2.5

    def test_negative_numbers(self):
        """Test median with negative numbers."""
        mf = MedianFinder()
        mf.addNum(-1)
        mf.addNum(-2)
        mf.addNum(-3)
        assert mf.findMedian() == -2.0

    def test_mixed_positive_negative(self):
        """Test median with mix of positive and negative."""
        mf = MedianFinder()
        mf.addNum(-1)
        mf.addNum(0)
        mf.addNum(1)
        assert mf.findMedian() == 0.0

    def test_larger_dataset(self):
        """Test median with larger dataset."""
        mf = MedianFinder()
        for i in range(1, 101):
            mf.addNum(float(i))
        assert mf.findMedian() == 50.5

    def test_descending_order(self):
        """Test median when adding elements in descending order."""
        mf = MedianFinder()
        for i in range(10, 0, -1):
            mf.addNum(float(i))
        assert mf.findMedian() == 5.5

    def test_ascending_order(self):
        """Test median when adding elements in ascending order."""
        mf = MedianFinder()
        for i in range(1, 11):
            mf.addNum(float(i))
        assert mf.findMedian() == 5.5

    def test_duplicate_values(self):
        """Test median with duplicate values."""
        mf = MedianFinder()
        mf.addNum(1)
        mf.addNum(1)
        mf.addNum(1)
        mf.addNum(1)
        assert mf.findMedian() == 1.0

    def test_large_range(self):
        """Test with values at constraint boundaries."""
        mf = MedianFinder()
        mf.addNum(-100000)
        mf.addNum(100000)
        assert mf.findMedian() == 0.0

    def test_zero(self):
        """Test with zero."""
        mf = MedianFinder()
        mf.addNum(0)
        mf.addNum(-1)
        mf.addNum(1)
        assert mf.findMedian() == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
