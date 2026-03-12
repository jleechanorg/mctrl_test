"""Tests for LeetCode 42 - Trapping Rain Water."""

import pytest
from trap import trap


@pytest.mark.parametrize(
    "height, expected",
    [
        # LeetCode examples
        ([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1], 6),
        ([4, 2, 0, 3, 2, 5], 9),
        # Edge cases
        ([], 0),
        ([1], 0),
        ([1, 2], 0),
        ([2, 1], 0),
        # No trapping
        ([1, 2, 3, 4, 5], 0),
        ([5, 4, 3, 2, 1], 0),
        # Simple trap
        ([3, 0, 3], 3),
        ([2, 0, 2], 2),
        # Uneven walls
        ([3, 0, 2], 2),
        ([2, 0, 3], 2),
        # Multiple pools
        ([3, 0, 3, 0, 3], 6),
        ([5, 2, 1, 2, 1, 5], 14),
        # Flat
        ([0, 0, 0], 0),
        ([3, 3, 3], 0),
        # Large valley
        ([5, 0, 0, 0, 0, 5], 20),
        # Staircase with pool
        ([1, 0, 2, 0, 3], 3),
    ],
)
def test_trap(height, expected):
    assert trap(height) == expected
