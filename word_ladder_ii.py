from __future__ import annotations

from collections import defaultdict


def find_ladders(begin_word: str, end_word: str, word_list: list[str]) -> list[list[str]]:
    """Return all shortest transformation sequences from begin_word to end_word."""
    if begin_word == end_word:
        return [[begin_word]]

    words = set(word_list)
    if end_word not in words:
        return []

    words.add(begin_word)

    # Build wildcard pattern adjacency, e.g. h*t -> [hot, hit]
    pattern_map: dict[str, list[str]] = defaultdict(list)
    word_len = len(begin_word)
    for word in words:
        if len(word) != word_len:
            continue
        for i in range(word_len):
            pattern = word[:i] + "*" + word[i + 1 :]
            pattern_map[pattern].append(word)

    parents: dict[str, set[str]] = defaultdict(set)
    current_level = {begin_word}
    visited = {begin_word}
    found_end = False

    while current_level and not found_end:
        next_level: set[str] = set()
        level_seen: set[str] = set()

        for word in current_level:
            for i in range(word_len):
                pattern = word[:i] + "*" + word[i + 1 :]
                for neighbor in pattern_map.get(pattern, []):
                    if neighbor in visited:
                        continue

                    if neighbor not in level_seen:
                        level_seen.add(neighbor)
                        next_level.add(neighbor)

                    parents[neighbor].add(word)
                    if neighbor == end_word:
                        found_end = True

        visited.update(level_seen)
        current_level = next_level

    if not found_end:
        return []

    results: list[list[str]] = []

    def backtrack(word: str, path: list[str]) -> None:
        if word == begin_word:
            results.append(path[::-1])
            return
        for parent in parents[word]:
            path.append(parent)
            backtrack(parent, path)
            path.pop()

    backtrack(end_word, [end_word])
    return results
