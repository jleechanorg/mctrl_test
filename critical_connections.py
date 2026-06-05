"""
LeetCode 1192: Critical Connections in a Network

There are n servers numbered from 0 to n - 1 connected by undirected
server connections forming a network. A connection (a, b) is critical
if the network becomes disconnected when removed.

Find all critical connections in the network in any order.

Example:
    Input: n = 4, connections = [[0,1],[1,2],[2,0],[1,3]]
    Output: [[1,3]]

Solution:
    Use Tarjan's algorithm for finding bridges in a graph.
    - Use DFS to assign discovery time (disc) and low link value to each node
    - A connection (u, v) is a bridge if low[v] > disc[u] (i.e., no back edge
      from v's subtree to u or above)

Time Complexity: O(V + E) - single DFS traversal
Space Complexity: O(V + E) - for adjacency list and recursion stack
"""

from typing import List


def critical_connections(n: int, connections: List[List[int]]) -> List[List[int]]:
    """
    Find all critical connections (bridges) in the network.

    Args:
        n: Number of servers (nodes)
        connections: List of [a, b] connections between servers

    Returns:
        List of critical connections that would disconnect the network if removed
    """
    # Build adjacency list
    graph = [[] for _ in range(n)]
    for a, b in connections:
        graph[a].append(b)
        graph[b].append(a)

    # disc[u] = discovery time of node u
    # low[u] = lowest discovery time reachable from u (including back edges)
    disc = [-1] * n
    low = [-1] * n
    result = []
    time = [0]  # Using list to allow mutation in nested function

    def dfs(u: int, parent: int) -> None:
        """DFS to find bridges using Tarjan's algorithm."""
        disc[u] = low[u] = time[0]
        time[0] += 1

        for v in graph[u]:
            if disc[v] == -1:  # Not visited
                dfs(v, u)
                low[u] = min(low[u], low[v])

                # Bridge condition: no back edge from v's subtree to u
                if low[v] > disc[u]:
                    result.append([u, v])
            elif v != parent:  # Back edge (not to immediate parent)
                low[u] = min(low[u], disc[v])

    # Run DFS from all components (in case graph is disconnected)
    for i in range(n):
        if disc[i] == -1:
            dfs(i, -1)

    return result


# Test cases
if __name__ == "__main__":
    # Test 1: Basic example
    n1 = 4
    connections1 = [[0, 1], [1, 2], [2, 0], [1, 3]]
    result1 = critical_connections(n1, connections1)
    print(f"Test 1: {result1}")  # Expected: [[1, 3]]

    # Test 2: No critical connections
    n2 = 3
    connections2 = [[0, 1], [1, 2], [2, 0]]
    result2 = critical_connections(n2, connections2)
    print(f"Test 2: {result2}")  # Expected: []

    # Test 3: Linear chain
    n3 = 4
    connections3 = [[0, 1], [1, 2], [2, 3]]
    result3 = critical_connections(n3, connections3)
    print(f"Test 3: {result3}")  # Expected: [[0, 1], [1, 2], [2, 3]]
