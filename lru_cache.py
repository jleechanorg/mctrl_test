"""
LeetCode Problem 146: LRU Cache

Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.

Implement the LRUCache class:
- LRUCache(int capacity) Initialize the LRU cache with positive size capacity
- int get(int key) Return the value of the key if it exists, otherwise return -1
- void put(int key, int value) Update the value of the key if it exists. Otherwise add the key-value pair.
  If the number of keys exceeds capacity, evict the least recently used key.

Must run in O(1) average time complexity.
"""

from __future__ import annotations


class DNode:
    """Doubly linked list node for LRU Cache."""

    def __init__(self, key: int = 0, value: int = 0):
        self.key = key
        self.value = value
        self.prev: DNode | None = None
        self.next: DNode | None = None


class LRUCache:
    """
    LRU Cache implementation using custom doubly-linked list.

    Time Complexity: O(1) for all operations (get, put)
    Space Complexity: O(capacity)
    """

    def __init__(self, capacity: int):
        """
        Initialize the LRU cache with the given capacity.

        Args:
            capacity: Positive integer representing the maximum number of keys
        """
        self.capacity = capacity
        self.cache: dict[int, DNode] = {}

        # Dummy head and tail nodes for easier manipulation
        self.head = DNode()
        self.tail = DNode()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: DNode) -> None:
        """Remove a node from the linked list. O(1)"""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_head(self, node: DNode) -> None:
        """Add a node right after head (most recently used). O(1)"""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def _move_to_head(self, node: DNode) -> None:
        """Move an existing node to the head (most recently used). O(1)"""
        self._remove(node)
        self._add_to_head(node)

    def get(self, key: int) -> int:
        """
        Get the value of the key if it exists, otherwise return -1.

        Args:
            key: The key to look up

        Returns:
            The value if key exists, -1 otherwise
        """
        if key in self.cache:
            node = self.cache[key]
            self._move_to_head(node)
            return node.value
        return -1

    def put(self, key: int, value: int) -> None:
        """
        Update the value of the key if it exists. Otherwise add the key-value pair.
        If the number of keys exceeds capacity, evict the least recently used key.

        Args:
            key: The key to insert or update
            value: The value to associate with the key
        """
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            # Create new node
            node = DNode(key, value)
            self.cache[key] = node
            self._add_to_head(node)

            # Evict if over capacity
            if len(self.cache) > self.capacity:
                # Remove least recently used (node before tail)
                lru_node = self.tail.prev
                self._remove(lru_node)
                del self.cache[lru_node.key]

    def __len__(self) -> int:
        """Return the number of items in the cache."""
        return len(self.cache)

    def __repr__(self) -> str:
        """Return string representation of cache contents."""
        items = []
        node = self.head.next
        while node != self.tail:
            items.append(f"{node.key}:{node.value}")
            node = node.next
        return f"LRUCache([{', '.join(items)}], capacity={self.capacity})"
