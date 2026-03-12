"""
Median of Two Sorted Arrays - LeetCode #4 (Hard)

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

Constraints:
    nums1.length == m
    nums2.length == n
    0 <= m <= 1000
    0 <= n <= 1000
    1 <= m + n <= 2000
    -10^6 <= nums1[i], nums2[i] <= 10^6
"""
from __future__ import annotations


def find_median_sorted_arrays(nums1: list[int], nums2: list[int]) -> float:
    """
    Find the median of two sorted arrays.

    Uses binary search on the shorter array to achieve O(log(min(m, n))) time.
    The idea is to partition both arrays such that:
    - Left halves combined = Right halves combined
    - All elements in left halves <= all elements in right halves

    Args:
        nums1: First sorted array (can be empty)
        nums2: Second sorted array (can be empty)

    Returns:
        The median value as a float

    Time Complexity: O(log(min(m, n)))
    Space Complexity: O(1)
    """
    # Ensure nums1 is the shorter array for optimal binary search
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    low, high = 0, m

    while low <= high:
        # Partition point in nums1
        partition1 = (low + high) // 2
        # Partition point in nums2 (remaining elements)
        partition2 = (m + n + 1) // 2 - partition1

        # Get boundary values
        # maxLeft1: max value in left partition of nums1 (or -inf if empty)
        max_left1 = float('-inf') if partition1 == 0 else nums1[partition1 - 1]
        # minRight1: min value in right partition of nums1 (or inf if empty)
        min_right1 = float('inf') if partition1 == m else nums1[partition1]

        # maxLeft2: max value in left partition of nums2 (or -inf if empty)
        max_left2 = float('-inf') if partition2 == 0 else nums2[partition2 - 1]
        # minRight2: min value in right partition of nums2 (or inf if empty)
        min_right2 = float('inf') if partition2 == n else nums2[partition2]

        # Check if partitions are correct
        if max_left1 <= min_right2 and max_left2 <= min_right1:
            # Found correct partition
            if (m + n) % 2 == 0:
                # Even total length: average of two middle elements
                return (max(max_left1, max_left2) + min(min_right1, min_right2)) / 2
            else:
                # Odd total length: middle element is max of left partitions
                return float(max(max_left1, max_left2))
        elif max_left1 > min_right2:
            # Too far right in nums1, move left
            high = partition1 - 1
        else:
            # Too far left in nums1, move right
            low = partition1 + 1

    raise ValueError("Input arrays are not valid")


def find_median_sorted_arrays_brute(nums1: list[int], nums2: list[int]) -> float:
    """
    Brute force solution: merge arrays and find median.

    This is O(m + n) time but easier to understand as a reference.

    Args:
        nums1: First sorted array
        nums2: Second sorted array

    Returns:
        The median value as a float

    Time Complexity: O(m + n)
    Space Complexity: O(m + n)
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

    # Append remaining elements
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
    print(find_median_sorted_arrays([1, 2], [3]))  # 2.0
    print(find_median_sorted_arrays([], [1]))  # 1.0
    print(find_median_sorted_arrays([], [2, 3]))  # 2.5
