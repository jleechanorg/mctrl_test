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
    Find the median of two sorted arrays.

    Uses binary search on the smaller array to achieve O(log(min(m, n))) time complexity.
    The key insight is to partition both arrays such that:
    - Left half contains all elements <= right half
    - Both halves have equal number of elements (or differ by 1 for odd total)

    Args:
        nums1: First sorted array (can be empty)
        nums2: Second sorted array (can be empty)

    Returns:
        The median value as a float

    Time Complexity: O(log(min(m, n)))
    Space Complexity: O(1) - only uses constant extra space
    """
    # Ensure nums1 is the smaller array for optimal binary search
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    left, right = 0, m

    while left <= right:
        # Partition point in nums1
        partition1 = (left + right) // 2
        # Partition point in nums2 - to maintain equal total elements on both sides
        partition2 = (m + n + 1) // 2 - partition1

        # Get boundary values
        # maxLeft1: max value in left partition of nums1 (or -inf if partition at start)
        maxLeft1 = float('-inf') if partition1 == 0 else nums1[partition1 - 1]
        # minRight1: min value in right partition of nums1 (or inf if partition at end)
        minRight1 = float('inf') if partition1 == m else nums1[partition1]

        maxLeft2 = float('-inf') if partition2 == 0 else nums2[partition2 - 1]
        minRight2 = float('inf') if partition2 == n else nums2[partition2]

        # Check if we found the correct partition
        if maxLeft1 <= minRight2 and maxLeft2 <= minRight1:
            # Correct partition found
            if (m + n) % 2 == 0:
                # Even total: average of two middle values
                return (max(maxLeft1, maxLeft2) + min(minRight1, minRight2)) / 2
            else:
                # Odd total: middle value is max of left partitions
                return float(max(maxLeft1, maxLeft2))
        elif maxLeft1 > minRight2:
            # Too far right in nums1, move left
            right = partition1 - 1
        else:
            # Too far left in nums1, move right
            left = partition1 + 1

    raise ValueError("Input arrays are not sorted or invalid")


def find_median_sorted_arrays_simple(nums1: list[int], nums2: list[int]) -> float:
    """
    Simpler O(m+n) merge-based solution for comparison.

    Args:
        nums1: First sorted array
        nums2: Second sorted array

    Returns:
        The median value as a float

    Time Complexity: O(m + n)
    Space Complexity: O(m + n) for the merged array
    """
    merged = []
    i, j = 0, 0

    # Merge both arrays
    while i < len(nums1) and j < len(nums2):
        if nums1[i] <= nums2[j]:
            merged.append(nums1[i])
            i += 1
        else:
            merged.append(nums2[j])
            j += 1

    # Append remaining elements
    while i < len(nums1):
        merged.append(nums1[i])
        i += 1
    while j < len(nums2):
        merged.append(nums2[j])
        j += 1

    n = len(merged)
    mid = n // 2
    if n % 2 == 0:
        return (merged[mid - 1] + merged[mid]) / 2
    return float(merged[mid])


if __name__ == "__main__":
    # Example tests
    print(find_median_sorted_arrays([1, 3], [2]))  # 2.0
    print(find_median_sorted_arrays([1, 2], [3, 4]))  # 2.5
    print(find_median_sorted_arrays([1], [2, 3, 4]))  # 2.5
