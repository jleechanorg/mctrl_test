#!/bin/bash
# ralph/lib/workspace.sh — Workspace resolution and runner preparation
# Sourced by ralph.sh. All functions take explicit args.

# Resolve workspace directory (default to repo root if empty)
# Usage: result=$(resolve_workspace <workspace_arg> <repo_root>)
resolve_workspace() {
  local workspace_arg="$1" repo_root="$2"
  if [ -n "$workspace_arg" ]; then
    echo "$workspace_arg"
  else
    echo "$repo_root"
  fi
}

# Build the agent prompt from CLAUDE.md with resolved paths
# Usage: prompt=$(build_prompt <claude_md> <prd_file> <progress_file> <workspace>)
build_prompt() {
  local template="$1" prd_file="$2" progress_file="$3" workspace="$4"
  [ ! -f "$template" ] && { echo "Error: $template not found" >&2; return 1; }

  local prompt
  prompt=$(cat "$template")
  # Resolve relative paths in the prompt to absolute
  prompt="${prompt//\`prd.json\`/\`$prd_file\`}"
  prompt="${prompt//at \`prd.json\`/at \`$prd_file\`}"
  prompt="${prompt//\`progress.txt\`/\`$progress_file\`}"
  prompt="${prompt//to \`progress.txt\`/to \`$progress_file\`}"

  if [ -n "$workspace" ]; then
    prompt="# Workspace: $workspace
All source code changes MUST go in $workspace (not the ralph/ directory).
$prompt"
  fi

  echo "$prompt"
}

# Generate runner script for tmux with CLAUDECODE fix
# Usage: prepare_runner <output_file> <workspace> <tool> <prompt_file> <log_file> <transcript_file>
prepare_runner() {
  local output_file="$1" workspace="$2" tool="$3"
  local prompt_file="$4" log_file="$5" transcript_file="$6"
  local tool_cmd="$tool"
  local tool_key="${tool_cmd%% *}"
  local tool_parts

  if command -v resolve_tool_cmd >/dev/null 2>&1; then
    tool_cmd="$(resolve_tool_cmd "$tool_key")"
  fi

  read -r -a tool_parts <<< "$tool_cmd"

  cat > "$output_file" <<RUNNER
#!/bin/bash
set -uo pipefail
unset CLAUDECODE     # Allow claude to run inside tmux subprocess
cd "$workspace"
if [[ "$tool_key" == "codex" ]]; then
  PROMPT=\$(cat "$prompt_file")
  ${tool_parts[@]} "\$PROMPT" 2>&1 | tee -a "$log_file" "$transcript_file"
else
  cat "$prompt_file" | ${tool_parts[@]} 2>&1 | tee -a "$log_file" "$transcript_file"
fi
RUNNER
  chmod +x "$output_file"
}
