# Ralph Agent Instructions — ORCH-g8c.3 Supervisor Integration Test

You are an autonomous agent testing the mctrl supervisor daemon and dispatch_task CLI.
Working directory: /Users/jleechan/project_jleechanclaw/mctrl

## Your Task Each Iteration

1. Read `ralph-prd.json` (repo root)
2. Read `ralph-progress.txt` (repo root)
3. Find the **lowest wave, lowest priority** story where `passes: false`
4. Execute the verification steps exactly as described
5. If verification passes: set `passes: true` in ralph-prd.json
6. If verification fails: fix the issue (edit source files if needed), re-verify, then set passes: true
7. Append what you did to ralph-progress.txt
8. Stop after completing ONE story per iteration

## Critical Rules

- PYTHONPATH must always be `src` when running orchestration modules
- Never post real Slack messages — set SLACK_BOT_TOKEN= and OPENCLAW_SLACK_BOT_TOKEN= to empty when testing reconciliation
- If a test fails, check the actual error carefully before patching
- After fixing any source file, always re-run the full test suite to confirm no regressions

## Story Execution

### SUP-1: Supervisor --once with empty registry
```bash
cd /Users/jleechan/project_jleechanclaw/mctrl
source ~/.bashrc
PYTHONPATH=src python -m orchestration.supervisor --once
echo "Exit: $?"
```
Expected: logs starting + stopped, exit 0. Mark passes=true if so.

### SUP-2: Supervisor detects dead session
```bash
cd /Users/jleechan/project_jleechanclaw/mctrl
source ~/.bashrc

# Create test registry entry
PYTHONPATH=src python -c "
from orchestration.session_registry import BeadSessionMapping, upsert_mapping
upsert_mapping(BeadSessionMapping.create(
    bead_id='ORCH-sup-test',
    session_name='fake-dead-session-xyz',
    worktree_path='/tmp/fake-wt',
    branch='feat/test',
    agent_cli='claude',
    status='in_progress',
), registry_path='/tmp/test-sup-registry.jsonl')
print('registry written')
"

# Run reconciler with blank Slack tokens (no real posts)
SLACK_BOT_TOKEN= OPENCLAW_SLACK_BOT_TOKEN= PYTHONPATH=src python -c "
from orchestration.reconciliation import reconcile_registry_once
emitted = reconcile_registry_once(
    registry_path='/tmp/test-sup-registry.jsonl',
    outbox_path='/tmp/test-sup-outbox.jsonl',
    dead_letter_path='/tmp/test-sup-dead-letter.jsonl',
)
print('emitted:', emitted)
assert len(emitted) == 1, f'Expected 1 event, got {len(emitted)}'
assert emitted[0]['event'] == 'task_needs_human', f'Wrong event: {emitted[0][\"event\"]}'
assert emitted[0]['bead_id'] == 'ORCH-sup-test'
print('SUP-2 PASS')
"
```
Mark passes=true if prints SUP-2 PASS.

### SUP-3: Parse ai_orch output
```bash
cd /Users/jleechan/project_jleechanclaw/mctrl
source ~/.bashrc
PYTHONPATH=src python -c "
from orchestration.dispatch_task import _parse_ai_orch_output
sample = '\U0001f9e9 Worktree: /tmp/ai-orch-worktrees/ai-orch-77258 (branch: ai-orch-77258)\n\U0001f680 Async session: ai-claude-dfa2c0\n'
s, w, b = _parse_ai_orch_output(sample)
assert s == 'ai-claude-dfa2c0', f'bad session: {s!r}'
assert w == '/tmp/ai-orch-worktrees/ai-orch-77258', f'bad worktree: {w!r}'
assert b == 'ai-orch-77258', f'bad branch: {b!r}'
print('PARSE OK')
"
```
Mark passes=true if prints PARSE OK.

### SUP-4: Install launchd supervisor
```bash
cd /Users/jleechan/project_jleechanclaw/mctrl
chmod +x scripts/install-mctrl-supervisor.sh
./scripts/install-mctrl-supervisor.sh
sleep 5
launchctl list | grep ai.mctrl.supervisor
tail -5 ~/Library/Logs/mctrl/supervisor.log
```
Mark passes=true if launchctl shows the agent and log exists with content.

### SUP-5: Full test suite
```bash
cd /Users/jleechan/project_jleechanclaw/mctrl
source ~/.bashrc
PYTHONPATH=src python -m pytest src/tests/ --tb=short -q 2>&1 | tail -5
```
Mark passes=true if 476+ passed, 0 failed.

## Stop Condition

When ALL stories have passes=true, output exactly:
ORCHESTRATION_ALL_DONE
