"""
Tests for LeetCode #239 - Sliding Window Maximum
"""
from __future__ import annotations

import pytest
from sliding_window_maximum import max_sliding_window


class TestSlidingWindowMaximum:
    """Test cases for max_sliding_window function."""

    def test_example_1(self):
        """Example 1 from LeetCode."""
        nums = [1, 3, -1, -3, 5, 3, 6, 7]
        k = 3
        expected = [3, 3, 5, 5, 6, 7]
        assert max_sliding_window(nums, k) == expected

    def test_example_2(self):
        """Example 2 from LeetCode - single element."""
        nums = [1]
        k = 1
        expected = [1]
        assert max_sliding_window(nums, k) == expected

    def test_single_element_window_equal_to_array_length(self):
        """When k equals array length, result is single maximum."""
        nums = [4, 2, 12, 3]
        k = 4
        expected = [12]
        assert max_sliding_window(nums, k) == expected

    def test_window_size_1(self):
        """Window size of 1 returns the array itself."""
        nums = [1, 2, 3, 4, 5]
        k = 1
        expected = [1, 2, 3, 4, 5]
        assert max_sliding_window(nums, k) == expected

    def test_all_same_elements(self):
        """All elements identical."""
        nums = [5, 5, 5, 5, 5]
        k = 2
        expected = [5, 5, 5, 5]
        assert max_sliding_window(nums, k) == expected

    def test_decreasing_array(self):
        """Strictly decreasing array - each window max is first element."""
        nums = [5, 4, 3, 2, 1]
        k = 3
        expected = [5, 4, 3]
        assert max_sliding_window(nums, k) == expected

    def test_increasing_array(self):
        """Strictly increasing array - each window max is last element."""
        nums = [1, 2, 3, 4, 5]
        k = 3
        expected = [3, 4, 5]
        assert max_sliding_window(nums, k) == expected

    def test_negative_numbers(self):
        """Array with negative numbers."""
        nums = [-1, -3, -2, -5, -1]
        k = 2
        expected = [-1, -2, -2, -1]
        assert max_sliding_window(nums, k) == expected

    def test_mixed_positive_negative(self):
        """Mix of positive and negative numbers."""
        nums = [1, -2, 5, 3, -1, 2, -4, 0]
        k = 3
        # Windows: [1,-2,5]=5, [-2,5,3]=5, [5,3,-1]=5, [3,-1,2]=3, [-1,2,-4]=2,,0]=2 [2,-4
        expected = [5, 5, 5, 3, 2, 2]
        assert max_sliding_window(nums, k) == expected

    def test_window_size_2(self):
        """Window size of 2."""
        nums = [1, 3, 2, 6, 4]
        k = 2
        expected = [3, 3, 6, 6]
        assert max_sliding_window(nums, k) == expected

    def test_large_k(self):
        """Large k value near array length."""
        nums = [1, 2, 3, 4, 5]
        k = 4
        expected = [4, 5]
        assert max_sliding_window(nums, k) == expected

    def test_two_elements_k_two(self):
        """Minimum valid input with k=2."""
        nums = [1, 2]
        k = 2
        expected = [2]
        assert max_sliding_window(nums, k) == expected

    def test_returns_list_type(self):
        """Verify return type is list."""
        nums = [1, 2, 3]
        k = 2
        result = max_sliding_window(nums, k)
        assert isinstance(result, list)
        assert all(isinstance(x, int) for x in result)


class TestSlidingWindowMaximumEdgeCases:
    """Edge case tests."""

    def test_empty_array(self):
        """Empty array."""
        nums = []
        k = 1
        expected = []
        assert max_sliding_window(nums, k) == expected

    def test_k_zero(self):
        """Window size zero returns empty."""
        nums = [1, 2, 3]
        k = 0
        expected = []
        assert max_sliding_window(nums, k) == expected

    def test_large_array(self):
        """Large array for performance testing."""
        nums = list(range(10000))
        k = 100
        result = max_sliding_window(nums, k)
        # Last element should be the max in last window
        assert result[-1] == 9999
        # Length should be n - k + 1
        assert len(result) == 10000 - 100 + 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
