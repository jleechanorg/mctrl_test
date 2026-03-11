#!/bin/bash
# ralph/lib/tools.sh — CLI tool adapter
# Resolves tool names (claude, codex, amp, minimax) to CLI commands.

# Resolve a tool name to its CLI command
# Usage: cmd=$(resolve_tool_cmd "claude")
resolve_tool_cmd() {
  local tool="$1"
  case "$tool" in
    claude)
      echo "claude --dangerously-skip-permissions -p"
      ;;
    minimax)
      # MiniMax uses Claude's Anthropic-compatible interface.
      # Environment wiring is applied in ralph.sh.
      echo "claude --dangerously-skip-permissions --print"
      ;;
    codex)
      echo "codex exec --full-auto"
      ;;
    amp)
      echo "amp -x"
      ;;
    *)
      echo "Error: Unknown tool '$tool'. Valid: claude, minimax, codex, amp" >&2
      return 1
      ;;
  esac
}

# List all supported tool names
# Usage: tools=$(list_supported_tools)
list_supported_tools() {
  echo "claude minimax codex amp"
}

# Check if a tool reads prompt from stdin (vs CLI arg)
# Usage: if [ "$(tool_needs_stdin "claude")" = "yes" ]; then ...
tool_needs_stdin() {
  local tool="$1"
  case "$tool" in
    claude|minimax|amp) echo "yes" ;;
    codex) echo "no" ;;
    *) echo "no" ;;
  esac
}
