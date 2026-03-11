"""
Trapping Rain Water - LeetCode Hard #42

Given n non-negative integers representing an elevation map where the width
of each bar is 1, compute how much water it can trap after raining.

Example 1:
Input: height = [0,1,0,2,1,0,1,3,2,1,2,1]
Output: 6

Example 2:
Input: height = [4,2,0,3,2,5]
Output: 9

Constraints:
- n == height.length
- 1 <= n <= 2 * 10^4
- 0 <= height[i] <= 10^5

Time Complexity: O(n) using two-pointer approach
Space Complexity: O(1)
"""

from __future__ import annotations
from typing import List


def trap(height: List[int]) -> int:
    """
    Calculate trapped rain water using the two-pointer technique.

    The key insight: water at any position is determined by
    min(max_left, max_right) - height[position].

    Two pointers converge from both ends. We always advance the
    pointer with the smaller max, because the water level at that
    side is guaranteed to be bounded by its own max (the other side
    is at least as tall).

    Args:
        height: List of non-negative integers representing elevation.

    Returns:
        Total units of trapped water.
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


def trap_dp(height: List[int]) -> int:
    """
    Alternative DP approach for verification.

    Precompute left_max[] and right_max[] arrays, then sum
    min(left_max[i], right_max[i]) - height[i] for each position.

    Time: O(n), Space: O(n)
    """
    n = len(height)
    if n < 3:
        return 0

    left_max = [0] * n
    right_max = [0] * n

    left_max[0] = height[0]
    for i in range(1, n):
        left_max[i] = max(left_max[i - 1], height[i])

    right_max[n - 1] = height[n - 1]
    for i in range(n - 2, -1, -1):
        right_max[i] = max(right_max[i + 1], height[i])

    water = 0
    for i in range(n):
        water += min(left_max[i], right_max[i]) - height[i]

    return water


# --------------- pytest tests ---------------

class TestTrappingRainWater:
    """Focused tests for LeetCode #42."""

    def test_example_1(self) -> None:
        assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6

    def test_example_2(self) -> None:
        assert trap([4, 2, 0, 3, 2, 5]) == 9

    def test_empty_and_trivial(self) -> None:
        assert trap([]) == 0
        assert trap([5]) == 0
        assert trap([1, 2]) == 0

    def test_no_trap_ascending(self) -> None:
        assert trap([1, 2, 3, 4, 5]) == 0

    def test_no_trap_descending(self) -> None:
        assert trap([5, 4, 3, 2, 1]) == 0

    def test_single_valley(self) -> None:
        # [3, 0, 3] traps 3 units
        assert trap([3, 0, 3]) == 3

    def test_deep_valley(self) -> None:
        # [5, 0, 0, 0, 5] traps 15 units
        assert trap([5, 0, 0, 0, 5]) == 15

    def test_staircase_up_down(self) -> None:
        # [0, 1, 2, 3, 2, 1, 0] — pyramid, no water
        assert trap([0, 1, 2, 3, 2, 1, 0]) == 0

    def test_multiple_valleys(self) -> None:
        # [2, 0, 2, 0, 2] — two valleys of 2 each
        assert trap([2, 0, 2, 0, 2]) == 4

    def test_asymmetric_walls(self) -> None:
        # [3, 0, 1, 0, 2] — bounded by min(3,2)=2
        # pos1: 2-0=2, pos2: 2-1=1, pos3: 2-0=2 => 5
        assert trap([3, 0, 1, 0, 2]) == 5

    def test_flat(self) -> None:
        assert trap([3, 3, 3, 3]) == 0

    def test_all_zeros(self) -> None:
        assert trap([0, 0, 0, 0]) == 0

    def test_large_values(self) -> None:
        # Two tall walls with zero between
        assert trap([100000, 0, 100000]) == 100000

    def test_alternating(self) -> None:
        # [1, 0, 1, 0, 1] => 2 units
        assert trap([1, 0, 1, 0, 1]) == 2

    def test_dp_matches_two_pointer(self) -> None:
        """Cross-validate both implementations on several inputs."""
        cases = [
            [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],
            [4, 2, 0, 3, 2, 5],
            [3, 0, 1, 0, 2],
            [5, 0, 0, 0, 5],
            [2, 0, 2, 0, 2],
            [1, 0, 1, 0, 1, 0, 1],
            [0],
            [],
        ]
        for h in cases:
            assert trap(h) == trap_dp(h), f"Mismatch on {h}"


if __name__ == "__main__":
    # Quick smoke test
    print(f"Example 1: {trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1])}")  # 6
    print(f"Example 2: {trap([4, 2, 0, 3, 2, 5])}")  # 9
    print("Done.")
