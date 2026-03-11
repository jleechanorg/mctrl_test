from __future__ import annotations

import pytest

from leetcode.sliding_window_maximum import max_sliding_window


class TestMaxSlidingWindow:
    """Tests for LeetCode 239 - Sliding Window Maximum."""

    def test_leetcode_example1(self) -> None:
        assert max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]

    def test_leetcode_example2(self) -> None:
        assert max_sliding_window([1], 1) == [1]

    def test_window_equals_array_length(self) -> None:
        assert max_sliding_window([4, 2, 7, 1], 4) == [7]

    def test_window_size_one(self) -> None:
        assert max_sliding_window([9, 3, 5, 1, 8], 1) == [9, 3, 5, 1, 8]

    def test_all_same_elements(self) -> None:
        assert max_sliding_window([5, 5, 5, 5], 2) == [5, 5, 5]

    def test_descending_order(self) -> None:
        assert max_sliding_window([5, 4, 3, 2, 1], 3) == [5, 4, 3]

    def test_ascending_order(self) -> None:
        assert max_sliding_window([1, 2, 3, 4, 5], 3) == [3, 4, 5]

    def test_negative_values(self) -> None:
        assert max_sliding_window([-7, -3, -5, -1, -9], 2) == [-3, -3, -1, -1]

    def test_empty_input(self) -> None:
        assert max_sliding_window([], 3) == []

    def test_large_window(self) -> None:
        nums = list(range(10000))
        result = max_sliding_window(nums, 100)
        assert len(result) == 9901
        assert result[-1] == 9999
        assert result[0] == 99
