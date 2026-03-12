"""Tests for Trapping Rain Water solution."""

import pytest
from src.trapping_rain_water import Solution


class TestTrapRainWater:
    def setup_method(self):
        self.sol = Solution()
    
    def test_basic_example(self):
        """Test the basic example from LeetCode."""
        height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
        assert self.sol.trap(height) == 6
    
    def test_example_2(self):
        """Test the second example from LeetCode."""
        height = [4, 2, 0, 3, 2, 5]
        assert self.sol.trap(height) == 9
    
    def test_empty_array(self):
        """Test with empty array."""
        assert self.sol.trap([]) == 0
    
    def test_single_element(self):
        """Test with single element."""
        assert self.sol.trap([1]) == 0
    
    def test_two_elements(self):
        """Test with two elements."""
        assert self.sol.trap([1, 2]) == 0
    
    def test_no_water_descending(self):
        """Test with descending heights (no water)."""
        height = [5, 4, 3, 2, 1]
        assert self.sol.trap(height) == 0
    
    def test_no_water_ascending(self):
        """Test with ascending heights (no water)."""
        height = [1, 2, 3, 4, 5]
        assert self.sol.trap(height) == 0
    
    def test_single_peak(self):
        """Test with single peak in middle."""
        height = [2, 0, 2]
        assert self.sol.trap(height) == 2
    
    def test_multiple_peaks(self):
        """Test with multiple peaks."""
        height = [3, 0, 0, 2, 0, 4]
        assert self.sol.trap(height) == 10
    
    def test_valley_shape(self):
        """Test valley shaped heights."""
        height = [5, 4, 1, 2, 1, 2, 5]
        assert self.sol.trap(height) == 15
    
    def test_flat_surface(self):
        """Test with flat surface."""
        height = [1, 1, 1, 1, 1]
        assert self.sol.trap(height) == 0
    
    def test_all_zeros(self):
        """Test with all zeros."""
        height = [0, 0, 0, 0, 0]
        assert self.sol.trap(height) == 0
    
    def test_boundary_cases(self):
        """Test with zeros at boundaries."""
        height = [0, 5, 0, 0, 0, 5]
        assert self.sol.trap(height) == 15
    
    def test_large_values(self):
        """Test with larger height values."""
        height = [5, 0, 5]
        assert self.sol.trap(height) == 5
    
    def test_alternating(self):
        """Test with alternating high-low pattern."""
        height = [1, 0, 1]
        assert self.sol.trap(height) == 1
