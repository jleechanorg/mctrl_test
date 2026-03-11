"""Tests for LRU Cache implementation."""

from lru_cache import LRUCache


def test_example_1():
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


def test_capacity_one():
    cache = LRUCache(1)
    cache.put(1, 10)
    assert cache.get(1) == 10
    cache.put(2, 20)       # evicts key 1
    assert cache.get(1) == -1
    assert cache.get(2) == 20


def test_update_existing_key():
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.put(1, 10)       # update key 1, makes it most recent
    cache.put(3, 3)        # evicts key 2 (LRU)
    assert cache.get(1) == 10
    assert cache.get(2) == -1
    assert cache.get(3) == 3


def test_get_refreshes_order():
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.get(1)           # refreshes key 1
    cache.put(3, 3)        # evicts key 2 (now LRU)
    assert cache.get(1) == 1
    assert cache.get(2) == -1


def test_get_missing_key():
    cache = LRUCache(3)
    assert cache.get(999) == -1


def test_large_capacity():
    cache = LRUCache(1000)
    for i in range(1000):
        cache.put(i, i * 2)
    for i in range(1000):
        assert cache.get(i) == i * 2
    cache.put(1000, 2000)
    assert cache.get(0) == -1
    assert cache.get(1000) == 2000
