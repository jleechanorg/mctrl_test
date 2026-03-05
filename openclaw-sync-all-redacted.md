# OpenClaw Full Config Sync (Safe/Redacted)

I can’t execute shell commands in this session right now (`exec` is currently blocked by allowlist), so run this on your machine in one shot.

This will:
- mirror **all of `~/.openclaw`** into the repo checkout
- redact secrets in-place
- keep binaries and generated/cache noise out
- commit and push to `https://github.com/jleechanorg/openclaw`

## One command

```bash
bash ~/.openclaw/workspace/openclaw/scripts/sync_openclaw_full_redacted.sh
```

## Script behavior
- copies everything except:
  - `.git`, `.DS_Store`, `*.pyc`, `*.pem`, `*.key`, `*.crt`, `*.p12`, `*.pfx`, `*.id_rsa*`, `node_modules`, `*.log`
- redacts probable secrets in copied text files using regex:
  - `password`, `secret`, `token`, `key`, `api[_-]key`, `private[_-]key`, `auth`, `oauth`, `client_secret`, bearer tokens, JWT-like long strings
  - environment-style assignments like `NAME=...`
- preserves file permissions + line endings where possible
- updates `REDACTION_LOG.md` with what was redacted

## Repo workflow
- clones/opens `jleechanorg/openclaw`
- copies the redacted snapshot under `openclaw-config/`
- commits `chore: sync ~/.openclaw with sensitive fields redacted`
- pushes to `main`
