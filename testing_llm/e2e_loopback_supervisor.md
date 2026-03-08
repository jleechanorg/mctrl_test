# Black-Box Loopback Verification

`testing_llm/` is reserved for real, black-box verification only.

Forbidden in this directory:
- mocks
- monkeypatching
- stubs
- fake sessions
- direct registry/outbox/session injection
- editing code or config as part of the claimed verification
- canned "confirmed run" tables without attached evidence

If a test needs simulated internals, it does not belong in `testing_llm/`. Move it to `src/tests/` and label it honestly as unit, integration, or simulated coverage.

## Goal

Verify the real loop:

`Slack trigger as jleechan -> dispatch_task -> real ai_orch session -> supervisor detects exit -> notify_openclaw -> Slack DM + thread reply`

This runbook is observe-only. It may trigger the system from the outside, then collect evidence from externally visible behavior.

## Prerequisites

- `source ~/.profile` works and provides `SLACK_USER_TOKEN`
- `bd` in PATH
- `ai_orch` in PATH
- `openclaw` in PATH
- `ai.mctrl.supervisor` is already running
- `MCTRL=/Users/jleechan/project_jleechanclaw/mctrl`

## Step 1: Prove Slack identity

```bash
source ~/.profile
curl -s https://slack.com/api/auth.test \
  -H "Authorization: Bearer $SLACK_USER_TOKEN"
```

Pass requirement:
- response contains `"ok":true`
- response identifies user `jleechan`

## Step 2: Post a real trigger as jleechan

```bash
source ~/.profile
TRIGGER_TEXT="[mctrl-blackbox] $(date +%s) real loopback verification"
curl -s -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer $SLACK_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"channel\":\"C0AKALZ4CKW\",\"text\":\"$TRIGGER_TEXT\"}"
```

Save the JSON response. The `ts` field is the real `trigger_ts`.

## Step 3: Create a real bead

```bash
bd create -p 2 "Black-box loopback verification" \
  --description "Real Slack trigger and real supervisor/OpenClaw loopback verification"
```

Save the bead id.

## Step 4: Start a real dispatch

```bash
cd "$MCTRL"
PYTHONPATH=src python -m orchestration.dispatch_task \
  --bead-id "<BEAD_ID>" \
  --task "Black-box loopback verification. Reply back through the normal completion path." \
  --slack-trigger-ts "<TRIGGER_TS>"
```

This step must create the real worktree/session through the normal system path. Do not write registry rows manually.

## Step 5: Observe the live system

Collect evidence only. Do not mutate runtime state.

Minimum evidence:
- supervisor evidence showing the real bead/session was detected
- real session identity from normal runtime output
- Slack DM evidence in `D0AFTLEJGJU`
- threaded reply evidence under the original `trigger_ts`
- OpenClaw-visible evidence that `notify_openclaw` actually delivered or that outbox fallback was used

Examples of acceptable evidence sources:
- supervisor logs
- OpenClaw session logs
- Slack API responses from `conversations.history` and `conversations.replies`
- `.messages/outbox.jsonl` state, read-only

## Step 6: Evaluate terminal outcome honestly

Two terminal outcomes are possible:

1. `task_finished`
2. `task_needs_human`

Either outcome is acceptable for this verification if and only if all evidence is internally consistent. Do not mix `task_finished` text with `needs_human` status, and do not report a PASS if OpenClaw delivery is only assumed.

## Pass Criteria

All of the following must be true:
- Slack trigger was posted by `jleechan`
- a real dispatch was launched through `orchestration.dispatch_task`
- a real session existed and later exited
- supervisor detected that real exit
- the reported terminal status matches the observed evidence
- Slack DM landed
- thread reply landed under the original trigger
- OpenClaw delivery is directly evidenced, not inferred

## Required Report Format

Every run must include both sections:

### Proved
- only claims backed by attached artifacts

### Not Proved
- anything not directly evidenced

Never report `E2E PASS` unless every pass criterion above is backed by artifacts from that run.
