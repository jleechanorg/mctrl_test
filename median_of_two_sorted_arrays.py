"""
LeetCode 4 - Median of Two Sorted Arrays

Given two sorted arrays nums1 and nums2 of size m and n respectively,
return the median of the two sorted arrays.

The overall run time complexity should be O(log(m + n)).

https://leetcode.com/problems/median-of-two-sorted-arrays/
"""

from __future__ import annotations


def find_median_sorted_arrays(nums1: list[int], nums2: list[int]) -> float:
    """
    Find the median of two sorted arrays.

    Uses binary search on the smaller array to achieve O(log(min(m, n))) time.

    Args:
        nums1: First sorted array
        nums2: Second sorted array

    Returns:
        Median value as a float

    Time Complexity: O(log(min(m, n)))
    Space Complexity: O(1)
    """
    # Handle empty arrays
    if not nums1 and not nums2:
        return 0.0
    if not nums1:
        n = len(nums2)
        mid = n // 2
        if n % 2 == 0:
            return (nums2[mid - 1] + nums2[mid]) / 2
        return float(nums2[mid])
    if not nums2:
        m = len(nums1)
        mid = m // 2
        if m % 2 == 0:
            return (nums1[mid - 1] + nums1[mid]) / 2
        return float(nums1[mid])

    # Ensure nums1 is the smaller array for optimization
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    low, high = 0, m

    while low <= high:
        # Partition positions
        partition1 = (low + high) // 2
        partition2 = (m + n + 1) // 2 - partition1

        # Get boundary values
        max_left1 = float('-inf') if partition1 == 0 else nums1[partition1 - 1]
        min_right1 = float('inf') if partition1 == m else nums1[partition1]

        max_left2 = float('-inf') if partition2 == 0 else nums2[partition2 - 1]
        min_right2 = float('inf') if partition2 == n else nums2[partition2]

        # Check if we found the correct partition
        if max_left1 <= min_right2 and max_left2 <= min_right1:
            # Found correct partition
            if (m + n) % 2 == 0:
                return (max(max_left1, max_left2) + min(min_right1, min_right2)) / 2
            else:
                return float(max(max_left1, max_left2))
        elif max_left1 > min_right2:
            # Too far right in nums1, move left
            high = partition1 - 1
        else:
            # Too far left in nums1, move right
            low = partition1 + 1

    raise ValueError("Input arrays are not sorted")


if __name__ == "__main__":
    # Example usage
    print(find_median_sorted_arrays([1, 3], [2]))  # 2.0
    print(find_median_sorted_arrays([1, 2], [3, 4]))  # 2.5
