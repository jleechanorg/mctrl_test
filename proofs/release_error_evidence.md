# merge_train Release & Error Evidence

## release --domain filtering (2026-05-17)

PR#220 held both hello_domain and algo_domain.

```
$ domain_lock release --pr 220 --domain algo_domain
RELEASED: algo_domain  PR#220  ...  released

$ domain_lock list --status active
hello_domain  PR#220  ...  active    # only hello_domain remains
```

## release idempotency (double-release)

```
$ domain_lock release --pr 220
RELEASED: hello_domain  PR#220  ...  released

$ domain_lock release --pr 220
no active reservations for PR #220   # exit 1, not crash
```

## UnknownPathError (bad domain)

```
$ domain_lock reserve --domain nonexistent_domain --pr 221 ...
error: unknown domain: nonexistent_domain    # exit 2
```
