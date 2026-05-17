# merge_train Audit & List Evidence

## audit (2026-05-17)

```
$ domain_lock audit
{
  "registry": {
    "domains": {
      "hello_domain": { "paths": ["hello.py", "test_hello.py"], "owners": ["jleechan2015"] },
      "algo_domain": { "paths": ["shortest_path_binary_matrix.py", ...], ... },
      "lc_domain": { "paths": ["two_sum.py", ...], ... },
      "proofs_domain": { "paths": ["proofs/**"], ... }
    }
  },
  "active_locks": {},        # all released — correct
  "total_entries": 18,       # full lifecycle history preserved
  "generated_at": "2026-05-17T05:02:26Z"
}
```

## list --status active

```
(no output — all released)
```

## list --status all

```
18 entries covering:
- 4 whole-domain reserves (PR#202, 203, 205, 210)
- 2 symbol-level reserves (PR#206/hello, PR#207/goodbye)
- 2 reserve-plan entries (PR#211)
- 1 rollback entry (PR#211 hello_domain, note=rollback:reserve_plan)
- Corresponding releases for each
```

## list --status released

```
9 released entries (includes rollback entry with note field)
```

## check --json with mixed domains

```json
{
  "ok": true,
  "free_domains": ["hello_domain", "lc_domain", "proofs_domain"],
  "held": [],
  "unmapped_files": []
}
```
