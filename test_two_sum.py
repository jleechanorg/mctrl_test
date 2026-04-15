"""Unit tests for Two Sum (LeetCode 1)."""
import pytest

from two_sum import two_sum


class TestTwoSum:
    def test_example_1(self) -> None:
        assert two_sum([2, 7, 11, 15], 9) == [0, 1]

    def test_example_2(self) -> None:
        assert two_sum([3, 2, 4], 6) == [1, 2]

    def test_example_3(self) -> None:
        assert two_sum([3, 3], 6) == [0, 1]

    def test_negative_numbers(self) -> None:
        assert two_sum([-1, -2, -3, -4, -5], -8) == [2, 4]

    def test_zero_target(self) -> None:
        assert two_sum([0, 4, 3, 0], 0) == [0, 3]

    def test_no_solution_raises(self) -> None:
        with pytest.raises(ValueError, match="No two elements"):
            two_sum([1, 2, 3], 10)
