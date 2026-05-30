# merge_train Pre-commit Hook Evidence

## Hook blocks held domain (2026-05-17)

hello_domain held by PR#230 (other-agent).

```
$ git add hello.py
$ git commit -m "test: should be blocked"
HELD: hello_domain by PR#230 agent=other-agent branch=feat/other-pr
# exit 1 — commit REFUSED
```

## Hook allows free domain

algo_domain was free (no active locks).

```
$ git add shortest_path_binary_matrix.py
$ git commit -m "feat: add grid_size()"
WARN: unmapped files (no domain): pr_domain_locks.jsonl
FREE: 1 domain(s) clear (algo_domain)
# exit 0 — commit ALLOWED
```

## Hook installation

```bash
ln -sf ../../hooks/pre-commit.sh .git/hooks/pre-commit
chmod +x hooks/pre-commit.sh
```
