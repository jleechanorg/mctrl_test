"""
Median of Two Sorted Arrays - LeetCode Hard

Given two sorted arrays nums1 and nums2 of size m and n respectively,
return the median of the two sorted arrays.

The overall run time complexity should be O(log(min(m, n))).

Example 1:
    Input: nums1 = [1,3], nums2 = [2]
    Output: 2.00000
    Explanation: merged array = [1,2,3] and median is 2.

Example 2:
    Input: nums1 = [1,2], nums2 = [3,4]
    Output: 2.50000
    Explanation: merged array = [1,2,3,4] and median is (2 + 3) / 2 = 2.5.

Constraints:
    nums1.length == m
    nums2.length == n
    0 <= m <= 1000
    0 <= n <= 1000
    1 <= m + n <= 2000
    -10^6 <= nums1[i], nums2[i] <= 10^6

Solution Approach:
    Binary Search on the shorter array to find the correct partition.
    We partition both arrays such that:
    - Left half contains all elements <= right half
    - Left half size = right half size (or differs by 1 for odd total)

Time Complexity: O(log(min(m, n)))
Space Complexity: O(1) - only using constant extra space
"""
from __future__ import annotations


def find_median_sorted_arrays(nums1: list[int], nums2: list[int]) -> float:
    """
    Find the median of two sorted arrays using binary search.

    Strategy:
    - Ensure nums1 is the shorter array for efficiency
    - Binary search on nums1 to find partition point
    - Validate partition satisfies: left_max <= right_min

    Args:
        nums1: First sorted array
        nums2: Second sorted array

    Returns:
        Median value as a float

    Examples:
        >>> find_median_sorted_arrays([1, 3], [2])
        2.0
        >>> find_median_sorted_arrays([1, 2], [3, 4])
        2.5
    """
    # Ensure nums1 is the shorter array for binary search efficiency
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    low, high = 0, m

    while low <= high:
        # Partition position in nums1
        partition1 = (low + high) // 2
        # Partition position in nums2 (remaining elements)
        partition2 = (m + n + 1) // 2 - partition1

        # Get boundary values
        # For left partition: max left value
        # For right partition: min right value
        left1 = float('-inf') if partition1 == 0 else nums1[partition1 - 1]
        right1 = float('inf') if partition1 == m else nums1[partition1]

        left2 = float('-inf') if partition2 == 0 else nums2[partition2 - 1]
        right2 = float('inf') if partition2 == n else nums2[partition2]

        # Check if partition is correct
        if left1 <= right2 and left2 <= right1:
            # Found correct partition
            if (m + n) % 2 == 0:
                return (max(left1, left2) + min(right1, right2)) / 2
            else:
                return float(max(left1, left2))
        elif left1 > right2:
            # Too far right in nums1, move left
            high = partition1 - 1
        else:
            # Too far left in nums1, move right
            low = partition1 + 1

    raise ValueError("Input arrays are not valid")


if __name__ == "__main__":
    # Example usage
    print(find_median_sorted_arrays([1, 3], [2]))  # Output: 2.0
    print(find_median_sorted_arrays([1, 2], [3, 4]))  # Output: 2.5
