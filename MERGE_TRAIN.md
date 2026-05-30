# merge_train integration

This repo uses [merge_train](https://github.com/jleechanorg/merge_train) for spawn-time file-domain locking.

## Quick reference

```bash
# Before spawning an agent
domain_lock reserve --domain hello_domain --pr <PR> --agent <name> --branch <branch>

# Check if files are free
domain_lock check --files hello.py test_hello.py

# After PR merges
domain_lock release --pr <PR>

# See all active locks
domain_lock list --status active

# Full audit
domain_lock audit
```

## Domains

| Domain | Files |
|--------|-------|
| hello_domain | hello.py, test_hello.py |
| algo_domain | shortest_path_binary_matrix.py, test_shortest_path_binary_matrix.py |
| lc_domain | two_sum.py, valid_parentheses.py, test_two_sum.py, test_valid_parentheses.py |
| proofs_domain | proofs/** |
