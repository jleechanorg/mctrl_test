"""
Focused tests for LeetCode #42 — Trapping Rain Water.

Tests both the O(1)-space two-pointer solution and the O(n)-space DP solution,
verifying they agree on all inputs.
"""

from __future__ import annotations

import pytest

from leet_code.trapping_rain_water import trap, trap_dp


# ── LeetCode examples ──────────────────────────────────────────────

class TestLeetCodeExamples:
    def test_example_1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_example_2(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9


# ── Edge cases ──────────────────────────────────────────────────────

class TestEdgeCases:
    def test_empty(self) -> None:
        assert trap([]) == 0

    def test_single_bar(self) -> None:
        assert trap([5]) == 0

    def test_two_bars(self) -> None:
        assert trap([3, 7]) == 0

    def test_three_bars_no_trap(self) -> None:
        assert trap([1, 2, 3]) == 0

    def test_three_bars_trap(self) -> None:
        assert trap([3, 0, 3]) == 3

    def test_all_same_height(self) -> None:
        assert trap([4, 4, 4, 4]) == 0

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0, 0]) == 0


# ── Shape patterns ──────────────────────────────────────────────────

class TestShapes:
    def test_v_shape(self) -> None:
        # Simple valley
        assert trap([5, 0, 5]) == 5

    def test_ascending(self) -> None:
        assert trap([1, 2, 3, 4, 5]) == 0

    def test_descending(self) -> None:
        assert trap([5, 4, 3, 2, 1]) == 0

    def test_peak(self) -> None:
        # Mountain shape — no water
        assert trap([1, 3, 5, 3, 1]) == 0

    def test_two_peaks_one_valley(self) -> None:
        assert trap([5, 1, 5]) == 4

    def test_staircase_down_then_wall(self) -> None:
        # [5,4,3,2,1,6] — water fills from right wall
        assert trap([5, 4, 3, 2, 1, 6]) == 10

    def test_multiple_valleys(self) -> None:
        # Two separate pools
        assert trap([3, 0, 3, 0, 3]) == 6

    def test_asymmetric_walls(self) -> None:
        # Shorter wall limits the water
        assert trap([2, 0, 5]) == 2

    def test_wide_basin(self) -> None:
        assert trap([10, 0, 0, 0, 0, 10]) == 40


# ── Larger / stress inputs ──────────────────────────────────────────

class TestLargerInputs:
    def test_alternating_high_low(self) -> None:
        # [5,0,5,0,5,0,5] → 3 valleys of 5 each
        assert trap([5, 0, 5, 0, 5, 0, 5]) == 15

    def test_constraint_max_size(self) -> None:
        """20_000 elements — verify O(n) doesn't time out."""
        height = list(range(10_000)) + list(range(10_000, -1, -1))
        result = trap(height)
        assert result == 0  # perfect pyramid, no water

    def test_deep_well(self) -> None:
        """Tall walls, wide zero floor."""
        height = [100_000] + [0] * 19_998 + [100_000]
        assert trap(height) == 100_000 * 19_998


# ── Cross-check: two-pointer vs DP ─────────────────────────────────

CROSS_CHECK_CASES = [
    [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],
    [4, 2, 0, 3, 2, 5],
    [3, 0, 3],
    [5, 4, 3, 2, 1, 6],
    [3, 0, 3, 0, 3],
    [2, 0, 5],
    [10, 0, 0, 0, 0, 10],
    [5, 0, 5, 0, 5, 0, 5],
    [0, 0, 0],
    [1],
    [],
    [1, 2, 3, 4, 3, 2, 1, 2, 3, 4, 3, 2, 1],
]


@pytest.mark.parametrize("height", CROSS_CHECK_CASES)
def test_two_pointer_matches_dp(height: list[int]) -> None:
    assert trap(height) == trap_dp(height)
