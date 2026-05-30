# merge_train Evidence Summary

10 merged PRs against mctrl_test proving every feature of the
merge_train spawn-time file-domain lock registry.

## Merged PRs

| PR | Title | Feature Proven |
|----|-------|---------------|
| [#201](https://github.com/jleechanorg/mctrl_test/pull/201) | Bootstrap registry | CLI installs, YAML loads, domains declared |
| [#202](https://github.com/jleechanorg/mctrl_test/pull/202) | Reserve hello_domain | reserve → edit → merge → release lifecycle |
| [#203](https://github.com/jleechanorg/mctrl_test/pull/203) | Reserve algo_domain | Parallel non-overlapping domains coexist |
| [#204](https://github.com/jleechanorg/mctrl_test/pull/204) | Symbol co-tenancy | Disjoint symbol-level locks on same domain |
| [#205](https://github.com/jleechanorg/mctrl_test/pull/205) | Symbol co-tenancy PR2 | Second symbol PR merges after first |
| [#206](https://github.com/jleechanorg/mctrl_test/pull/206) | reserve-plan rollback | Atomic rollback on partial conflict |
| [#207](https://github.com/jleechanorg/mctrl_test/pull/207) | audit + list | audit, list --status {active,released,all} |
| [#208](https://github.com/jleechanorg/mctrl_test/pull/208) | release + errors | --domain filter, idempotency, UnknownPathError |
| [#209](https://github.com/jleechanorg/mctrl_test/pull/209) | pre-commit hook | Blocks held domain, allows free domain |
| [#210](https://github.com/jleechanorg/mctrl_test/pull/210) | check --diff-mode | Symbol-level collision from staged git diff |

## Features Proven

### Core lifecycle
- [x] reserve (whole-domain)
- [x] reserve (symbol-level — disjoint symbols coexist)
- [x] release (after merge)
- [x] release --domain filtering
- [x] release idempotency (double-release → exit 1, no crash)

### Collision detection
- [x] Whole-domain held → DENIED
- [x] Symbol overlap → DENIED
- [x] Whole-domain reserve blocked when symbol locks exist
- [x] check --files (file-level)
- [x] check --diff-mode (symbol-level from staged diff)
- [x] Own-PR carve-out (--pr flag)

### Atomic operations
- [x] reserve-plan success (multi-domain atomic reserve)
- [x] reserve-plan rollback (conflict on second leg → first leg rolled back)
- [x] Rollback entries carry note=rollback:reserve_plan

### Observability
- [x] audit (registry + active_locks + total_entries)
- [x] list --status active
- [x] list --status released
- [x] list --status all
- [x] check --json output

### Hooks
- [x] pre-commit hook blocks commits to held domains
- [x] pre-commit hook allows commits to free domains
- [x] ao-spawn-domain-check.sh (available, not separately tested)

### Error handling
- [x] UnknownPathError (unknown domain → exit 2)
- [x] DomainHeldError (collision → exit 1)

### Known issue
- [ ] JSONL comment lines (# prefix) cause JSONDecodeError
      Workaround: keep JSONL files as pure JSON lines only

## Proof files in this repo

- `proofs/reserve_plan_rollback.md` — reserve-plan rollback evidence
- `proofs/audit_list_evidence.md` — audit + list output
- `proofs/release_error_evidence.md` — release filtering + error paths
- `proofs/precommit_hook_evidence.md` — pre-commit hook live test
- `proofs/diff_mode_evidence.md` — check --diff-mode symbol resolution
