"""Tests for LeetCode #42 Trapping Rain Water."""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "leet_code"))

from trapping_rain_water import trap


class TestTrappingRainWater:
    """Focused tests for trap()."""

    # --- LeetCode examples ---

    def test_example_1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_example_2(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9

    # --- Edge cases ---

    def test_empty(self) -> None:
        assert trap([]) == 0

    def test_single_bar(self) -> None:
        assert trap([5]) == 0

    def test_two_bars(self) -> None:
        assert trap([3, 7]) == 0

    def test_three_bars_valley(self) -> None:
        assert trap([3, 0, 3]) == 3

    def test_flat(self) -> None:
        assert trap([2, 2, 2, 2]) == 0

    # --- Monotonic sequences (no water) ---

    def test_ascending(self) -> None:
        assert trap([1, 2, 3, 4, 5]) == 0

    def test_descending(self) -> None:
        assert trap([5, 4, 3, 2, 1]) == 0

    # --- Shapes ---

    def test_v_shape(self) -> None:
        assert trap([5, 0, 5]) == 5

    def test_w_shape(self) -> None:
        assert trap([3, 0, 3, 0, 3]) == 6

    def test_asymmetric_walls(self) -> None:
        # Left wall shorter than right: water bounded by left wall
        assert trap([2, 0, 5]) == 2

    def test_multiple_pools(self) -> None:
        # Two separate pools
        assert trap([3, 0, 2, 0, 4]) == 7

    def test_staircase_down_up(self) -> None:
        assert trap([4, 3, 2, 1, 2, 3, 4]) == 9

    # --- Large values ---

    def test_tall_walls_deep_valley(self) -> None:
        assert trap([100000, 0, 100000]) == 100000

    # --- All zeros ---

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0, 0]) == 0

    # --- Single trapped unit ---

    def test_single_unit_trapped(self) -> None:
        assert trap([1, 0, 1]) == 1

    # --- Plateau with dip ---

    def test_plateau_with_dip(self) -> None:
        assert trap([3, 3, 0, 3, 3]) == 3
