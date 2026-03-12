"""
Median of Two Sorted Arrays - LeetCode #4 (Hard)

Given two sorted arrays nums1 and nums2 of size m and n respectively,
return the median of the two sorted arrays.

The overall run time complexity should be O(log (m+n)).

Example 1:
    Input: nums1 = [1,3], nums2 = [2]
    Output: 2.00000
    Explanation: merged array = [1,2,3] and median is 2.

Example 2:
    Input: nums1 = [1,2], nums2 = [3,4]
    Output: 2.50000
    Explanation: merged array = [1,2,3,4] and median is (2 + 3) / 2 = 2.5.

Constraints:
    - nums1.length == m
    - nums2.length == n
    - 0 <= m <= 1000
    - 0 <= n <= 1000
    - 1 <= m + n <= 2000
    - -10^6 <= nums1[i], nums2[i] <= 10^6
"""
from __future__ import annotations


def find_median_sorted_arrays(nums1: list[int], nums2: list[int]) -> float:
    """
    Find the median of two sorted arrays using binary search.

    Approach: Binary search on the smaller array to find the correct partition.
    Time Complexity: O(log(min(m, n)))
    Space Complexity: O(1)

    Args:
        nums1: First sorted array
        nums2: Second sorted array

    Returns:
        The median of the two sorted arrays
    """
    # Ensure nums1 is the smaller array for optimization
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    low, high = 0, m

    while low <= high:
        partition1 = (low + high) // 2
        partition2 = (m + n + 1) // 2 - partition1

        # Get left and right boundary values
        max_left1 = float('-inf') if partition1 == 0 else nums1[partition1 - 1]
        min_right1 = float('inf') if partition1 == m else nums1[partition1]

        max_left2 = float('-inf') if partition2 == 0 else nums2[partition2 - 1]
        min_right2 = float('inf') if partition2 == n else nums2[partition2]

        # Check if we found the correct partition
        if max_left1 <= min_right2 and max_left2 <= min_right1:
            # Found the correct partition
            if (m + n) % 2 == 0:
                return (max(max_left1, max_left2) + min(min_right1, min_right2)) / 2
            else:
                return float(max(max_left1, max_left2))
        elif max_left1 > min_right2:
            # Move left in nums1
            high = partition1 - 1
        else:
            # Move right in nums1
            low = partition1 + 1

    raise ValueError("Input arrays are not valid")


def find_median_sorted_arrays_brute(nums1: list[int], nums2: list[int]) -> float:
    """
    Brute force solution - merge and find median.

    Time Complexity: O(m + n)
    Space Complexity: O(m + n)

    Args:
        nums1: First sorted array
        nums2: Second sorted array

    Returns:
        The median of the two sorted arrays
    """
    merged = sorted(nums1 + nums2)
    n = len(merged)

    if n % 2 == 0:
        return (merged[n // 2 - 1] + merged[n // 2]) / 2
    else:
        return float(merged[n // 2])
