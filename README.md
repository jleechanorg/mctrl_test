# mctrl_test

Python hello-world project used for mctrl orchestration testing.

## Usage

```bash
python hello.py
```

## Testing

```bash
pytest test_hello.py -v
```
<<<<<<< HEAD
=======

### Spawn an agent

```bash
pip install jleechanorg-orchestration

ai_orch run --agent-cli claude "Fix flaky integration tests and open PR"
ai_orch run --agent-cli codex "Refactor auth middleware"
```

### Backup

```bash
./scripts/backup-openclaw-full.sh
./scripts/install-openclaw-backup-jobs.sh  # set up scheduled backups
```

### Install launchd services

```bash
./scripts/install-launchagents.sh  # installs all plists from openclaw-config/
./scripts/install-openclaw-scheduled-jobs.sh  # installs and migrates scheduled jobs
```

## Agent Selection Guide

| Task Type | Agent | Why |
|-----------|-------|-----|
| Backend logic, complex bugs, multi-file refactors | Codex | Deep reasoning, low false-positive rate |
| Frontend, git operations, fast iteration | Claude Code | Fast, broad context |
| UI design, specs, creative | Gemini | Design sensibility |
| IDE-integrated tasks | Cursor | Tight IDE integration |

## Projects Managed

| Repo | Description |
|------|-------------|
| [worldarchitect.ai](https://github.com/jleechanorg/worldarchitect.ai) | AI RPG — primary project |
| [codex_fork](https://github.com/jleechanorg/codex_fork) | Fork of Codex open source CLI |
| [beads](https://github.com/jleechanorg/beads) | Memory upgrade for coding agents |
| [ai_universe](https://github.com/jleechanorg/ai_universe) | MCP Backend Server (Firebase + Cerebras) |
| [ai_universe_frontend](https://github.com/jleechanorg/ai_universe_frontend) | Multi-model AI consultation platform |
| [mcp_mail](https://github.com/jleechanorg/mcp_mail) | Agent-to-agent mail coordination |
| [worldai_claw](https://github.com/jleechanorg/worldai_claw) | AI RPG powered by OpenClaw |
| [claude-commands](https://github.com/jleechanorg/claude-commands) | Claude command collection |

## License

Private — personal workspace and tools for jleechan's OpenClaw setup.

bead rev-s1i
>>>>>>> 3149e7cdfb (docs: append bead rev-s1i marker to README)

bead rev-s1i
