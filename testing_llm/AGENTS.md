# testing_llm Rules

This directory inherits the root repo rules and adds stricter verification rules.

## Purpose

`testing_llm/` is for real, black-box, observe-only verification artifacts.

## Hard Rules

- No mocks
- No monkeypatching
- No stubs
- No fake sessions
- No direct registry/outbox/session injection
- No code or config edits as part of the claimed verification run
- No canned pass tables or historical claims without attached evidence

## Allowed Actions

- Inject a real external trigger such as a Slack message posted as jleechan
- Read logs, Slack responses, OpenClaw-visible outputs, and other externally visible artifacts
- Summarize only what the evidence directly proves

## Reporting

Every result must include:
- `Proved`
- `Not Proved`

Never label anything in this directory as `E2E PASS` unless every claimed step is backed by artifacts from that run.
