# Project Context: beads

**Repo**: https://github.com/jleechanorg/beads
**Commits**: 1,898

## What It Is

"Memory upgrade for your coding agent" — task tracking system for AI agents.

## Key Files

- `beads.go` - Main entry point
- `.beads/` - Beads data directory
- `CLAUDE.md` - Project-specific agent instructions

## Common Tasks

| Task | Command |
|------|---------|
| Run beads | `bd <command>` |
| Create task | `bd create "title" --priority 2` |
| List tasks | `bd list` |

## Notes

- Requires `bd` CLI installed (from beads repo or separate install)
- Uses JSONL for storage under `.beads/`
- MCP server available but needs bd CLI to function
