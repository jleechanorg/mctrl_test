# Peekaboo Antigravity UI Automation Setup (OpenClaw)

## Goal

Enable OpenClaw agents to control the **Antigravity IDE** through GUI automation using the Peekaboo CLI on macOS.

**Bead:** `ORCH-ma4`

## Status

- **In progress**: environment setup and tooling scaffolded.
- Local Peekaboo skill added to `openclaw-config/skills/peekaboo/`.
- Preflight check script at `scripts/peekaboo-preflight.sh`.
- Limitation: not headless; requires a physical Mac session with Accessibility + Screen Recording permissions.

## 1) Environment Prerequisites

- macOS machine with Antigravity installed and launchable.
- OpenClaw working locally with a current version.
- User can run shell commands from terminal (`open -a Antigravity`, etc.).
- Permissions granted in System Settings:
  - **Accessibility** (for Peekaboo UI automation actions)
  - **Screen Recording** (for screenshots and UI snapshots)

## 2) Install Peekaboo CLI

```bash
brew install steipete/tap/peekaboo
```

Verify installation:

```bash
peekaboo --version
peekaboo permissions      # check Accessibility + Screen Recording
```

A local copy of the official Peekaboo skill is at `openclaw-config/skills/peekaboo/SKILL.md` — it documents all CLI commands, targeting parameters, and examples.

## 3) PeekabooBridge

PeekabooBridge is built into the **OpenClaw macOS app** (`PeekabooBridgeHostCoordinator.swift`). When the app is running with PeekabooBridge enabled:

- Bridge socket: `~/Library/Application Support/OpenClaw/PeekabooBridge.sock`
- Allowlisted team IDs include the OpenClaw signing team (`Y5PE65HELJ`) plus the current app's team
- Services exposed: UI automation, screen capture, window management, menu service, application service, dialog service

**To enable:** launch the OpenClaw macOS app and ensure PeekabooBridge is enabled in settings. Keep the app running during automation sessions.

## 4) Confirm Antigravity Control Path

1. Open Antigravity:
   ```bash
   open -a Antigravity
   ```

2. Take an annotated UI snapshot (semantic map with clickable element IDs):
   ```bash
   peekaboo see --app Antigravity --annotate --path /tmp/antigravity-see.png
   ```

3. Click a UI element (e.g., button B1 from the snapshot):
   ```bash
   peekaboo click --on B1 --app Antigravity
   ```

4. Type into a text field:
   ```bash
   peekaboo type "Hello from Peekaboo" --app Antigravity
   ```

5. Submit (press Enter):
   ```bash
   peekaboo press return --app Antigravity
   ```

6. Capture result screenshot:
   ```bash
   peekaboo image --app Antigravity --path /tmp/antigravity-result.png
   ```

## 5) Test Plan (Minimum Viable Verification)

### Automated validation (local CI-safe)

Run the preflight check:

```bash
bash scripts/peekaboo-preflight.sh
```

This validates:
- Peekaboo CLI installed and on PATH
- Accessibility permission granted
- Screen Recording permission granted
- Antigravity app found
- PeekabooBridge socket exists
- Local skill file present

Additional file/tracker checks:
- `test -f roadmap/PEEKABOO_ANTIGRAVITY_UI_AUTOMATION.md`
- `rg -n "ORCH-ma4" roadmap/PEEKABOO_ANTIGRAVITY_UI_AUTOMATION.md`
- `bd show ORCH-ma4` returns a ticket entry

### Manual runtime validation (macOS)

Run the skill against a simple Antigravity task:
1. Ensure Antigravity is visible and focused.
2. Agent prompt uses Peekaboo actions to create a new task/agent.
3. Confirm the see → click → type → submit path succeeds and returns a result.
4. Confirm output appears in the expected preview/terminal pane.
5. Note any UI fragility points (renamed controls, focus errors, permission prompts).

## Known Failure Modes

- Peekaboo not installed → `peekaboo: command not found`.
- Permissions not granted → Accessibility/Screen Recording actions silently fail.
- Window not focused → clicks/typing land in wrong app. Use `--app Antigravity` targeting.
- Antigravity UI changes element labels → re-run `peekaboo see --annotate` to refresh snapshot IDs.
- Heavy automation on restricted accounts → prompts/actions may be limited by app policy.
- PeekabooBridge not running → socket missing; start OpenClaw macOS app.

## Next Steps

1. Install Peekaboo CLI (`brew install steipete/tap/peekaboo`) and run preflight.
2. Build a retry wrapper + retryable prompt for focus/app state recovery.
3. Add concise runbook for session setup (`SOUL.md` / agent prompt guidance).
4. Capture exact command/version matrix that works for this environment.
