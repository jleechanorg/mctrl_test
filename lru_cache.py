"""LeetCode 146 - LRU Cache

Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.

Implement the LRUCache class:
- LRUCache(int capacity) Initialize the LRU cache with positive size capacity.
- int get(int key) Return the value of the key if the key exists, otherwise return -1.
- void put(int key, int value) Update the value of the key if the key exists.
  Otherwise, add the key-value pair to the cache. If the number of keys exceeds
  the capacity from this operation, evict the least recently used key.

The functions get and put must each run in O(1) average time complexity.
"""


class Node:
    """Doubly linked list node."""
    __slots__ = ('key', 'val', 'prev', 'next')

    def __init__(self, key: int = 0, val: int = 0):
        self.key = key
        self.val = val
        self.prev: 'Node | None' = None
        self.next: 'Node | None' = None


class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.cache: dict[int, Node] = {}
        # Sentinel head/tail to avoid null checks
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
            if len(self.cache) == self.cap:
                # Evict LRU (node just before tail sentinel)
                lru = self.tail.prev
                self._remove(lru)
                del self.cache[lru.key]
            node = Node(key, value)
            self.cache[key] = node
            self._add_to_front(node)
