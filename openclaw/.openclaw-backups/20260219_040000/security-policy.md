# OpenClaw Security Policy

## Allowed CLI Commands
- codex
- npm
- npx
- git
- node
- python
- pip

## Blocked Commands (Exfiltration/Dangerous)
- curl
- wget
- ssh
- sudo
- rm -rf
- dd
- mkfs

## Workspace Restrictions
- Working directory: /Users/jleechan/.openclaw/workspace
- No access to: ~/.ssh, ~/.aws, ~/.config, ~/Documents

## Review this file before enabling new commands
