# merge_train V4 Multifile M2 Plan Rollback and Retry Evidence

This document records evidence that the v4 MULTIFILE M2 worker correctly exercises the multi-domain `reserve-plan` atomic rollback and retry mechanism under contention in a saturated demo state.

## 1. Saturated Demo State (Active Locks)

The following active locks were held in the registry:
- **PR #197 (Worker C3)**: holds `demo::delta` and `demo::helper_c`
- **PR #199 (Worker M1)**: holds `demo::helper_e` and `demo2::alpha2`

```bash
$ domain_lock --registry merge_train_demo/file_domains.yaml --log pr_domain_locks.jsonl list --status active
demo	PR#197	mt-197	mt-test/worker-C3	2026-05-29T21:00:00Z	active	symbols=delta,helper_c
demo	PR#199	mt-199	mt-test/worker-M1	2026-05-29T21:05:00Z	active	symbols=helper_e
demo2	PR#199	mt-199	mt-test/worker-M1	2026-05-29T21:05:00Z	active	symbols=alpha2
```

## 2. First Attempt: Overlap & Rollback

Worker M2 (PR #200) attempted to reserve a plan containing `demo2::beta2` (free) and `demo::delta` (held by PR #197):

**Plan File (`proofs/plan_m2_attempt1.yaml`)**:
```yaml
plan:
  - domain: demo2
    symbols:
      - beta2
  - domain: demo
    symbols:
      - delta
```

**Execution Output**:
```bash
$ domain_lock --registry merge_train_demo/file_domains.yaml --log pr_domain_locks.jsonl reserve-plan --pr 200 --agent mt-200 --branch mt-test/worker-M2 --plan proofs/plan_m2_attempt1.yaml
DENIED: symbol(s) delta in domain 'demo' held by PR #197 (agent=mt-197, branch=mt-test/worker-C3) (plan rolled back)
```

**Audit Log Rollback Verification**:
The first leg (`demo2::beta2`) succeeded initially and was immediately rolled back:
```json
{"domain":"demo2","pr":200,"agent":"mt-200","branch":"mt-test/worker-M2","opened_at":"2026-05-30T05:06:03Z","status":"active","closed_at":null,"note":null,"symbols":["beta2"]}
{"domain":"demo2","pr":200,"agent":"mt-200","branch":"mt-test/worker-M2","opened_at":"2026-05-30T05:06:03Z","status":"released","closed_at":"2026-05-30T05:06:03Z","note":"rollback:reserve_plan","symbols":["beta2"]}
```

## 3. Second Attempt: Successful Retry with Disjoint Plan

Worker M2 retried reserving a plan containing `demo2::beta2` and `demo::helper_f` (both dynamically free and disjoint):

**Plan File (`proofs/plan_m2_attempt2.yaml`)**:
```yaml
plan:
  - domain: demo2
    symbols:
      - beta2
  - domain: demo
    symbols:
      - helper_f
```

**Execution Output**:
```bash
$ domain_lock --registry merge_train_demo/file_domains.yaml --log pr_domain_locks.jsonl reserve-plan --pr 200 --agent mt-200 --branch mt-test/worker-M2 --plan proofs/plan_m2_attempt2.yaml
RESERVED: demo2	PR#200	mt-200	mt-test/worker-M2	2026-05-30T05:06:13Z	active	symbols=beta2
RESERVED: demo	PR#200	mt-200	mt-test/worker-M2	2026-05-30T05:06:13Z	active	symbols=helper_f
```

Both legs were successfully and atomically reserved.
