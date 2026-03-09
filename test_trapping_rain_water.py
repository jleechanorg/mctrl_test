"""
Tests for Trapping Rain Water solution.
"""

import pytest
from trapping_rain_water import Solution, trap_brute_force, trap_dp


class TestTrappingRainWater:
    def setup_method(self):
        self.sol = Solution()

    def test_example(self):
        height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
        assert self.sol.trap(height) == 6

    def test_second_example(self):
        height = [4, 2, 0, 3, 2, 5]
        assert self.sol.trap(height) == 9

    def test_empty(self):
        assert self.sol.trap([]) == 0

    def test_no_water_trapped(self):
        height = [1, 2, 3, 4, 5]
        assert self.sol.trap(height) == 0

    def test_single_element(self):
        assert self.sol.trap([1]) == 0
        assert self.sol.trap([0]) == 0

    def test_two_elements(self):
        assert self.sol.trap([1, 0]) == 0
        assert self.sol.trap([1, 2]) == 0

    def test_valley(self):
        height = [1, 0, 1]
        assert self.sol.trap(height) == 1

    def test_multiple_valleys(self):
        height = [5, 4, 1, 2]
        assert self.sol.trap(height) == 1

    def test_all_same(self):
        height = [3, 3, 3, 3]
        assert self.sol.trap(height) == 0

    def test_negative_no(self):
        # No negative values in this problem per LeetCode
        pass


class TestTrapBruteForce:
    def test_same_as_optimized(self):
        sol = Solution()
        test_cases = [
            [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],
            [4, 2, 0, 3, 2, 5],
            [1, 0, 1],
            [5, 4, 1, 2],
        ]
        for height in test_cases:
            assert sol.trap(height) == trap_brute_force(height)


class TestTrapDP:
    def test_same_as_optimized(self):
        sol = Solution()
        test_cases = [
            [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],
            [4, 2, 0, 3, 2, 5],
            [1, 0, 1],
            [5, 4, 1, 2],
            [],
        ]
        for height in test_cases:
            assert sol.trap(height) == trap_dp(height)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
