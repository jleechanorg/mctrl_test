# Remembering Preferences

- If user says "minimax", interpret it as using `claudem()` behavior from `~/.bashrc`:
  - `ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic`
  - `ANTHROPIC_AUTH_TOKEN=$MINIMAX_API_KEY`
  - `ANTHROPIC_MODEL=MiniMax-M2.5`
  - run `claude --dangerously-skip-permissions --teammate-mode=tmux`
- Do **not** shadow real CLI names with function names (e.g., never redefine `claude()`).
- When user asks to remember something, always report:
  1) location of file edit in `~/.openclaw`
  2) merge-to-`origin/main` remote commit URL (or explicitly state blocker if unavailable).
- SOUL.md location preference:
  - Never put/update SOUL at `/Users/jleechan/SOUL.md`.
  - Always use `~/.openclaw/SOUL.md` as the authoritative SOUL file.
