"""LRU Cache - LeetCode Hard

Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.

Uses a doubly linked list + hash map for O(1) get and put operations.
"""
from __future__ import annotations


class Node:
    __slots__ = ("key", "val", "prev", "next")

    def __init__(self, key: int = 0, val: int = 0) -> None:
        self.key = key
        self.val = val
        self.prev: Node | None = None
        self.next: Node | None = None


class LRUCache:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.cache: dict[int, Node] = {}
        # Sentinel nodes to avoid edge cases
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node: Node) -> None:
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add_to_front(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            node = self.cache[key]
            node.val = value
            self._remove(node)
            self._add_to_front(node)
        else:
            if len(self.cache) >= self.capacity:
                # Evict LRU (node before tail sentinel)
                lru = self.tail.prev
                self._remove(lru)
                del self.cache[lru.key]
            node = Node(key, value)
            self.cache[key] = node
            self._add_to_front(node)


# --------------- Tests ---------------

def test_example_1() -> None:
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == 1
    cache.put(3, 3)  # evicts key 2
    assert cache.get(2) == -1
    cache.put(4, 4)  # evicts key 1
    assert cache.get(1) == -1
    assert cache.get(3) == 3
    assert cache.get(4) == 4


def test_overwrite_existing_key() -> None:
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(1, 10)
    assert cache.get(1) == 10
    assert len(cache.cache) == 1


def test_capacity_one() -> None:
    cache = LRUCache(1)
    cache.put(1, 1)
    cache.put(2, 2)  # evicts 1
    assert cache.get(1) == -1
    assert cache.get(2) == 2


def test_get_promotes_to_most_recent() -> None:
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.get(1)      # promotes key 1
    cache.put(3, 3)   # should evict key 2 (LRU), not key 1
    assert cache.get(2) == -1
    assert cache.get(1) == 1
    assert cache.get(3) == 3


def test_put_existing_promotes() -> None:
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.put(1, 10)   # update key 1 — promotes it
    cache.put(3, 3)    # should evict key 2
    assert cache.get(2) == -1
    assert cache.get(1) == 10


def test_get_nonexistent() -> None:
    cache = LRUCache(3)
    assert cache.get(999) == -1


if __name__ == "__main__":
    test_example_1()
    test_overwrite_existing_key()
    test_capacity_one()
    test_get_promotes_to_most_recent()
    test_put_existing_promotes()
    test_get_nonexistent()
    print("All tests passed!")
