"""
Tests for LeetCode #42 — Trapping Rain Water.

Focused test suite covering edge cases, canonical examples,
and adversarial inputs.
"""

from __future__ import annotations

import sys
import os

# Add leet_code to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'leet_code'))

from trapping_rain_water import trap


class TestTrappingRainWater:
    """Core correctness tests for trap()."""

    # --- LeetCode examples ---

    def test_example_1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_example_2(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9

    # --- Edge cases ---

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

    # --- Shapes ---

    def test_ascending(self) -> None:
        """Strictly ascending — no water trapped."""
        assert trap([1, 2, 3, 4, 5]) == 0

    def test_descending(self) -> None:
        """Strictly descending — no water trapped."""
        assert trap([5, 4, 3, 2, 1]) == 0

    def test_flat(self) -> None:
        """All same height — no water trapped."""
        assert trap([3, 3, 3, 3]) == 0

    def test_valley(self) -> None:
        """Simple V-shape valley."""
        assert trap([5, 0, 5]) == 5

    def test_asymmetric_valley(self) -> None:
        """Water bounded by the shorter side."""
        assert trap([3, 0, 5]) == 3

    def test_multiple_valleys(self) -> None:
        """Two separate pools."""
        assert trap([3, 0, 3, 0, 3]) == 6

    def test_staircase_up_then_down(self) -> None:
        """Pyramid — no water trapped."""
        assert trap([1, 2, 3, 2, 1]) == 0

    def test_bathtub(self) -> None:
        """Walls on both ends, zeros in middle."""
        assert trap([5, 0, 0, 0, 5]) == 15

    def test_nested_valleys(self) -> None:
        """Valley within a valley."""
        assert trap([4, 1, 3, 1, 4]) == 7

    # --- Large / stress ---

    def test_large_flat_valley(self) -> None:
        """Wide flat valley between two tall walls."""
        height = [100] + [0] * 1000 + [100]
        assert trap(height) == 100_000

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0, 0]) == 0

    def test_single_peak(self) -> None:
        """Peak in center — no water."""
        assert trap([0, 0, 5, 0, 0]) == 0

    def test_alternating(self) -> None:
        """Alternating high-low pattern."""
        assert trap([2, 0, 2, 0, 2]) == 4

    def test_decreasing_peaks(self) -> None:
        """Peaks get shorter — water only trapped by shorter boundary."""
        # [5,0,4,0,3,0,2]
        # Between 5 and 4: 4 water
        # Between 4 and 3: 3 water
        # Between 3 and 2: 2 water
        assert trap([5, 0, 4, 0, 3, 0, 2]) == 9
