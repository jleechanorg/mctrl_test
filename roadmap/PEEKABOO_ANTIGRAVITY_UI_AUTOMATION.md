# Peekaboo Antigravity UI Automation Setup (OpenClaw)

## Goal

Enable OpenClaw agents to control the **Antigravity IDE** through GUI automation using the Peekaboo extension on macOS.

**Bead:** `ORCH-ma4`

## Status

- Planned: enable macOS-only automation path for agent workflows that cannot use backend APIs.
- Limitation: not headless; requires a physical Mac session with Accessibility + Screen Recording permissions.

## 1) Environment prerequisites

- macOS machine with Antigravity installed and launchable.
- OpenClaw working locally with a current version.
- User can run shell commands from terminal (`open -a Antigravity`, etc.).
- Permissions available in System Settings:
  - Accessibility (for PeekabooBridge)
  - Screen Recording (if screenshots are required)

## 2) Install Peekaboo skill

1. In OpenClaw, install the skill package (official/bundled source):

```bash
npx openclaw skills add peekaboo
```

2. Confirm the skill appears in local skill list (or equivalent list command in your installed OpenClaw version).
3. If install command differs in your version, use the closest official install path from CLI help/docs and re-run with the exact syntax.

## 3) Install/run PeekabooBridge

1. Launch/install the PeekabooBridge companion app (macOS helper for Accessibility API actions).
2. In System Settings, grant Accessibility + Screen Recording.
3. Keep the bridge running during automation sessions.

## 4) Confirm Antigravity control path

1. Open Antigravity:

```bash
open -a Antigravity
```

2. Focus the window from the bridge control layer.
3. Snapshot UI state (semantic map preferred over raw screenshots).
4. Navigate to Mission Control in-app context if needed.
5. Click **New Agent** / equivalent UI control.
6. Enter a prompt, run it, and wait for completion signal.
7. Capture result artifact (screenshot or output pane snapshot).

## 5) Test plan (minimum viable verification)

### Automated validation (local CI-safe)
- File + tracker validation:
  - `test -f roadmap/PEEKABOO_ANTIGRAVITY_UI_AUTOMATION.md`
  - `rg -n "ORCH-ma4" roadmap/PEEKABOO_ANTIGRAVITY_UI_AUTOMATION.md`
  - `mcp__beads__show` for `ORCH-ma4` returns a ticket entry

### Manual runtime validation (macOS)
- Run the skill against a simple Antigravity task:
  1. Ensure Antigravity is visible.
  2. Agent prompt uses Peekaboo actions to create a new task/agent.
  3. Confirm the UI click/type/submit path succeeds and returns a result.
  4. Confirm output appears in the expected preview/terminal pane.
  5. Note any UI fragility points (renamed controls, focus errors, permission prompts).

## Known failure modes

- Bridge not permitted in Accessibility/Screen Recording → actions silently fail.
- Window not focused → clicks/typing land in wrong app.
- Antigravity UI changes refs/labels → semantic snapshots need refresh.
- Heavy automation on restricted accounts → prompts/actions may be limited by app policy.

## Next steps

1. Capture exact command/version matrix that works for your environment.
2. Build a retry wrapper + retryable prompt for focus/app state recovery.
3. Add a concise runbook for session setup (`SOUL.md` / agent prompt guidance).
