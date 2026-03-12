"""
Median of Two Sorted Arrays - LeetCode #4 (Hard)

Given two sorted arrays nums1 and nums2 of size m and n respectively,
return the median of the two sorted arrays.

The overall run time complexity should be O(log(min(m, n))).

Example 1:
    Input: nums1 = [1,3], nums2 = [2]
    Output: 2.00000
    Explanation: merged array = [1,2,3], median is 2.

Example 2:
    Input: nums1 = [1,2], nums2 = [3,4]
    Output: 2.50000
    Explanation: merged array = [1,2,3,4], median is (2+3)/2 = 2.5.

Time Complexity: O(log(min(m, n))) - binary search on smaller array
Space Complexity: O(1) - only using constant extra space
"""
from __future__ import annotations


def find_median_sorted_arrays(nums1: list[int], nums2: list[int]) -> float:
    """
    Find the median of two sorted arrays using binary search.

    Strategy:
    - Ensure nums1 is the smaller array for optimization
    - Use binary search to find the correct partition where:
      - Left half contains half of combined elements
      - Right half contains the other half
      - All elements in left partition <= all elements in right partition

    Args:
        nums1: First sorted array
        nums2: Second sorted array

    Returns:
        The median value as a float
    """
    # Ensure nums1 is the smaller array
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    low, high = 0, m

    while low <= high:
        # Partition indices
        partition1 = (low + high) // 2
        partition2 = (m + n + 1) // 2 - partition1

        # Get boundary values (use -inf/-inf for edge cases)
        max_left1 = float('-inf') if partition1 == 0 else nums1[partition1 - 1]
        min_right1 = float('inf') if partition1 == m else nums1[partition1]

        max_left2 = float('-inf') if partition2 == 0 else nums2[partition2 - 1]
        min_right2 = float('inf') if partition2 == n else nums2[partition2]

        # Check if we found the correct partition
        if max_left1 <= min_right2 and max_left2 <= min_right1:
            # Found correct partition
            if (m + n) % 2 == 0:
                # Even total length: average of two middle elements
                return (max(max_left1, max_left2) + min(min_right1, min_right2)) / 2
            else:
                # Odd total length: middle element is max of left partitions
                return float(max(max_left1, max_left2))
        elif max_left1 > min_right2:
            # Partition1 is too far right, move left
            high = partition1 - 1
        else:
            # Partition1 is too far left, move right
            low = partition1 + 1

    raise ValueError("Input arrays are not sorted or have invalid values")


def find_median_sorted_arrays_naive(nums1: list[int], nums2: list[int]) -> float:
    """
    Naive O(m+n) solution for verification - merge and find median.

    Args:
        nums1: First sorted array
        nums2: Second sorted array

    Returns:
        The median value as a float
    """
    merged = []
    i, j = 0, 0

    # Merge sorted arrays
    while i < len(nums1) and j < len(nums2):
        if nums1[i] <= nums2[j]:
            merged.append(nums1[i])
            i += 1
        else:
            merged.append(nums2[j])
            j += 1

    # Add remaining elements
    while i < len(nums1):
        merged.append(nums1[i])
        i += 1
    while j < len(nums2):
        merged.append(nums2[j])
        j += 1

    # Find median
    n = len(merged)
    if n % 2 == 0:
        return (merged[n // 2 - 1] + merged[n // 2]) / 2
    else:
        return float(merged[n // 2])


if __name__ == "__main__":
    # Example tests
    print(find_median_sorted_arrays([1, 3], [2]))  # 2.0
    print(find_median_sorted_arrays([1, 2], [3, 4]))  # 2.5
    print(find_median_sorted_arrays([1, 2, 3], [4, 5]))  # 3.0
    print(find_median_sorted_arrays([1], [2, 3, 4]))  # 2.5
