# testing_mcp Rules

This directory inherits the root repo rules and adds stricter MCP verification rules.

## Purpose

`testing_mcp/` is for real OpenClaw MCP verification only.

## Hard Rules

- No mocks
- No monkeypatching
- No stubs
- No fake MCP servers
- No fake OpenClaw responses
- No replayed or canned payloads presented as live results
- No code or config edits as part of the claimed verification run

## Allowed Actions

- Call the real local `openclaw mcp` path
- Collect the real returned payload
- Collect real downstream evidence from logs, sessions, or recipient-visible artifacts

## Reporting

Every result must include:
- `Proved`
- `Not Proved`

Never report a pass from this directory unless the MCP path is real, local, and evidenced.
