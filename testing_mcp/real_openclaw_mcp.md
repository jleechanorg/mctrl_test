# Real OpenClaw MCP Verification

`testing_mcp/` is reserved for real MCP verification only.

Forbidden in this directory:
- mocks
- monkeypatching
- stubs
- fake MCP servers
- fake OpenClaw responses
- replayed/canned outputs presented as a live result
- code or config changes as part of the claimed verification

If a check needs simulated internals, it does not belong in `testing_mcp/`. Put it in `src/tests/` and label it honestly.

## Goal

Verify that this repo can talk to the real local OpenClaw MCP path, not a fake or patched substitute.

The canonical live route in this repo is the one used by `src/orchestration/openclaw_notifier.py`:

```text
openclaw mcp call mcp-agent-mail send_message ...
```

## Preconditions

- `openclaw` is installed and on `PATH`
- the local OpenClaw environment is running and usable
- the target recipient agent exists in the real local OpenClaw environment
- no code/config edits are made during the claimed verification run

## Step 1: Verify the CLI exists

```bash
openclaw --help
```

Pass requirement:
- command succeeds

## Step 2: Verify MCP subcommand availability

```bash
openclaw mcp --help
```

Pass requirement:
- command succeeds and shows MCP usage

If this fails, the test must fail loudly. Do not fall back to a fake path and do not report success.

## Step 3: Send a real MCP message

Use the live MCP agent-mail tool, not a stub:

```bash
openclaw mcp call mcp-agent-mail send_message \
  --project_key "<REAL_PROJECT_KEY>" \
  --sender_name "<REAL_SENDER_AGENT>" \
  --to "<REAL_RECIPIENT_AGENT>" \
  --subject "mctrl real MCP verification" \
  --body_md "Real MCP verification from testing_mcp at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

Save the full JSON response.

## Step 4: Verify delivery with real evidence

Acceptable evidence:
- returned MCP payload from `send_message`
- real OpenClaw session/log evidence showing the message was handled
- real recipient-visible evidence if the target agent or channel exposes it

Not acceptable:
- "the command returned 0" without payload
- inferred delivery without downstream evidence
- screenshots or summaries without the underlying artifact

## Pass Criteria

All of the following must be true:
- `openclaw mcp --help` worked on the real local install
- `openclaw mcp call mcp-agent-mail send_message` was executed against the real local environment
- the response payload indicates success
- at least one downstream real artifact confirms the message was actually handled

## Required Report Format

Every `testing_mcp/` run must include:

### Proved
- only claims directly backed by attached artifacts

### Not Proved
- anything inferred but not directly evidenced

Never report a pass from `testing_mcp/` unless the MCP path is real, local, and evidenced end to end.
