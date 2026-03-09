# mctrl Reliability Execution Plan

Status: In progress
Owner: jleechanclaw orchestration
Last Updated: 2026-03-08

## Goal

Make mctrl status and handoff behavior trustworthy:
- do not mark work finished unless it is reviewable on remote
- do not send malformed Slack thread replies
- do not lose already-salvaged work
- do not let reused session names corrupt bead status
- do not let registry/worktree history grow without lifecycle controls

## In-Scope Beads

1. `ORCH-sjn` (P1 bug)
   Reclassify local-only commits as `needs_human` unless the branch is reachable on `origin`, and require push instructions in agent dispatch guidance.
2. `ORCH-en7` (P2 bug)
   Treat missing Slack trigger timestamps as absent, not the literal string `"None"`.
3. `ORCH-vej` (P1 task)
   Review PR #68 and land or explicitly reject the salvaged work from `ORCH-p0p`.
4. `ORCH-n5g` (P2 bug)
   Make dispatched session identity unique and bead-traceable.
5. `ORCH-gzr` (P3 task)
   Add registry/worktree archival and pruning policy after status truth is fixed.

Out of scope for this plan:
- `ORCH-6ej`
- `ORCH-0ik`

Those epics expand mctrl surface area. This plan is only for making the current core reliable.

## Execution Order

### Phase 1 - Finish Means Remote
Beads:
- `ORCH-sjn`
- `ORCH-en7`

Why first:
- `ORCH-sjn` is the active data-loss bug. Local commits are not a safe handoff surface.
- `ORCH-en7` is a same-layer notifier defect with a tiny blast radius and should ship with the first reliability pass.

Deliverables:
- reconciliation checks remote branch reachability before emitting `task_finished`
- missing remote branch becomes `task_needs_human` with explicit summary/action text
- dispatch instructions tell the spawned agent to push before stopping
- Slack notifier ignores missing/`None` trigger timestamps
- targeted unit coverage for both paths

### Phase 2 - Salvage What Already Exists
Bead:
- `ORCH-vej`

Why second:
- PR #68 already contains real work. It should be reviewed before more orchestration changes drift away from it.
- This is recovery work, not the durable fix itself.

Deliverables:
- review PR #68 against current `main`
- record what should merge, what should be superseded, and what should be abandoned
- merge only with explicit operator approval and passing CI

### Phase 3 - Unique Session Identity
Bead:
- `ORCH-n5g`

Why third:
- session-name reuse is another status-truth bug, but it becomes easier to validate once finish-vs-stranded behavior is already correct

Deliverables:
- unique tmux session name per dispatch, traceable to the bead
- registry records the unique name actually used by supervisor/reconciliation
- tests cover collision avoidance or post-spawn rename behavior

### Phase 4 - Lifecycle Hygiene
Bead:
- `ORCH-gzr`

Why last:
- pruning is useful only after terminal-state correctness is trustworthy
- archival policy should preserve evidence from the earlier fixes and salvage review

Deliverables:
- explicit archive/prune policy for terminal mappings and dead worktrees
- supervisor/archive flow that keeps active evidence while reducing stale clutter
- tests for archival thresholds and retained visibility

## Decision Notes

- `ORCH-gzr` stays behind `ORCH-n5g`. Cleanup should not ship before the current identity bugs are fixed.
- `ORCH-vej` remains in the sequence even though it is manual/review-heavy because stranded work should be resolved before the underlying branch and notifier flows drift further.
- If `ORCH-vej` cannot be merged immediately because approval or CI is missing, document that state and continue with `ORCH-n5g`.

## Validation Standard

For each implementation bead:
1. Run targeted unit tests for the changed modules.
2. Verify the new status text/action matches the failure mode.
3. Confirm beads/notes reflect the outcome and next dependency.

For `ORCH-vej`:
1. Review PR diff and CI state.
2. Record merge recommendation or rejection reason.
3. Merge only with explicit user approval.
