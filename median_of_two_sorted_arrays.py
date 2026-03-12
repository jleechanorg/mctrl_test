"""
Median of Two Sorted Arrays - LeetCode #4

Given two sorted arrays nums1 and nums2 of size m and n respectively,
return the median of the two sorted arrays.

The overall run time complexity should be O(log(m + n)).

Example 1:
    Input: nums1 = [1,3], nums2 = [2]
    Output: 2.00000
    Explanation: merged array = [1,2,3] and median is 2.

Example 2:
    Input: nums1 = [1,2], nums2 = [3,4]
    Output: 2.50000
    Explanation: merged array = [1,2,3,4] and median is (2 + 3) / 2 = 2.5.
"""
from __future__ import annotations


def find_median_sorted_arrays(nums1: list[int], nums2: list[int]) -> float:
    """
    Find the median of two sorted arrays using binary search.

    Time Complexity: O(log(min(m, n))) where m = len(nums1), n = len(nums2)
    Space Complexity: O(1)

    The algorithm uses binary search on the shorter array to find a partition
    such that:
    - Left half of both arrays combined == Right half of both arrays combined
    - All elements on left are <= all elements on right

    This ensures the median is at the partition boundary.
    """
    # Ensure nums1 is the shorter array for binary search efficiency
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    low, high = 0, m

    while low <= high:
        # Partition positions
        partition1 = (low + high) // 2
        partition2 = (m + n + 1) // 2 - partition1

        # Get boundary values (use -inf/-inf for out of bounds)
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
                return max(max_left1, max_left2)
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

    This is a simpler but less efficient solution included for comparison.
    """
    merged = sorted(nums1 + nums2)
    n = len(merged)

    if n % 2 == 0:
        return (merged[n // 2 - 1] + merged[n // 2]) / 2
    else:
        return float(merged[n // 2])


if __name__ == "__main__":
    # Example tests
    print(find_median_sorted_arrays([1, 3], [2]))  # 2.0
    print(find_median_sorted_arrays([1, 2], [3, 4]))  # 2.5
    print(find_median_sorted_arrays([1, 2], [3]))  # 2.0
