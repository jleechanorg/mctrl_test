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
    Explanation: merged array = [1,2,3,4] and median is (2+3)/2 = 2.5.

Constraints:
    - nums1.length == m
    - nums2.length == n
    - 0 <= m <= 1000
    - 0 <= n <= 1000
    - 1 <= m + n <= 2000
    - -10^6 <= nums1[i], nums2[i] <= 10^6

Solution Approach:
    We use binary search on the smaller array to find the partition point.
    We partition both arrays such that:
    - Left half contains equal or one more element than right half
    - All elements in left half <= all elements in right half

    Time Complexity: O(log(min(m, n)))
    Space Complexity: O(1)
"""


def find_median_sorted_arrays(nums1: list[int], nums2: list[int]) -> float:
    """
    Find the median of two sorted arrays using binary search.

    Strategy: Binary search on the shorter array to find the correct partition.
    The key insight is that we partition both arrays such that:
    - Left halves combined have the same size as right halves (or differ by 1)
    - All elements in left halves <= all elements in right halves

    Args:
        nums1: First sorted array (can be empty)
        nums2: Second sorted array (can be empty)

    Returns:
        The median value as a float
    """
    # Ensure nums1 is the shorter array for optimization
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    low, high = 0, m

    while low <= high:
        # Partition indices
        partition1 = (low + high) // 2
        partition2 = (m + n + 1) // 2 - partition1

        # Get boundary values (use -inf/inf for edge cases)
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
            # Partition1 is too far right, move left
            high = partition1 - 1
        else:
            # Partition1 is too far left, move right
            low = partition1 + 1

    raise ValueError("Input arrays are not sorted or invalid")


def find_median_sorted_arrays_brute(nums1: list[int], nums2: list[int]) -> float:
    """
    Brute force solution by merging arrays (O(m+n) time, O(m+n) space).

    This is provided for comparison and testing purposes.
    """
    merged = []
    i, j = 0, 0

    while i < len(nums1) and j < len(nums2):
        if nums1[i] <= nums2[j]:
            merged.append(nums1[i])
            i += 1
        else:
            merged.append(nums2[j])
            j += 1

    # Append remaining elements
    merged.extend(nums1[i:])
    merged.extend(nums2[j:])

    n = len(merged)
    mid = n // 2
    if n % 2 == 0:
        return (merged[mid - 1] + merged[mid]) / 2
    return float(merged[mid])


if __name__ == "__main__":
    # Test cases
    test_cases = [
        ([1, 3], [2], 2.0),
        ([1, 2], [3, 4], 2.5),
        ([], [1], 1.0),
        ([], [1, 2, 3], 2.0),
        ([1], [2, 3, 4], 2.5),
        ([1, 3, 5, 7, 9], [2, 4, 6, 8, 10], 5.5),
        ([1, 1, 1], [1, 1, 1], 1.0),
        ([1], [1], 1.0),
        ([2], [], 2.0),
        ([], [2], 2.0),
    ]

    print("Running tests...")
    for nums1, nums2, expected in test_cases:
        result = find_median_sorted_arrays(nums1, nums2)
        result_brute = find_median_sorted_arrays_brute(nums1, nums2)
        assert result == expected, f"Failed: {nums1}, {nums2} -> {result}, expected {expected}"
        assert result_brute == expected, f"Brute failed: {nums1}, {nums2} -> {result_brute}, expected {expected}"
        print(f"  PASS: {nums1}, {nums2} -> {result}")

    print("All tests passed!")
