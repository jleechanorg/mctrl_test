# merge_train AO Spawn-Integration Evidence

## Pre-spawn gate: blocks conflicting worker (2026-05-17)

hello_domain reserved by PR#300 (ao-worker-a).

```
$ MERGE_TRAIN_FILES="hello.py test_hello.py" \
  MERGE_TRAIN_REGISTRY=file_domains.yaml \
  bash hooks/ao-spawn-domain-check.sh
HELD: hello_domain by PR#300 agent=ao-worker-a branch=feat/ao-integration-a
exit: 1  # spawn REFUSED
```

## Pre-spawn gate: allows non-overlapping worker

algo_domain is free (no active locks).

```
$ MERGE_TRAIN_FILES="shortest_path_binary_matrix.py" \
  MERGE_TRAIN_REGISTRY=file_domains.yaml \
  bash hooks/ao-spawn-domain-check.sh
FREE: 1 domain(s) clear (algo_domain)
exit: 0  # spawn ALLOWED
```

## Own-PR carve-out

```
$ MERGE_TRAIN_FILES="hello.py test_hello.py" \
  MERGE_TRAIN_PR=300 \
  MERGE_TRAIN_REGISTRY=file_domains.yaml \
  bash hooks/ao-spawn-domain-check.sh
FREE: 1 domain(s) clear (hello_domain)
exit: 0  # own-PR re-check is free
```

## Empty files list allows spawn (no-op)

```
$ MERGE_TRAIN_FILES="" \
  MERGE_TRAIN_REGISTRY=file_domains.yaml \
  bash hooks/ao-spawn-domain-check.sh
merge_train: MERGE_TRAIN_FILES is empty — no files to check, allowing spawn
exit: 0
```

## Release after merge

```
$ domain_lock release --pr 300
RELEASED: hello_domain  PR#300  ao-worker-a  feat/ao-integration-a  released
```

## External lock storage (orch-i7uv)

Lock log is now at `~/.merge_train/locks/<repo-hash>/pr_domain_locks.jsonl`
— outside the repo tree. No more JSONL merge conflicts.

```
$ ls ~/.merge_train/locks/
c1b59b22bdd7/

$ domain_lock audit | jq '.total_entries'
2
```
