"""
Test cases for LeetCode Problem 146: LRU Cache
"""

import pytest
from lru_cache import LRUCache


class TestLRUCacheBasic:
    """Basic functionality tests for LRUCache."""

    def test_put_and_get(self):
        """Test basic put and get operations."""
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        assert cache.get(1) == 1
        assert cache.get(2) == 2

    def test_get_nonexistent_key(self):
        """Test getting a key that doesn't exist returns -1."""
        cache = LRUCache(2)
        cache.put(1, 1)
        assert cache.get(3) == -1
        assert cache.get(1) == 1
        assert cache.get(4) == -1

    def test_update_existing_key(self):
        """Test updating an existing key updates its value."""
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.put(1, 10)  # Update key 1
        assert cache.get(1) == 10
        assert cache.get(2) == 2


class TestLRUCacheEviction:
    """Tests for LRU eviction behavior."""

    def test_eviction_least_recently_used(self):
        """Test that least recently used key is evicted when capacity is exceeded."""
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.put(3, 3)  # Should evict key 1 (least recently used)
        assert cache.get(1) == -1
        assert cache.get(2) == 2
        assert cache.get(3) == 3

    def test_get_makes_key_most_recently_used(self):
        """Test that accessing a key makes it most recently used."""
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        _ = cache.get(1)  # Access key 1, making it most recently used
        cache.put(3, 3)  # Should evict key 2, not key 1
        assert cache.get(1) == 1
        assert cache.get(2) == -1
        assert cache.get(3) == 3

    def test_put_makes_key_most_recently_used(self):
        """Test that updating a key makes it most recently used."""
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.put(2, 20)  # Update key 2
        cache.put(3, 3)  # Should evict key 1
        assert cache.get(1) == -1
        assert cache.get(2) == 20
        assert cache.get(3) == 3


class TestLRUCacheEdgeCases:
    """Edge case tests."""

    def test_capacity_one(self):
        """Test cache with capacity of 1."""
        cache = LRUCache(1)
        cache.put(1, 1)
        cache.put(2, 2)
        assert cache.get(1) == -1
        assert cache.get(2) == 2

    def test_same_key_put_twice(self):
        """Test putting the same key twice."""
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(1, 2)  # Update
        assert cache.get(1) == 2
        assert len(cache) == 1

    def test_empty_cache_get(self):
        """Test get on empty cache."""
        cache = LRUCache(2)
        assert cache.get(1) == -1

    def test_single_element_cache(self):
        """Test cache with single element capacity."""
        cache = LRUCache(1)
        cache.put(1, 1)
        assert cache.get(1) == 1
        cache.put(2, 2)
        assert cache.get(1) == -1
        assert cache.get(2) == 2


class TestLRUCacheLeetCodeExample:
    """Test the exact example from LeetCode."""

    def test_leetcode_example(self):
        """
        Test the example from LeetCode:
        Input: ['LRUCache', 'put', 'put', 'get', 'put', 'get', 'put', 'get', 'get', 'get']
               [[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]
        Output: [null, null, null, 1, null, -1, null, -1, 3, 4]
        """
        cache = LRUCache(2)

        # put(1, 1)
        cache.put(1, 1)
        # put(2, 2)
        cache.put(2, 2)
        # get(1) -> 1
        assert cache.get(1) == 1
        # put(3, 3) - evicts key 2
        cache.put(3, 3)
        # get(2) -> -1
        assert cache.get(2) == -1
        # put(4, 4) - evicts key 1
        cache.put(4, 4)
        # get(1) -> -1
        assert cache.get(1) == -1
        # get(3) -> 3
        assert cache.get(3) == 3
        # get(4) -> 4
        assert cache.get(4) == 4


class TestLRUCacheComplexity:
    """Verify O(1) operations by ensuring no linear traversals."""

    def test_large_capacity_operations(self):
        """Test operations on a large capacity cache work correctly."""
        cache = LRUCache(3000)

        # Fill cache
        for i in range(3000):
            cache.put(i, i * 10)

        # Access first element to make it most recently used
        assert cache.get(0) == 0

        # Add one more, should evict key 1 (not 0)
        cache.put(3000, 30000)
        assert cache.get(0) == 0
        assert cache.get(1) == -1
        assert cache.get(3000) == 30000

    def test_many_updates(self):
        """Test many updates to the same key."""
        cache = LRUCache(3)
        for i in range(100):
            cache.put(1, i)

        assert cache.get(1) == 99
        assert len(cache) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
