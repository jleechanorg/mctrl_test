"""Word Search II solver module.

LeetCode 212 (Hard): Word Search II
-----------------------------------
Given an ``m x n`` board of characters and a list of strings ``words``, return
all words from ``words`` that can be formed by traversing adjacent board cells.
Adjacency is horizontal or vertical (4-directional). A single board cell cannot
be reused in a single word path.

This module provides two solvers:
1. ``find_words_optimized``: Trie + DFS with prefix pruning and in-place
   dedup optimization.
2. ``find_words_baseline``: Slower per-word DFS baseline that is useful for
   correctness checks and small random sanity tests.

The module also includes:
- board formatting helpers,
- random test-case generation utilities,
- complexity notes,
- a CLI entrypoint for running sample or random comparisons.

Typical usage:

>>> board = [
...     ["o", "a", "a", "n"],
...     ["e", "t", "a", "e"],
...     ["i", "h", "k", "r"],
...     ["i", "f", "l", "v"],
... ]
>>> words = ["oath", "pea", "eat", "rain"]
>>> sorted(find_words_optimized(board, words))
['eat', 'oath']

Design constraints:
- Inputs are treated as immutable from the caller's perspective.
- Outputs are deduplicated regardless of duplicate words in input.
- Empty board or empty words returns an empty list.
"""

from __future__ import annotations

import argparse
import random
import string
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

Board = List[List[str]]
WordList = Sequence[str]


@dataclass(frozen=True)
class ComplexityNote:
    """Holds complexity notes for reporting/documentation."""

    solver: str
    time: str
    space: str
    notes: str


COMPLEXITY_NOTES: Tuple[ComplexityNote, ...] = (
    ComplexityNote(
        solver="optimized (trie + dfs)",
        time="O(M*N*4^L) worst-case traversal, often much smaller with prefix pruning",
        space=(
            "O(total_chars_in_words) trie + O(L) recursion + O(k) result set, "
            "where L=max word length"
        ),
        notes=(
            "Build trie once, walk board once per start cell, and cut branches as soon "
            "as path is not a trie prefix."
        ),
    ),
    ComplexityNote(
        solver="baseline (per-word dfs)",
        time="O(W*M*N*4^L) in worst case",
        space="O(L) recursion stack + visited tracking per search",
        notes=(
            "Runs an independent DFS search for each unique word; easier to reason about "
            "but substantially slower when word list is large."
        ),
    ),
)


def board_to_string(board: Sequence[Sequence[str]]) -> str:
    """Render a board into a readable multiline string.

    Empty boards are rendered as ``<empty board>``.
    """
    if not board or not board[0]:
        return "<empty board>"
    return "\n".join(" ".join(row) for row in board)


def clone_board(board: Sequence[Sequence[str]]) -> Board:
    """Return a deep-ish clone (row copies) of a char board."""
    return [list(row) for row in board]


def normalize_board(board: Sequence[Sequence[str]]) -> Board:
    """Normalize and validate a board.

    Validation rules:
    - Board may be empty.
    - If non-empty, every row must have same length.
    - Every cell should be a 1-character string.

    Returns a cloned board so callers can mutate internally without touching input.
    """
    if not board:
        return []

    row_len = len(board[0])
    normalized: Board = []
    for r, row in enumerate(board):
        if len(row) != row_len:
            raise ValueError(f"Board is ragged at row {r}: expected {row_len}, got {len(row)}")
        out_row: List[str] = []
        for c, cell in enumerate(row):
            if not isinstance(cell, str) or len(cell) != 1:
                raise ValueError(
                    f"Board cell ({r}, {c}) must be a single character string, got {cell!r}"
                )
            out_row.append(cell)
        normalized.append(out_row)
    return normalized


def normalize_words(words: WordList) -> List[str]:
    """Normalize word list by removing empties and preserving first occurrence order.

    Dedup is intentional because Word Search II expects unique outputs.
    """
    seen: Set[str] = set()
    out: List[str] = []
    for w in words:
        if not isinstance(w, str):
            raise ValueError(f"Word must be str, got {type(w)!r}")
        if not w:
            continue
        if w not in seen:
            seen.add(w)
            out.append(w)
    return out


def generate_random_board(
    rows: int,
    cols: int,
    *,
    alphabet: str = string.ascii_lowercase,
    rng: Optional[random.Random] = None,
) -> Board:
    """Generate a random board with characters from ``alphabet``."""
    if rows < 0 or cols < 0:
        raise ValueError("rows and cols must be >= 0")
    if not alphabet:
        raise ValueError("alphabet must not be empty")
    rr = rng or random.Random()
    return [[rr.choice(alphabet) for _ in range(cols)] for _ in range(rows)]


def _neighbors(r: int, c: int, rows: int, cols: int) -> Iterable[Tuple[int, int]]:
    """Yield 4-directional neighbors in-bounds."""
    if r > 0:
        yield r - 1, c
    if r + 1 < rows:
        yield r + 1, c
    if c > 0:
        yield r, c - 1
    if c + 1 < cols:
        yield r, c + 1


def _sample_words_from_board(
    board: Sequence[Sequence[str]],
    *,
    count: int,
    min_len: int,
    max_len: int,
    rng: random.Random,
) -> List[str]:
    """Generate valid words by random walks on board.

    This is useful for creating random test cases where at least some words are
    guaranteed to exist.
    """
    if not board or not board[0] or count <= 0:
        return []

    rows, cols = len(board), len(board[0])
    words: Set[str] = set()
    attempts = max(100, count * 30)

    for _ in range(attempts):
        start_r = rng.randrange(rows)
        start_c = rng.randrange(cols)
        target_len = rng.randint(max(1, min_len), max(min_len, max_len))

        path = [(start_r, start_c)]
        used = {(start_r, start_c)}
        chars = [board[start_r][start_c]]

        while len(chars) < target_len:
            r, c = path[-1]
            candidates = [(nr, nc) for nr, nc in _neighbors(r, c, rows, cols) if (nr, nc) not in used]
            if not candidates:
                break
            nr, nc = rng.choice(candidates)
            path.append((nr, nc))
            used.add((nr, nc))
            chars.append(board[nr][nc])

        if min_len <= len(chars) <= max_len:
            words.add("".join(chars))
            if len(words) >= count:
                break

    return list(words)


def generate_random_case(
    rows: int,
    cols: int,
    *,
    word_count: int,
    min_word_len: int = 2,
    max_word_len: int = 8,
    alphabet: str = "abcdefg",
    present_ratio: float = 0.6,
    seed: Optional[int] = None,
) -> Tuple[Board, List[str]]:
    """Create a random board and word list for experiments/tests.

    ``present_ratio`` controls how many candidate words should likely be present.
    The remainder are random synthetic words that may or may not exist.
    """
    if word_count < 0:
        raise ValueError("word_count must be >= 0")
    if not 0 <= present_ratio <= 1:
        raise ValueError("present_ratio must be in [0, 1]")

    rng = random.Random(seed)
    board = generate_random_board(rows, cols, alphabet=alphabet, rng=rng)

    guaranteed_n = int(round(word_count * present_ratio))
    random_n = max(0, word_count - guaranteed_n)

    present_words = _sample_words_from_board(
        board,
        count=guaranteed_n,
        min_len=min_word_len,
        max_len=max_word_len,
        rng=rng,
    )

    random_words: List[str] = []
    for _ in range(random_n):
        length = rng.randint(max(1, min_word_len), max(min_word_len, max_word_len))
        random_words.append("".join(rng.choice(alphabet) for _ in range(length)))

    words = normalize_words(present_words + random_words)
    return board, words


class TrieNode:
    """Trie node for optimized word search."""

    __slots__ = ("children", "word")

    def __init__(self) -> None:
        self.children: Dict[str, TrieNode] = {}
        self.word: Optional[str] = None


def build_trie(words: Sequence[str]) -> TrieNode:
    """Build a trie from words.

    Terminal nodes store the full word for O(1) retrieval when found.
    """
    root = TrieNode()
    for word in words:
        node = root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.word = word
    return root


def find_words_optimized(board: Sequence[Sequence[str]], words: WordList) -> List[str]:
    """Find all words using trie-guided DFS with prefix pruning.

    Returns a deduplicated list. Order is discovery order (not sorted).
    """
    grid = normalize_board(board)
    dict_words = normalize_words(words)
    if not grid or not grid[0] or not dict_words:
        return []

    rows, cols = len(grid), len(grid[0])
    root = build_trie(dict_words)
    found: List[str] = []

    def dfs(r: int, c: int, parent: TrieNode) -> None:
        ch = grid[r][c]
        node = parent.children.get(ch)
        if node is None:
            return

        # Found a word. Set to None to avoid duplicate additions if discovered
        # by another path.
        if node.word is not None:
            found.append(node.word)
            node.word = None

        grid[r][c] = "#"
        for nr, nc in _neighbors(r, c, rows, cols):
            next_ch = grid[nr][nc]
            if next_ch != "#" and next_ch in node.children:
                dfs(nr, nc, node)
        grid[r][c] = ch

        # Leaf pruning: if node has no remaining children and no word,
        # remove it from parent to reduce future branch work.
        if not node.children and node.word is None:
            parent.children.pop(ch, None)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] in root.children:
                dfs(r, c, root)

    return found


def _exists_word_on_board(grid: Board, word: str) -> bool:
    """Baseline helper: check whether one word exists on board via DFS."""
    if not grid or not grid[0]:
        return False
    if not word:
        return False

    rows, cols = len(grid), len(grid[0])

    # Quick rejection by character counts.
    available: Dict[str, int] = {}
    needed: Dict[str, int] = {}
    for row in grid:
        for ch in row:
            available[ch] = available.get(ch, 0) + 1
    for ch in word:
        needed[ch] = needed.get(ch, 0) + 1
    for ch, cnt in needed.items():
        if available.get(ch, 0) < cnt:
            return False

    target = list(word)
    visited = [[False] * cols for _ in range(rows)]

    def dfs(r: int, c: int, idx: int) -> bool:
        if grid[r][c] != target[idx]:
            return False
        if idx == len(target) - 1:
            return True

        visited[r][c] = True
        for nr, nc in _neighbors(r, c, rows, cols):
            if not visited[nr][nc] and dfs(nr, nc, idx + 1):
                visited[r][c] = False
                return True
        visited[r][c] = False
        return False

    first = target[0]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == first and dfs(r, c, 0):
                return True
    return False


def find_words_baseline(board: Sequence[Sequence[str]], words: WordList) -> List[str]:
    """Find all words with slower per-word DFS search.

    This baseline is intentionally simpler and typically slower than trie-based
    search, but acts as a trusted oracle for random correctness checks.
    """
    grid = normalize_board(board)
    dict_words = normalize_words(words)
    if not grid or not grid[0] or not dict_words:
        return []

    found: List[str] = []
    for word in dict_words:
        if _exists_word_on_board(grid, word):
            found.append(word)
    return found


def _run_sample_case() -> None:
    """Run and print canonical sample case."""
    board = [
        ["o", "a", "a", "n"],
        ["e", "t", "a", "e"],
        ["i", "h", "k", "r"],
        ["i", "f", "l", "v"],
    ]
    words = ["oath", "pea", "eat", "rain", "hike", "oat"]

    print("Sample board:")
    print(board_to_string(board))
    print(f"Words: {words}")

    baseline = sorted(find_words_baseline(board, words))
    optimized = sorted(find_words_optimized(board, words))

    print(f"Baseline:  {baseline}")
    print(f"Optimized: {optimized}")
    if baseline != optimized:
        raise SystemExit("Mismatch between baseline and optimized on sample case")


def _run_random_case(seed: int, rows: int, cols: int, words_n: int, show_board: bool) -> None:
    """Generate one random case and compare both solvers."""
    board, words = generate_random_case(
        rows,
        cols,
        word_count=words_n,
        min_word_len=2,
        max_word_len=7,
        seed=seed,
    )

    if show_board:
        print("Random board:")
        print(board_to_string(board))
    print(f"Random words ({len(words)}): {words}")

    baseline = sorted(find_words_baseline(board, words))
    optimized = sorted(find_words_optimized(board, words))

    print(f"Baseline found {len(baseline)} words")
    print(f"Optimized found {len(optimized)} words")

    if baseline != optimized:
        print(f"Baseline:  {baseline}")
        print(f"Optimized: {optimized}")
        raise SystemExit("Mismatch on random case")

    print("Random case comparison passed")


def _print_complexity_notes() -> None:
    """Print complexity notes."""
    print("Complexity Notes")
    for note in COMPLEXITY_NOTES:
        print(f"- Solver: {note.solver}")
        print(f"  Time: {note.time}")
        print(f"  Space: {note.space}")
        print(f"  Notes: {note.notes}")


def _build_parser() -> argparse.ArgumentParser:
    """Build CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Word Search II solver demo: run canonical sample and optional random "
            "baseline-vs-optimized comparisons."
        )
    )
    parser.add_argument(
        "--mode",
        choices=("sample", "random", "both"),
        default="both",
        help="Which run mode to execute.",
    )
    parser.add_argument("--seed", type=int, default=7, help="Random seed.")
    parser.add_argument("--rows", type=int, default=4, help="Random board rows.")
    parser.add_argument("--cols", type=int, default=4, help="Random board cols.")
    parser.add_argument("--words", type=int, default=12, help="Random words count.")
    parser.add_argument(
        "--hide-board",
        action="store_true",
        help="Hide board rendering for random case.",
    )
    parser.add_argument(
        "--complexity",
        action="store_true",
        help="Print complexity notes.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entrypoint used by ``python -m`` or direct script execution."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.complexity:
        _print_complexity_notes()

    if args.mode in ("sample", "both"):
        _run_sample_case()

    if args.mode in ("random", "both"):
        _run_random_case(
            seed=args.seed,
            rows=args.rows,
            cols=args.cols,
            words_n=args.words,
            show_board=not args.hide_board,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
