"""LeetCode #42 — Trapping Rain Water.

Implementation and focused tests.
"""

from __future__ import annotations


def trap(height: list[int]) -> int:
    """Calculate how much water can be trapped after raining.

    Uses two-pointer approach — O(n) time, O(1) space.
    """
    if len(height) < 3:
        return 0

    left, right = 0, len(height) - 1
    left_max, right_max = height[left], height[right]
    water = 0

    while left < right:
        if left_max <= right_max:
            left += 1
            left_max = max(left_max, height[left])
            water += left_max - height[left]
        else:
            right -= 1
            right_max = max(right_max, height[right])
            water += right_max - height[right]

    return water


# --------------- Tests ---------------

import pytest


class TestTrapRainWater:
    """Focused tests for LeetCode #42."""

    def test_classic_example(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_second_example(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9

    def test_empty(self) -> None:
        assert trap([]) == 0

    def test_single_bar(self) -> None:
        assert trap([5]) == 0

    def test_two_bars(self) -> None:
        assert trap([3, 7]) == 0

    def test_flat(self) -> None:
        assert trap([3, 3, 3, 3]) == 0

    def test_ascending(self) -> None:
        assert trap([1, 2, 3, 4, 5]) == 0

    def test_descending(self) -> None:
        assert trap([5, 4, 3, 2, 1]) == 0

    def test_v_shape(self) -> None:
        # [3, 0, 3] traps 3 units
        assert trap([3, 0, 3]) == 3

    def test_w_shape(self) -> None:
        # [3, 0, 3, 0, 3] traps 6 units
        assert trap([3, 0, 3, 0, 3]) == 6

    def test_single_trap(self) -> None:
        assert trap([2, 0, 2]) == 2

    def test_asymmetric_walls(self) -> None:
        # min(5,3)=3 over the gap: 3-1=2
        assert trap([5, 1, 3]) == 2

    def test_tall_edges_deep_valley(self) -> None:
        assert trap([10, 0, 0, 0, 10]) == 30

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0]) == 0

    def test_large_input(self) -> None:
        # Sawtooth pattern: 0,100,0,100,...
        n = 10_000
        height = [100 if i % 2 else 0 for i in range(n)]
        result = trap(height)
        assert result > 0
        # Each valley between two 100s traps 100 units; 4999 valleys
        assert result == 100 * (n // 2 - 1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
