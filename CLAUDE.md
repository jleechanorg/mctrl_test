# Project: jleechanclaw (orchestration system)

## PR Readiness Definition

A PR is **ready/mergeable** when ALL of the following are true:

1. **CI green** — all GitHub Actions checks pass
2. **Tests passing** — relevant test suite runs clean locally and in CI
3. **No merge conflicts** — GitHub shows MERGEABLE, not CONFLICTING
4. **No serious review comments** — no unresolved bug reports or blocking feedback from reviewers
5. **CodeRabbit approves or is rate-limited** — if CodeRabbit was unable to review due to rate limits, treat as acceptable (not a blocker)

A PR that meets all 5 criteria can be merged without further review. If any criterion fails, fix before merging.

## Project Structure

- `src/orchestration/` — core orchestration engine (task dispatch, heartbeat, MC integration)
- `docs/` — project documentation
- `roadmap/` — planning artifacts
- `config.yaml` — project configuration

## Conventions

- Commit messages: `type(scope): description` (conventional commits)
- Branch naming: `fix/`, `feat/`, `chore/` prefixes
- Tests live alongside source or in dedicated test directories
- Use `gh` CLI for all GitHub operations
