# CMUX Integration Design for Mission Control + Ralph + Orchestration

## Status
Draft proposal for cross-repo implementation (`jleechanclaw` + `worldarchitect.ai`).

## Goal
Add a first-class **cmux execution mode** alongside tmux so that:
1. Every new Mission Control task can spawn into a named cmux terminal (`mc:{branch_name}`).
2. Ralph tasks can run in cmux as an alternative to tmux.
3. `orchestration/` supports cmux backend selection, attach to existing terminals, or create new ones.
4. Operators can watch full live output and manually interrupt/steer by typing directly.

---

## User Stories

1. **Mission Control task launch**
   - As an operator, when a task is created in MC inbox and dispatched, I want a cmux terminal created automatically with a predictable name like `mc:feature-branch`, so I can inspect live execution.

2. **Ralph workflow in cmux**
   - As an operator, I want Ralph tasks to run in cmux mode instead of tmux when configured, without changing task content.

3. **Manual takeover**
   - As an operator, I want to attach to the running cmux terminal, observe full logs, type commands, interrupt, and continue execution flow.

4. **Compatibility fallback**
   - As an operator, if cmux is unavailable or misconfigured, I want controlled fallback behavior (either fail-fast or explicit fallback to tmux based on config).

---

## Scope

### In Scope
- Add `cmux` execution backend in orchestration abstractions.
- Mission Control dispatch integration to create/target cmux terminal names.
- Ralph task path support for cmux backend.
- Attach/list/status primitives for cmux sessions/terminals.
- Config + CLI flags to choose backend per task/workflow.

### Out of Scope (Phase 1)
- Rewriting task business logic.
- Replacing tmux entirely.
- Multi-host cmux federation.

---

## Architecture

## 1) Unified terminal backend interface
Define a single internal terminal backend contract used by Mission Control and Ralph dispatchers.

Suggested interface:
- `ensure_terminal(targetName, options)` -> create or return existing terminal handle
- `run_command(handle, command, env, cwd)`
- `attach(handle)`
- `send_input(handle, text)`
- `interrupt(handle)`
- `read_log(handle, sinceOffset?)`
- `is_alive(handle)`
- `terminate(handle)`

Backends:
- `TmuxBackend` (existing behavior)
- `CmuxBackend` (new)

This minimizes changes in higher-level orchestration logic.

## 2) Naming and targeting strategy
Terminal naming convention:
- Mission Control task default: `mc:{branch_name}`
- Ralph task default: `ralph:{branch_name}` (or `mc:{branch_name}` if unified namespace desired)

Normalization:
- Lowercase
- Replace `/` and spaces with `-`
- Truncate to safe max length

Collision strategy:
- If name exists and `reuse=true`: attach/reuse.
- If name exists and `reuse=false`: append short suffix (`-a1b2`).

## 3) Backend selection model
Configuration precedence (highest to lowest):
1. Explicit task override (`terminal_backend=cmux|tmux`)
2. Workflow default (Ralph or MC profile)
3. Global default in config

Additional options:
- `terminal_target`: explicit name to attach/create
- `terminal_reuse`: true/false
- `terminal_fallback`: `never|tmux`

## 4) Mission Control integration points
In `jleechanclaw` task dispatch pipeline:
- At task-to-worker handoff, resolve branch name and compute terminal name.
- Ask backend manager for terminal handle (`ensure_terminal`).
- Launch task command in terminal context.
- Persist terminal metadata with task state:
  - backend type
  - terminal name/id
  - attach command

Task status view should expose:
- `backend=cmux`
- `target=mc:...`
- `attach_hint=...`

## 5) Ralph integration points
Ralph runner currently tmux-first should call the same backend manager.
- Add Ralph setting: `RALPH_TERMINAL_BACKEND=tmux|cmux`
- Keep current tmux path as default until explicitly switched.

## 6) Cross-repo orchestration support (`worldarchitect.ai/orchestration`)
Add cmux mode in orchestration runtime and command surfaces:
- CLI args:
  - `--terminal-backend tmux|cmux`
  - `--terminal-target <name>`
  - `--reuse-terminal`
- Config/env:
  - `ORCH_TERMINAL_BACKEND`
  - `ORCH_TERMINAL_FALLBACK`

Operational modes:
- **Create new** terminal if none exists.
- **Target existing** terminal if requested.

This lets backend and frontend PR task runs use identical mechanics.

---

## UX / Operator Controls

Required operator capabilities:
1. List active terminals by backend and task mapping.
2. Attach to live terminal.
3. Send manual input.
4. Interrupt current process (Ctrl+C equivalent).
5. Detach without killing.

Mission Control should store and display one-line attach instructions for each running task.

---

## Failure Handling

1. **cmux missing binary / unavailable**
   - If `terminal_fallback=tmux`: log warning + use tmux.
   - If `terminal_fallback=never`: fail task launch with actionable error.

2. **Terminal creation failure**
   - Task remains `inbox` or moves to `error` with reason + retry option.

3. **Command exits unexpectedly**
   - Preserve terminal for inspection; do not auto-destroy by default.

4. **Manual operator interruption**
   - Mark task as `interrupted_by_operator` and allow resume/retry actions.

---

## Security / Safety Considerations
- Explicitly log manual operator intervention events.
- Avoid injecting raw unescaped user strings into shell commands.
- Keep backend wrapper responsible for safe command composition.
- Include per-task cwd + env in audit metadata (excluding secrets).

---

## Rollout Plan

### Phase 0: Design + interface hardening
- Finalize backend interface and config schema.
- Add no-op cmux feature flag plumbing.

### Phase 1: Orchestration library cmux backend
- Implement `CmuxBackend` and unit tests.
- Add CLI/config/env support.
- Validate attach/reuse/create flows.

### Phase 2: Mission Control integration (`jleechanclaw`)
- Use backend manager in MC task dispatch.
- Terminal naming `mc:{branch_name}`.
- Persist/display terminal metadata.

### Phase 3: Ralph integration
- Add Ralph backend selector.
- Execute Ralph tasks in cmux when enabled.

### Phase 4: Cross-repo adoption (`worldarchitect.ai`)
- Update orchestration callers to pass backend options.
- Verify backend preview/frontend companion workflows still pass.

---

## Testing Plan

### Unit tests
- Name normalization + collision behavior
- Backend selection precedence
- Fallback behavior matrix
- Terminal lifecycle methods (mocked)

### Integration tests
- Create task -> cmux terminal created -> command running
- Reuse existing cmux terminal path
- Operator interrupt path
- Ralph flow in cmux mode

### Live/manual validation
- Start task and attach from operator shell
- Type command manually while task active
- Interrupt and verify state transitions

---

## Open Questions
1. Canonical cmux attach/list command format to show in task UI?
2. Should MC and Ralph share namespace (`mc:*`) or stay separated (`mc:*`, `ralph:*`)?
3. Default fallback policy in production: strict fail vs tmux fallback?
4. Should terminals auto-cleanup after successful completion, or remain until TTL expiry?

---

## Recommended Initial Defaults
- Default backend: `tmux` (compatibility)
- Enable cmux via explicit opt-in per workflow/task.
- Fallback: `tmux` for first rollout; move to strict after confidence.
- Keep completed terminals for short TTL (e.g., 24h) for debugging.

---

## Success Criteria
- New MC tasks can run with `terminal_backend=cmux` and named terminal `mc:{branch_name}`.
- Ralph can execute in cmux via config without code-path divergence.
- Operator can attach, observe, type, interrupt, and detach successfully.
- Existing tmux behavior remains intact when cmux is disabled.
