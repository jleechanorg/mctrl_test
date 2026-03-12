"""
Test cases for Median of Two Sorted Arrays solution.
"""
from __future__ import annotations

import pytest

from median_of_two_sorted_arrays import find_median_sorted_arrays


class TestFindMedianSortedArrays:
    """Test cases for the median of two sorted arrays problem."""

    def test_example_1(self):
        """Example 1 from LeetCode: [1,3], [2] -> 2.0"""
        assert find_median_sorted_arrays([1, 3], [2]) == 2.0

    def test_example_2(self):
        """Example 2 from LeetCode: [1,2], [3,4] -> 2.5"""
        assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5

    def test_both_empty(self):
        """Both arrays empty -> ValueError"""
        with pytest.raises(ValueError):
            find_median_sorted_arrays([], [])

    def test_one_empty_first(self):
        """First array empty"""
        assert find_median_sorted_arrays([], [1]) == 1.0

    def test_one_empty_second(self):
        """Second array empty"""
        assert find_median_sorted_arrays([1], []) == 1.0

    def test_single_element_both(self):
        """Single element in both arrays"""
        assert find_median_sorted_arrays([1], [2]) == 1.5

    def test_single_element_different(self):
        """Single element with different values"""
        assert find_median_sorted_arrays([1], [3]) == 2.0

    def test_identical_arrays(self):
        """Both arrays have identical elements"""
        assert find_median_sorted_arrays([1, 2, 3], [1, 2, 3]) == 2.0

    def test_first_array_longer(self):
        """First array is longer than second"""
        assert find_median_sorted_arrays([1, 2, 3, 4, 5], [6, 7]) == 4.0

    def test_second_array_longer(self):
        """Second array is longer than first"""
        assert find_median_sorted_arrays([1, 2], [3, 4, 5, 6, 7]) == 4.0

    def test_even_total_elements(self):
        """Total number of elements is even"""
        assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5

    def test_odd_total_elements(self):
        """Total number of elements is odd"""
        assert find_median_sorted_arrays([1, 2, 3], [4, 5]) == 3.0

    def test_negative_numbers(self):
        """Arrays with negative numbers"""
        assert find_median_sorted_arrays([-5, -3, -1], [-4, -2, 0]) == -2.5

    def test_mixed_positive_negative(self):
        """Arrays with both positive and negative numbers"""
        # Merged: [-1, 0, 1, 2, 3, 4] -> 6 elements -> median = (1+2)/2 = 1.5
        assert find_median_sorted_arrays([-1, 0, 1], [2, 3, 4]) == 1.5

    def test_large_gap_values(self):
        """Arrays with large gap between values"""
        assert find_median_sorted_arrays([1, 1000], [2, 3]) == 2.5

    def test_duplicate_values(self):
        """Arrays with many duplicate values"""
        assert find_median_sorted_arrays([1, 1, 1, 1], [1, 1, 1, 1]) == 1.0

    def test_duplicates_at_boundary(self):
        """Duplicates at partition boundary"""
        assert find_median_sorted_arrays([1, 2, 2], [2, 3, 3]) == 2.0

    def test_min_length_one_array(self):
        """One array has minimum length (1 element)"""
        assert find_median_sorted_arrays([1], [2, 3, 4, 5]) == 3.0

    def test_large_values(self):
        """Arrays with large integer values"""
        assert find_median_sorted_arrays([1000000], [1000001]) == 1000000.5

    def test_small_values(self):
        """Arrays with small integer values"""
        assert find_median_sorted_arrays([-1000000], [-999999]) == -999999.5

    def test_complex_case_1(self):
        """Complex test case 1"""
        assert find_median_sorted_arrays([1, 2, 3, 4, 5], [6, 7, 8, 9, 10]) == 5.5

    def test_complex_case_2(self):
        """Complex test case 2"""
        assert find_median_sorted_arrays([1, 3, 5, 7, 9], [2, 4, 6, 8, 10]) == 5.5

    def test_overlapping_ranges(self):
        """Arrays with overlapping value ranges"""
        assert find_median_sorted_arrays([1, 2, 3], [2, 3, 4]) == 2.5

    def test_all_elements_in_one_array(self):
        """All elements in one array, other is small"""
        assert find_median_sorted_arrays([1, 2, 3, 4, 5], [10]) == 3.5


class TestFindMedianEdgeCases:
    """Edge case tests for median calculation."""

    def test_both_single_element(self):
        """Both arrays have single element"""
        result = find_median_sorted_arrays([5], [5])
        assert result == 5.0

    def test_first_array_larger_second_single(self):
        """First array larger, second has single element"""
        # Merged: [1, 2, 3, 4, 5] -> 5 elements -> median = 3
        result = find_median_sorted_arrays([1, 2, 3, 4], [5])
        assert result == 3

    def test_second_array_larger_first_single(self):
        """Second array larger, first has single element"""
        # Merged: [1, 2, 3, 4, 5] -> 5 elements -> median = 3
        result = find_median_sorted_arrays([1], [2, 3, 4, 5])
        assert result == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
