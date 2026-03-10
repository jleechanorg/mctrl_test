import random

import pytest

from median_sliding_window import median_sliding_window


def brute_force_medians(nums: list[int], k: int) -> list[float]:
    out: list[float] = []
    for i in range(len(nums) - k + 1):
        window = sorted(nums[i : i + k])
        if k % 2 == 1:
            out.append(float(window[k // 2]))
        else:
            out.append((window[k // 2 - 1] + window[k // 2]) / 2.0)
    return out


def test_leetcode_example_1() -> None:
    nums = [1, 3, -1, -3, 5, 3, 6, 7]
    k = 3
    assert median_sliding_window(nums, k) == [1.0, -1.0, -1.0, 3.0, 5.0, 6.0]


def test_leetcode_example_2() -> None:
    nums = [1, 2]
    k = 1
    assert median_sliding_window(nums, k) == [1.0, 2.0]


def test_even_window_size() -> None:
    nums = [1, 4, 2, 3]
    k = 2
    assert median_sliding_window(nums, k) == [2.5, 3.0, 2.5]


def test_all_equal_values() -> None:
    nums = [7, 7, 7, 7, 7]
    k = 3
    assert median_sliding_window(nums, k) == [7.0, 7.0, 7.0]


def test_with_negative_and_duplicate_values() -> None:
    nums = [-5, -5, -1, -1, 0, 2, 2]
    k = 4
    assert median_sliding_window(nums, k) == [-3.0, -1.0, -0.5, 1.0]


def test_k_equals_full_length() -> None:
    nums = [9, 1, 8, 2, 7]
    k = len(nums)
    assert median_sliding_window(nums, k) == [7.0]


def test_invalid_k_raises() -> None:
    with pytest.raises(ValueError):
        median_sliding_window([1, 2, 3], 0)
    with pytest.raises(ValueError):
        median_sliding_window([1, 2, 3], 4)


def test_randomized_against_bruteforce() -> None:
    rng = random.Random(42)
    for _ in range(120):
        n = rng.randint(1, 30)
        nums = [rng.randint(-50, 50) for _ in range(n)]
        k = rng.randint(1, n)
        assert median_sliding_window(nums, k) == brute_force_medians(nums, k)
