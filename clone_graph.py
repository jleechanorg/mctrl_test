from __future__ import annotations
from collections import deque


class Node:
    """Node class for the graph representation."""

    def __init__(self, val: int = 0, neighbors: list[Node] | None = None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []

    def __repr__(self) -> str:
        return f"Node({self.val})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return False
        return self.val == other.val

    def __hash__(self) -> int:
        return hash(self.val)


def clone_graph(root: Node | None) -> Node | None:
    """
    Return a deep copy of the graph starting from the given node.

    Uses BFS with a hashmap to track visited nodes and their clones.

    Args:
        root: The starting node of the graph to clone.

    Returns:
        A deep copy of the graph, or None if root is None.
    """
    if root is None:
        return None

    # Hashmap to store visited nodes: original -> clone
    visited: dict[int, Node] = {}

    # BFS queue
    queue: deque[Node] = deque([root])

    # Create clone of root node
    visited[root.val] = Node(root.val)

    while queue:
        node = queue.popleft()
        current_clone = visited[node.val]

        # Process all neighbors
        for neighbor in node.neighbors:
            if neighbor.val not in visited:
                # Create clone of neighbor and add to queue
                visited[neighbor.val] = Node(neighbor.val)
                queue.append(neighbor)

            # Add cloned neighbor to current node's neighbors
            current_clone.neighbors.append(visited[neighbor.val])

    return visited[root.val]


def clone_graph_dfs(root: Node | None) -> Node | None:
    """
    Return a deep copy of the graph using DFS approach.

    Args:
        root: The starting node of the graph to clone.

    Returns:
        A deep copy of the graph, or None if root is None.
    """
    if root is None:
        return None

    visited: dict[int, Node] = {}

    def dfs(node: Node) -> Node:
        if node.val in visited:
            return visited[node.val]

        # Create clone
        clone = Node(node.val)
        visited[node.val] = clone

        # Clone all neighbors
        for neighbor in node.neighbors:
            clone.neighbors.append(dfs(neighbor))

        return clone

    return dfs(root)


def build_graph(adj_list: list[list[int]]) -> Node | None:
    """
    Build a graph from adjacency list representation.

    Args:
        adj_list: List of lists where adj_list[i] contains neighbors of node i.

    Returns:
        The root node (node 0) of the constructed graph.
    """
    if not adj_list:
        return None

    n = len(adj_list)
    nodes = [Node(i) for i in range(n)]

    for i in range(n):
        for neighbor_idx in adj_list[i]:
            nodes[i].neighbors.append(nodes[neighbor_idx])

    return nodes[0]


def graph_to_adj_list(root: Node | None) -> list[list[int]]:
    """
    Convert a graph to adjacency list representation for comparison.

    Args:
        root: The root node of the graph.

    Returns:
        Adjacency list representation.
    """
    if root is None:
        return []

    # First, collect all nodes via BFS to get the total count
    all_nodes: list[Node] = []
    visited: dict[int, bool] = {}
    queue: deque[Node] = deque([root])
    visited[root.val] = True

    while queue:
        node = queue.popleft()
        all_nodes.append(node)

        for neighbor in node.neighbors:
            if neighbor.val not in visited:
                visited[neighbor.val] = True
                queue.append(neighbor)

    # Build adjacency list in node index order
    max_val = max(node.val for node in all_nodes)
    result: list[list[int]] = [[] for _ in range(max_val + 1)]

    for node in all_nodes:
        result[node.val] = [neighbor.val for neighbor in node.neighbors]

    return result


if __name__ == "__main__":
    # Test with example: [[1,2],[0,2],[0,1]]
    adj_list = [[1, 2], [0, 2], [0, 1]]
    root = build_graph(adj_list)
    cloned = clone_graph(root)

    print("Original:", adj_list)
    print("Cloned:", graph_to_adj_list(cloned))
