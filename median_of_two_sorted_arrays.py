from __future__ import annotations


def find_median_sorted_arrays(nums1: list[int], nums2: list[int]) -> float:
    """
    LeetCode #4 – Median of Two Sorted Arrays.

    Given two sorted arrays nums1 and nums2, return the median of the two
    sorted arrays in O(log(min(m, n))) time.
    """
    # Ensure binary search runs on the shorter array.
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    half = (m + n + 1) // 2

    lo, hi = 0, m
    while lo <= hi:
        i = (lo + hi) // 2  # partition index in nums1
        j = half - i        # partition index in nums2

        left1 = nums1[i - 1] if i > 0 else float("-inf")
        left2 = nums2[j - 1] if j > 0 else float("-inf")
        right1 = nums1[i] if i < m else float("inf")
        right2 = nums2[j] if j < n else float("inf")

        if left1 <= right2 and left2 <= right1:
            # Correct partition found.
            if (m + n) % 2 == 1:
                return float(max(left1, left2))
            return (max(left1, left2) + min(right1, right2)) / 2.0

        if left1 > right2:
            hi = i - 1
        else:
            lo = i + 1

    raise ValueError("Input arrays are not sorted")
