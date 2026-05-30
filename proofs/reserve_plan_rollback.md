# merge_train Reserve-Plan Evidence

This document records evidence that `reserve-plan` correctly implements
atomic all-or-nothing multi-domain reservation with rollback.

## Rollback test (2026-05-17)

1. proofs_domain held by PR#210 (placeholder)
2. reserve-plan for PR#211 requested [hello_domain, proofs_domain]
3. hello_domain reserved first (succeeded)
4. proofs_domain reserved second (DENIED — held by PR#210)
5. hello_domain reservation ROLLED BACK (note=rollback:reserve_plan)
6. Result: zero reservations leaked for PR#211

## Successful plan (after releasing proofs_domain)

1. Both domains free
2. reserve-plan for PR#211 succeeded: both hello_domain + proofs_domain
3. release --pr 211 released both simultaneously
