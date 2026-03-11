"""LRU Cache - LeetCode Hard

Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.
Uses a doubly linked list + hash map for O(1) get and put operations.
"""


class Node:
    __slots__ = ("key", "val", "prev", "next")

    def __init__(self, key: int = 0, val: int = 0) -> None:
        self.key = key
        self.val = val
        self.prev: Node | None = None
        self.next: Node | None = None


class LRUCache:
    def __init__(self, capacity: int) -> None:
        self.cap = capacity
        self.cache: dict[int, Node] = {}
        # Sentinel nodes
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
            if len(self.cache) >= self.cap:
                lru = self.tail.prev
                self._remove(lru)
                del self.cache[lru.key]
            node = Node(key, value)
            self.cache[key] = node
            self._add_to_front(node)


# --- Tests ---

def test_example_1() -> None:
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


def test_capacity_one() -> None:
    cache = LRUCache(1)
    cache.put(1, 10)
    assert cache.get(1) == 10
    cache.put(2, 20)       # evicts key 1
    assert cache.get(1) == -1
    assert cache.get(2) == 20


def test_update_existing_key() -> None:
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.put(1, 10)       # update key 1, makes it most recent
    cache.put(3, 3)        # evicts key 2 (LRU)
    assert cache.get(1) == 10
    assert cache.get(2) == -1
    assert cache.get(3) == 3


def test_get_refreshes_order() -> None:
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.get(1)           # refreshes key 1
    cache.put(3, 3)        # evicts key 2 (now LRU)
    assert cache.get(1) == 1
    assert cache.get(2) == -1


def test_get_missing_key() -> None:
    cache = LRUCache(3)
    assert cache.get(999) == -1


def test_large_capacity() -> None:
    cache = LRUCache(1000)
    for i in range(1000):
        cache.put(i, i * 2)
    for i in range(1000):
        assert cache.get(i) == i * 2
    # Adding one more evicts key 0
    cache.put(1000, 2000)
    assert cache.get(0) == -1
    assert cache.get(1000) == 2000


if __name__ == "__main__":
    test_example_1()
    test_capacity_one()
    test_update_existing_key()
    test_get_refreshes_order()
    test_get_missing_key()
    test_large_capacity()
    print("All tests passed!")
