"""
Test cases for Median of Two Sorted Arrays (LeetCode #4)
"""
from __future__ import annotations

import pytest

from median_of_two_sorted_arrays import (
    find_median_sorted_arrays,
    find_median_sorted_arrays_naive,
)


class TestFindMedianSortedArrays:
    """Test cases for find_median_sorted_arrays function."""

    # Basic examples from problem statement
    def test_example1(self):
        assert find_median_sorted_arrays([1, 3], [2]) == 2.0

    def test_example2(self):
        assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5

    # Edge cases
    def test_single_element_arrays(self):
        assert find_median_sorted_arrays([1], [2]) == 1.5

    def test_one_empty_array(self):
        assert find_median_sorted_arrays([], [1]) == 1.0

    def test_both_single_elements(self):
        assert find_median_sorted_arrays([1], [2]) == 1.5

    # Odd total length cases
    def test_odd_total_three_elements(self):
        assert find_median_sorted_arrays([1], [2, 3]) == 2.0

    def test_odd_total_five_elements(self):
        assert find_median_sorted_arrays([1, 2], [3, 4, 5]) == 3.0

    def test_odd_total_seven_elements(self):
        assert find_median_sorted_arrays([1, 2, 3], [4, 5, 6, 7]) == 4.0

    # Even total length cases
    def test_even_total_four_elements(self):
        assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5

    def test_even_total_six_elements(self):
        assert find_median_sorted_arrays([1, 2, 3], [4, 5, 6]) == 3.5

    def test_even_total_eight_elements(self):
        assert find_median_sorted_arrays([1, 2, 3, 4], [5, 6, 7, 8]) == 4.5

    # Duplicate values
    def test_with_duplicates_odd(self):
        assert find_median_sorted_arrays([1, 1], [1, 2]) == 1.0

    def test_with_duplicates_even(self):
        assert find_median_sorted_arrays([1, 1], [1, 1]) == 1.0

    def test_many_duplicates(self):
        assert find_median_sorted_arrays([2, 2, 2], [2, 2, 2]) == 2.0

    # Negative numbers
    def test_negative_numbers(self):
        assert find_median_sorted_arrays([-5, -3, -1], [-4, -2, 0]) == -2.5

    def test_mixed_positive_negative(self):
        assert find_median_sorted_arrays([-10, 0], [0, 10]) == 0.0

    # Large numbers
    def test_large_numbers(self):
        assert find_median_sorted_arrays([10**9], [10**9 + 1]) == 1e9 + 0.5

    # Larger arrays
    def test_larger_arrays(self):
        nums1 = list(range(1, 101))  # 1 to 100
        nums2 = list(range(101, 201))  # 101 to 200
        result = find_median_sorted_arrays(nums1, nums2)
        assert result == 100.5

    def test_unbalanced_arrays(self):
        # Small array with large array
        assert find_median_sorted_arrays([1], [2, 3, 4, 5, 6]) == 3.5

    def test_unbalanced_arrays2(self):
        # Large array with small array - median of [1,2,3,4,5,6] is (3+4)/2 = 3.5
        assert find_median_sorted_arrays([2, 3, 4, 5, 6], [1]) == 3.5

    # Verify against naive implementation
    @pytest.mark.parametrize(
        "nums1,nums2",
        [
            ([1, 3], [2]),
            ([1, 2], [3, 4]),
            ([], [1]),
            ([1], []),
            ([1, 2, 3], [4, 5, 6]),
            ([1, 1, 1], [1, 1, 1]),
            ([-5, -3, -1], [-4, -2, 0]),
            ([2, 2], [2, 2]),
            ([1, 2], [3]),
            ([1], [2, 3]),
        ],
    )
    def test_matches_naive(self, nums1: list[int], nums2: list[int]):
        """Verify result matches the naive O(m+n) merge solution."""
        expected = find_median_sorted_arrays_naive(nums1, nums2)
        result = find_median_sorted_arrays(nums1, nums2)
        assert result == expected
