"""
Median of Two Sorted Arrays - LeetCode Hard Problem

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
    Explanation: merged array = [1,2,3,4] and median is (2+3)/2 = 2.5.

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

    Strategy:
    - Ensure nums1 is the shorter array for optimization
    - Use binary search on the shorter array to find the correct partition
    - The partition should divide both arrays such that:
      - Left halves contain the smaller half of all elements
      - Right halves contain the larger half of all elements

    Time Complexity: O(log(min(m, n))) where m and n are array lengths
    Space Complexity: O(1) - only using a few variables

    Args:
        nums1: First sorted array
        nums2: Second sorted array

    Returns:
        The median of the two sorted arrays

    Raises:
        ValueError: If both arrays are empty
    """
    # Handle empty arrays
    if not nums1 and not nums2:
        raise ValueError("Cannot find median of two empty arrays")

    # Ensure nums1 is the shorter array for optimization
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    low, high = 0, m

    while low <= high:
        # Partition indices
        partition1 = (low + high) // 2
        partition2 = (m + n + 1) // 2 - partition1

        # Get boundary values
        # maxLeft1: maximum value in left partition of nums1
        # minRight1: minimum value in right partition of nums1
        # maxLeft2: maximum value in left partition of nums2
        # minRight2: minimum value in right partition of nums2

        max_left1 = float('-inf') if partition1 == 0 else nums1[partition1 - 1]
        min_right1 = float('inf') if partition1 == m else nums1[partition1]
        max_left2 = float('-inf') if partition2 == 0 else nums2[partition2 - 1]
        min_right2 = float('inf') if partition2 == n else nums2[partition2]

        # Check if we found the correct partition
        if max_left1 <= min_right2 and max_left2 <= min_right1:
            # Found the correct partition
            if (m + n) % 2 == 0:
                # Even total length: average of two middle values
                return (max(max_left1, max_left2) + min(min_right1, min_right2)) / 2
            else:
                # Odd total length: middle value is max of left partitions
                return max(max_left1, max_left2)
        elif max_left1 > min_right2:
            # Too far right in nums1, move left
            high = partition1 - 1
        else:
            # Too far left in nums1, move right
            low = partition1 + 1

    raise ValueError("Input arrays are not valid")


# Alias for cleaner import
median = find_median_sorted_arrays


if __name__ == "__main__":
    # Example usage
    print(find_median_sorted_arrays([1, 3], [2]))  # Output: 2.0
    print(find_median_sorted_arrays([1, 2], [3, 4]))  # Output: 2.5
