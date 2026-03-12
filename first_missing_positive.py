"""
LeetCode 41 - First Missing Positive

Given an unsorted integer array nums, return the smallest missing positive integer.

Approach:
- Use O(n) time and O(1) space by placing each number in its correct position
- For each number in range [1, n], swap it to index (value - 1) if possible
- After placement, scan to find first index where nums[i] != i + 1
- If all positions are correct, answer is n + 1

Time Complexity: O(n) - each element is moved at most once
Space Complexity: O(1) - in-place modification
"""


def first_missing_positive(nums: list[int]) -> int:
    """
    Find the smallest missing positive integer.

    Args:
        nums: List of unsorted integers (can contain duplicates, negatives, zeros)

    Returns:
        The smallest missing positive integer

    Example:
        >>> first_missing_positive([1, 2, 0])
        3
        >>> first_missing_positive([3, 4, -1, 1])
        2
        >>> first_missing_positive([7, 8, 9, 11, 12])
        1
    """
    n = len(nums)

    # Place each number in its correct position: nums[i] should be i + 1
    for i in range(n):
        # Keep swapping until nums[i] is in correct position [1, n] and not duplicate
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            # Swap nums[i] with nums[nums[i] - 1]
            correct_idx = nums[i] - 1
            nums[i], nums[correct_idx] = nums[correct_idx], nums[i]

    # Find first position where nums[i] != i + 1
    for i in range(n):
        if nums[i] != i + 1:
            return i + 1

    # If all positions are correct, answer is n + 1
    return n + 1


if __name__ == "__main__":
    # Test cases
    test_cases = [
        ([1, 2, 0], 3),
        ([3, 4, -1, 1], 2),
        ([7, 8, 9, 11, 12], 1),
        ([1, 1, 0, -1, 2], 3),
        ([], 1),
        ([1], 2),
        ([2], 1),
        ([1, 2, 3, 4, 5], 6),
        ([5, 4, 3, 2, 1], 6),
    ]

    for nums, expected in test_cases:
        result = first_missing_positive(nums.copy())  # copy to avoid mutation in print
        print(f"nums={nums}, expected={expected}, got={result}, pass={result == expected}")
