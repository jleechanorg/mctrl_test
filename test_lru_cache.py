"""Tests for LRU Cache (LeetCode 146)."""

import pytest
from lru_cache import LRUCache


class TestLRUCacheLeetCodeExample:
    """The example from the LeetCode problem statement."""

    def test_leetcode_example_1(self):
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        assert cache.get(1) == 1
        cache.put(3, 3)        # evicts key 2
        assert cache.get(2) == -1
        cache.put(4, 4)        # evicts key 1
        assert cache.get(1) == -1
        assert cache.get(3) == 3
        assert cache.get(4) == 4


class TestGetMiss:
    def test_get_nonexistent_key(self):
        cache = LRUCache(2)
        assert cache.get(99) == -1

    def test_get_after_eviction(self):
        cache = LRUCache(1)
        cache.put(1, 10)
        cache.put(2, 20)  # evicts 1
        assert cache.get(1) == -1
        assert cache.get(2) == 20


class TestPutUpdate:
    def test_update_existing_key(self):
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(1, 10)
        assert cache.get(1) == 10

    def test_update_refreshes_usage(self):
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.put(1, 10)    # refreshes key 1
        cache.put(3, 3)     # should evict key 2 (LRU), not key 1
        assert cache.get(1) == 10
        assert cache.get(2) == -1
        assert cache.get(3) == 3


class TestEvictionOrder:
    def test_get_refreshes_usage(self):
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.get(1)         # refreshes key 1
        cache.put(3, 3)      # should evict key 2
        assert cache.get(1) == 1
        assert cache.get(2) == -1

    def test_sequential_evictions(self):
        cache = LRUCache(3)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.put(3, 3)
        cache.put(4, 4)  # evicts 1
        cache.put(5, 5)  # evicts 2
        assert cache.get(1) == -1
        assert cache.get(2) == -1
        assert cache.get(3) == 3
        assert cache.get(4) == 4
        assert cache.get(5) == 5


class TestCapacityOne:
    def test_capacity_one(self):
        cache = LRUCache(1)
        cache.put(1, 1)
        assert cache.get(1) == 1
        cache.put(2, 2)
        assert cache.get(1) == -1
        assert cache.get(2) == 2


class TestLargerWorkload:
    def test_many_operations(self):
        cache = LRUCache(3)
        for i in range(100):
            cache.put(i, i * 10)
        # Only last 3 should remain
        for i in range(97):
            assert cache.get(i) == -1
        for i in range(97, 100):
            assert cache.get(i) == i * 10
