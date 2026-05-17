# merge_train check --diff-mode Evidence

## Setup

Two symbol-level locks on algo_domain:
- PR#240: symbols=grid_size,has_path
- PR#241: symbols=shortest_path_binary_matrix

## Case 1: Edit free symbol (shortest_path_binary_matrix_dfs) — FREE

Staged change trims docstring of `shortest_path_binary_matrix_dfs`.

```json
{
  "ok": true,
  "free_domains": ["algo_domain"],
  "held": [],
  "touched_symbols": { "algo_domain": ["shortest_path_binary_matrix_dfs"] }
}
```

Result: `shortest_path_binary_matrix_dfs` does not overlap any held symbol → FREE.

## Case 2: Edit held symbol (shortest_path_binary_matrix) — HELD

Staged change trims docstring of `shortest_path_binary_matrix` (held by PR#241).

```json
{
  "ok": false,
  "held": [{ "domain": "algo_domain", "holder": { "pr": 241, "symbols": ["shortest_path_binary_matrix"] } }],
  "touched_symbols": { "algo_domain": ["shortest_path_binary_matrix"] }
}
```

Result: `shortest_path_binary_matrix` overlaps PR#241's held symbol → HELD.

## Case 3: Own-PR carve-out with --diff-mode

`check --files shortest_path_binary_matrix.py --diff-mode --pr 241` → FREE.
Own-PR reservation doesn't self-conflict, even in symbol-level mode.

## Key insight

Without --diff-mode, any edit to `shortest_path_binary_matrix.py` would
be HELD (file-level collision). With --diff-mode, only edits touching
overlapping Python symbols collide — enabling true fine-grained
co-tenancy on the same file.
