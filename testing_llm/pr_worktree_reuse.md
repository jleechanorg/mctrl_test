# Worktree Reuse — Black-Box Verification

Real, observe-only. No mocks. No registry injection. No code edits during the run.

## Goal

Verify that `resolve_worktree_for_branch` correctly:
1. Returns an existing worktree when the branch is already checked out
2. Creates a fresh worktree when the branch exists on remote but not locally
3. Raises when the branch is missing everywhere

## Prerequisites

- `MCTRL=/Users/jleechan/project_jleechanclaw/mctrl`
- `PYTHONPATH=$MCTRL/src`
- A real git repo with at least one remote branch

## Step 1: Prove existing worktree detection

```bash
cd $MCTRL

# List real worktrees — confirms ground truth
git worktree list --porcelain

# Call find_existing_worktree for a branch that IS checked out
PYTHONPATH=src python3 -c "
from orchestration.dispatch_task import find_existing_worktree
result = find_existing_worktree('feat/mvp-loopback-supervisor', '.')
print('found:', result)
"
```

Pass requirement:
- Output contains a real path (not None)
- Path matches one of the `git worktree list` entries

## Step 2: Prove primary worktree is skipped

```bash
PYTHONPATH=src python3 -c "
from orchestration.dispatch_task import find_existing_worktree
# main branch is only in the primary worktree — should return None
result = find_existing_worktree('main', '.')
print('result (expect None):', result)
"
```

Pass requirement:
- Output is `None` — primary worktree must never be returned for dispatch

## Step 3: Prove fresh checkout for remote-only branch

```bash
# Pick any remote branch not currently in a local worktree
BRANCH=$(git branch -r | grep -v HEAD | head -1 | sed 's|origin/||' | tr -d ' ')
echo "Testing with branch: $BRANCH"

PYTHONPATH=src python3 -c "
import tempfile, os
from orchestration.dispatch_task import resolve_worktree_for_branch
with tempfile.TemporaryDirectory() as base:
    path, is_new = resolve_worktree_for_branch('$BRANCH', '.', base)
    print('path:', path)
    print('is_new:', is_new)
    print('worktree exists:', os.path.isdir(path))
    # Cleanup
    import subprocess
    subprocess.run(['git', 'worktree', 'remove', '--force', path])
"
```

Pass requirement:
- `is_new` is `True`
- Path exists as a real directory at call time
- Worktree removed cleanly after

## Step 4: Prove ValueError for nonexistent branch

```bash
PYTHONPATH=src python3 -c "
import tempfile
from orchestration.dispatch_task import resolve_worktree_for_branch
try:
    resolve_worktree_for_branch('feat/ghost-does-not-exist-xyz', '.', '/tmp')
    print('ERROR: expected ValueError')
except ValueError as e:
    print('Correctly raised ValueError:', e)
"
```

Pass requirement:
- Output contains `Correctly raised ValueError`
- No crash, no traceback

## Step 5: Self-test — resolve PR #59 branch

```bash
# PR #59 branch is feat/mvp-loopback-supervisor
# It should already be in a worktree (the main checkout)
# BUT the primary worktree should be skipped, so result is a linked worktree or None

PYTHONPATH=src python3 -c "
from orchestration.dispatch_task import find_existing_worktree
result = find_existing_worktree('feat/mvp-loopback-supervisor', '.')
print('linked worktree for PR #59 branch:', result)
"
```

Pass requirement:
- If a linked worktree exists for this branch → returns its path
- If only the primary checkout has it → returns None (correct — primary is excluded)

## Required Report Format

Every run must include:

### Proved
- (only claims backed by output from this run)

### Not Proved
- (anything not directly shown)
