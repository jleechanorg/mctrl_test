"""
LeetCode #4: Median of Two Sorted Arrays

Given two sorted arrays nums1 and nums2 of size m and n respectively, return
the median of the two sorted arrays.

The overall run time complexity should be O(log(m + n)).

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
    Find the median of two sorted arrays in O(log(min(m, n))) time.

    Strategy: Use binary search on the shorter array to find the partition
    point that correctly divides both arrays into two halves with equal
    total elements. The median is then computed from the partition boundaries.

    Approach:
    1. Ensure nums1 is the shorter array (optimizes binary search)
    2. Binary search on nums1 to find the correct partition
    3. At the correct partition:
       - left1 <= right2 (all elements in left part of nums1 <= all in right part of nums2)
       - left2 <= right1 (all elements in left part of nums2 <= all in right part of nums1)
    4. If total length is even: median = (max(left1, left2) + min(right1, right2)) / 2
       If total length is odd: median = max(left1, left2)

    Time Complexity: O(log(min(m, n))) - binary search on smaller array
    Space Complexity: O(1) - only using a few variables

    Args:
        nums1: First sorted array (can be empty)
        nums2: Second sorted array (can be empty)

    Returns:
        The median of the two sorted arrays
    """
    # Ensure nums1 is the shorter array for optimal binary search
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    low, high = 0, m

    while low <= high:
        # Partition positions
        partition1 = (low + high) // 2
        partition2 = (m + n + 1) // 2 - partition1

        # Get boundary values (use -inf for empty partitions)
        max_left1 = float('-inf') if partition1 == 0 else nums1[partition1 - 1]
        min_right1 = float('inf') if partition1 == m else nums1[partition1]

        max_left2 = float('-inf') if partition2 == 0 else nums2[partition2 - 1]
        min_right2 = float('inf') if partition2 == n else nums2[partition2]

        # Check if partition is correct
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
    # Example tests
    print(find_median_sorted_arrays([1, 3], [2]))  # 2.0
    print(find_median_sorted_arrays([1, 2], [3, 4]))  # 2.5
    print(find_median_sorted_arrays([1, 2], [3]))  # 2.0
    print(find_median_sorted_arrays([], [1]))  # 1.0
    print(find_median_sorted_arrays([2], []))  # 2.0
