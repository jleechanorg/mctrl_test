"""
LeetCode #4 - Median of Two Sorted Arrays (Hard)

Given two sorted arrays nums1 and nums2, return the median of the two sorted
arrays. Time complexity: O(log(m+n)).
"""
from __future__ import annotations


def find_median_sorted_arrays(nums1: list[int], nums2: list[int]) -> float:
    # Ensure nums1 is the shorter array for binary search efficiency
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    half = (m + n + 1) // 2

    lo, hi = 0, m
    while lo <= hi:
        i = (lo + hi) // 2  # partition index in nums1
        j = half - i         # partition index in nums2

        left1 = nums1[i - 1] if i > 0 else float("-inf")
        right1 = nums1[i] if i < m else float("inf")
        left2 = nums2[j - 1] if j > 0 else float("-inf")
        right2 = nums2[j] if j < n else float("inf")

        if left1 <= right2 and left2 <= right1:
            # Found the correct partition
            if (m + n) % 2 == 1:
                return float(max(left1, left2))
            return (max(left1, left2) + min(right1, right2)) / 2.0
        elif left1 > right2:
            hi = i - 1
        else:
            lo = i + 1

    raise ValueError("Input arrays are not sorted")


# --- Tests ---

def test_example1() -> None:
    assert find_median_sorted_arrays([1, 3], [2]) == 2.0


def test_example2() -> None:
    assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5


def test_single_elements() -> None:
    assert find_median_sorted_arrays([1], [2]) == 1.5


def test_empty_first() -> None:
    assert find_median_sorted_arrays([], [1]) == 1.0


def test_empty_second() -> None:
    assert find_median_sorted_arrays([2], []) == 2.0


def test_both_empty_one_element() -> None:
    assert find_median_sorted_arrays([], [5, 6, 7]) == 6.0


def test_larger_arrays() -> None:
    assert find_median_sorted_arrays([1, 2, 3, 4, 5], [6, 7, 8, 9, 10]) == 5.5


def test_overlapping() -> None:
    assert find_median_sorted_arrays([1, 3, 5, 7], [2, 4, 6, 8]) == 4.5


def test_identical() -> None:
    assert find_median_sorted_arrays([1, 1, 1], [1, 1, 1]) == 1.0


def test_negative_numbers() -> None:
    assert find_median_sorted_arrays([-5, -3, -1], [-2, 0, 2]) == -1.5


def test_single_large_vs_small() -> None:
    assert find_median_sorted_arrays([100000], [-100000]) == 0.0


if __name__ == "__main__":
    test_example1()
    test_example2()
    test_single_elements()
    test_empty_first()
    test_empty_second()
    test_both_empty_one_element()
    test_larger_arrays()
    test_overlapping()
    test_identical()
    test_negative_numbers()
    test_single_large_vs_small()
    print("All tests passed!")
