"""Tests for LeetCode #42 — Trapping Rain Water."""

from __future__ import annotations

import sys
import os

# Add leet_code to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "leet_code"))

from trapping_rain_water import trap


class TestLeetCodeExamples:
    """Official LeetCode examples."""

    def test_example_1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_example_2(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9


class TestEdgeCases:
    """Boundary and degenerate inputs."""

    def test_empty_array(self) -> None:
        assert trap([]) == 0

    def test_single_element(self) -> None:
        assert trap([5]) == 0

    def test_two_elements(self) -> None:
        assert trap([3, 7]) == 0

    def test_three_elements_no_trap(self) -> None:
        assert trap([1, 2, 3]) == 0

    def test_three_elements_with_trap(self) -> None:
        assert trap([3, 0, 3]) == 3

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0, 0]) == 0

    def test_all_same_height(self) -> None:
        assert trap([5, 5, 5, 5]) == 0


class TestPatterns:
    """Recognizable elevation patterns."""

    def test_ascending(self) -> None:
        assert trap([1, 2, 3, 4, 5]) == 0

    def test_descending(self) -> None:
        assert trap([5, 4, 3, 2, 1]) == 0

    def test_valley(self) -> None:
        # Single valley: walls of 5, floor of 0, width 3
        assert trap([5, 0, 0, 0, 5]) == 15

    def test_peak(self) -> None:
        assert trap([0, 1, 2, 3, 2, 1, 0]) == 0

    def test_two_valleys(self) -> None:
        assert trap([3, 0, 3, 0, 3]) == 6

    def test_staircase_down_then_up(self) -> None:
        # 4,3,2,1,2,3,4 — symmetric valley
        assert trap([4, 3, 2, 1, 2, 3, 4]) == 9

    def test_asymmetric_walls(self) -> None:
        # Left wall shorter — water bounded by left wall
        assert trap([2, 0, 0, 5]) == 4

    def test_multiple_pools(self) -> None:
        assert trap([5, 2, 1, 2, 1, 5]) == 14

    def test_tall_spike_in_middle(self) -> None:
        # No water trapped — spike doesn't form a container
        assert trap([0, 0, 10, 0, 0]) == 0


class TestLargeInput:
    """Performance and scale."""

    def test_large_valley(self) -> None:
        n = 20000
        height = [n] + [0] * (n - 2) + [n]
        expected = n * (n - 2)
        assert trap(height) == expected

    def test_sawtooth(self) -> None:
        # Alternating 0,1,0,1,...,1 — each interior 0 between two 1s holds 1 unit
        height = [i % 2 for i in range(1000)]  # starts 0, ends 1
        # Water fills every 0 that has a 1 on both sides = 499 zeroes trapped
        assert trap(height) == 499

    def test_zigzag_with_trap(self) -> None:
        # [2,0,2,0,2,...] — each valley holds 2
        height = [2, 0] * 500 + [2]
        assert trap(height) == 2 * 500
