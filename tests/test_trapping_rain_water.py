"""
Tests for LeetCode #42 — Trapping Rain Water.

Covers: LeetCode examples, edge cases, monotonic sequences,
single-basin, plateaus, large input, and stress.
"""

from __future__ import annotations

import pytest

from leet_code.trapping_rain_water import trap


# ── LeetCode examples ──────────────────────────────────────────────

class TestLeetCodeExamples:
    def test_example_1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_example_2(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9


# ── Edge cases ──────────────────────────────────────────────────────

class TestEdgeCases:
    def test_empty_list(self) -> None:
        assert trap([]) == 0

    def test_single_bar(self) -> None:
        assert trap([5]) == 0

    def test_two_bars(self) -> None:
        assert trap([3, 7]) == 0

    def test_three_bars_no_trap(self) -> None:
        assert trap([1, 2, 3]) == 0

    def test_three_bars_with_trap(self) -> None:
        assert trap([3, 0, 3]) == 3

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0, 0]) == 0

    def test_all_same_height(self) -> None:
        assert trap([5, 5, 5, 5]) == 0


# ── Monotonic sequences ────────────────────────────────────────────

class TestMonotonic:
    def test_strictly_increasing(self) -> None:
        assert trap([1, 2, 3, 4, 5]) == 0

    def test_strictly_decreasing(self) -> None:
        assert trap([5, 4, 3, 2, 1]) == 0


# ── Basin patterns ──────────────────────────────────────────────────

class TestBasins:
    def test_single_deep_basin(self) -> None:
        # 3 gaps × depth 5 = 15
        assert trap([5, 0, 0, 0, 5]) == 15

    def test_asymmetric_basin(self) -> None:
        # Water limited by shorter wall (3)
        assert trap([5, 0, 0, 3]) == 6

    def test_multiple_basins(self) -> None:
        # Two distinct pools
        assert trap([3, 0, 3, 0, 3]) == 6

    def test_nested_basin(self) -> None:
        # Staircase down then up
        assert trap([5, 2, 1, 2, 5]) == 10

    def test_v_shape(self) -> None:
        assert trap([3, 1, 3]) == 2


# ── Plateaus and flat tops ──────────────────────────────────────────

class TestPlateaus:
    def test_plateau_walls(self) -> None:
        # 2 inner zeros × depth 3 = 6
        assert trap([3, 3, 0, 0, 3, 3]) == 6

    def test_plateau_floor(self) -> None:
        # 3 inner zeros × depth 2 = 6
        assert trap([2, 0, 0, 0, 2]) == 6


# ── Larger / stress inputs ─────────────────────────────────────────

class TestStress:
    def test_large_mountain(self) -> None:
        # Rising then falling — no water trapped
        n = 10_000
        height = list(range(n)) + list(range(n, -1, -1))
        assert trap(height) == 0

    def test_large_valley(self) -> None:
        # Two tall walls with zeros between
        n = 20_000
        height = [n] + [0] * (n - 2) + [n]
        expected = n * (n - 2)
        assert trap(height) == expected

    def test_alternating_spikes(self) -> None:
        # [5,0,5,0,5,...] — each gap traps 5
        n = 1_000
        height = [5 if i % 2 == 0 else 0 for i in range(n)]
        # 499 valleys of depth 5
        assert trap(height) == 499 * 5
