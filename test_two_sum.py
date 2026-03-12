"""
Unit tests for LeetCode #1 - Two Sum problem.
"""
from __future__ import annotations

import pytest
from two_sum import two_sum, two_sum_brute_force


class TestTwoSum:
    """Test suite for Two Sum solution."""

    def test_basic_case(self):
        """Test basic case: [2,7,11,15], target=9 -> [0,1]"""
        nums = [2, 7, 11, 15]
        target = 9
        result = two_sum(nums, target)
        assert sorted(result) == [0, 1]
        assert nums[result[0]] + nums[result[1]] == target

    def test_middle_elements(self):
        """Test case: [3,2,4], target=6 -> [1,2]"""
        nums = [3, 2, 4]
        target = 6
        result = two_sum(nums, target)
        assert sorted(result) == [1, 2]
        assert nums[result[0]] + nums[result[1]] == target

    def test_duplicate_values(self):
        """Test case: [3,3], target=6 -> [0,1]"""
        nums = [3, 3]
        target = 6
        result = two_sum(nums, target)
        assert sorted(result) == [0, 1]
        assert nums[result[0]] + nums[result[1]] == target

    def test_negative_numbers(self):
        """Test with negative numbers."""
        nums = [-1, -2, -3, -4, -5]
        target = -8
        result = two_sum(nums, target)
        assert nums[result[0]] + nums[result[1]] == target

    def test_brute_force_basic(self):
        """Test brute force solution basic case."""
        nums = [2, 7, 11, 15]
        target = 9
        result = two_sum_brute_force(nums, target)
        assert sorted(result) == [0, 1]
        assert nums[result[0]] + nums[result[1]] == target

    # Intentionally failing test - expects return in sorted order
    def test_return_sorted_indices(self):
        """
        Intentionally failing test: expects indices to be returned in ascending order.
        This test will fail because two_sum returns indices in the order they are found.
        """
        nums = [2, 7, 11, 15]  # Target 9: 2+7=9, indices [0,1]
        target = 9
        result = two_sum(nums, target)
        # This test expects [1, 0] but function returns [0, 1]
        # The function returns indices in the order they appear in the array
        # but this test expects the larger index first
        assert result[0] > result[1], f"Expected larger index first, got {result}"


class TestTwoSumEdgeCases:
    """Edge case tests for Two Sum."""

    def test_two_elements(self):
        """Test with exactly two elements."""
        nums = [1, 2]
        target = 3
        result = two_sum(nums, target)
        assert result == [0, 1]

    def test_large_numbers(self):
        """Test with large numbers."""
        nums = [1000000000, 500000000, 500000000]
        target = 1000000000
        result = two_sum(nums, target)
        assert nums[result[0]] + nums[result[1]] == target
