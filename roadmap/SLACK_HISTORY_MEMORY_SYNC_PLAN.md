# Slack History -> Memory Sync Plan

## Goal
Make OpenClaw remember more of Jeffrey's Slack context by periodically ingesting Slack message history into `~/.openclaw/memory/slack-history/`, which is already included by memory search via `memorySearch.extraPaths` parent path `~/.openclaw/memory`.

## Why This Is Needed
OpenClaw can read Slack history during a turn, but it is bounded by `historyLimit` / `dmHistoryLimit` and context-scoped retrieval. It does not automatically persist all past Slack conversations into memory files by config alone.

## Design
1. Source: Slack Web API (`conversations.history`, `conversations.replies`) using bot token.
2. Scope: channel IDs from `openclaw.json` allowlist (`channels.slack.channels`) unless overridden.
3. Safety: redact secrets/PII before write.
4. Dedupe: maintain `~/.openclaw/memory/slack-sync-state.json` with per-channel latest `ts`.
5. Output path:
   - staging: `/tmp/openclaw-slack-memory-staging/<timestamp>/`
   - promoted: `~/.openclaw/memory/slack-history/`
6. Artifact format: markdown files + `manifest.json` for verification.

## Script
- `scripts/slack_history_to_memory.py`

## Staging Verification Contract
1. Run with `--full-history` into `/tmp/...` and without `--promote`.
2. Verify:
   - `manifest.json` exists
   - channel message counts are non-zero where expected
   - markdown artifacts are present and redacted
3. Promote by rerunning with `--promote` or copying staged artifacts to `~/.openclaw/memory/slack-history/`.

## Launchd Scheduling Plan
1. Add a launchd job (hourly or every 4 hours) that runs:
   - `/bin/bash -lc 'python3 <repo>/scripts/slack_history_to_memory.py --stage-dir /tmp/openclaw-slack-memory-staging --promote'`
2. Log stdout/stderr to `~/.openclaw/logs/scheduled-jobs/`.
3. Keep schedule disabled by default until first staging validation passes.

## Answer: Can We "Just Configure OpenClaw" To Treat Conversations As Memory?
Not fully. Config can increase retrieval limits and enable memory search, but long-term conversation persistence still needs an ingestion path (like this sync job) to materialize history into indexed memory files.
