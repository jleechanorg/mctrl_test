# Blank-first PR workflow for `jleechanorg/openclaw`

## Why this workflow
Keep the repository creation clean and auditable:

1. Create an empty repository first.
2. Apply sanitized config changes on a feature branch.
3. Open a PR for review.

## Steps

```bash
cd /Users/jleechan/.openclaw/workspace/openclaw-rehome

# 1) Run this once to create blank base + feature PR branch
./blank-to-pr.sh openclaw jleechanorg

# 2) Open PR (the script prints an example command)
gh pr create --repo jleechanorg/openclaw \
  --base main --head config-snapshot \
  --title "chore: add sanitized OpenClaw config snapshot"
```

## Safety

- `blank-to-pr.sh` creates an empty starting commit before adding files.
- `bootstrap-openclaw-config.sh` scrubs common secret patterns (`token`, `secret`, `password`, Slack tokens like `xoxb-`/`xapp-`) from copied files.
- This keeps the first commit non-sensitive and reviewable.
