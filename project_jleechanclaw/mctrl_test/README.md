# mctrl_test

`mctrl_test` is a minimal test repository used to validate Mission Control (mctrl) task dispatch and agent execution flows.

## What this repo is for

- Sanity-checking that dispatched tasks can create and modify files
- Verifying basic project scaffolding behavior in a fresh repository
- Serving as a lightweight example for Python + pytest + CI setup flows

## Typical contents

This repo is intended to stay simple, usually containing:

- A small Python hello-world style module or script
- Basic `pytest` tests
- A CI workflow to run tests on push/PR

## Why it exists

It provides a low-risk target for testing orchestration reliability before running larger automation tasks on production repositories.
Loop5 E2E test touchpoint.
