# Agent Outcome Ledger: Structured Learning Loop

> The missing link between tactical automation and strategic improvement.

**Bead:** `ORCH-qvd` (P1)
**Sub-tasks:** `ORCH-657` (schema+writer), `ORCH-5s8` (lifecycle integration), `ORCH-6y3` (pattern synthesis cron)
**Depends on:** `ORCH-y77` (lifecycle reaction engine)
**Enables:** `ORCH-04k` (Self-Improving Prompts), `ORCH-vvh` (Cost Dashboard), `ORCH-431` (Replay Failed Agents), `ORCH-8z2` (Cross-Repo Coordination)

## Problem

Every agent spawn is a fresh guess. jleechanclaw picks a CLI (claude/codex/gemini/cursor), crafts a prompt, and fires. The lifecycle engine (PR #7) handles tactical reactions — retry on CI failure, forward review comments. But nothing captures what happened for future reference.

The orchestrator makes the same mistakes repeatedly:
- Sending auth bugs to the wrong CLI
- Omitting file paths that would have saved 3 retries
- Over-stuffing prompts when a focused one would have worked
- Not knowing which task types cost 10x more tokens than expected

There's no feedback. No learning. No compounding improvement.

## Solution

A structured outcome log that captures every agent run as a JSONL record, stored in the OpenClaw workspace where `memory_search` can index it. Weekly LLM-generated pattern synthesis produces a markdown summary that feeds directly into jleechanclaw's context at session start.

The orchestrator literally gets smarter every week — grounded in real data (CI pass rates, merge rates, retry counts, token costs), not hallucinated self-assessment.

## Architecture

```
                    ┌──────────────────────────┐
                    │   lifecycle_reactions.py   │
                    │   (terminal states)        │
                    └──────────┬───────────────┘
                               │ record_outcome()
                               ▼
                    ┌──────────────────────────┐
                    │   outcome_ledger.py        │
                    │                            │
                    │  - OutcomeRecord dataclass  │
                    │  - record_outcome()         │
                    │  - get_recent_outcomes()    │
                    │  - monthly JSONL rotation   │
                    └──────────┬───────────────┘
                               │ writes
                               ▼
                    ┌──────────────────────────┐
                    │  ~/.openclaw/workspace/    │
                    │  outcomes/                 │
                    │    2026-02.jsonl           │
                    │    2026-03.jsonl           │
                    │    PATTERNS.md  ◄──── weekly cron synthesis
                    └──────────────────────────┘
                               │
                    memorySearch.extraPaths
                               │
                               ▼
                    ┌──────────────────────────┐
                    │  jleechanclaw session      │
                    │  (reads PATTERNS.md at     │
                    │   startup via memory_search)│
                    └──────────────────────────┘
```

## JSONL Schema

Each record is a single line in `outcomes/YYYY-MM.jsonl`:

```jsonl
{
  "ts": "2026-02-25T10:30:00Z",
  "run_id": "run-abc123",
  "cli": "claude",
  "repo": "worldarchitect.ai",
  "task_type": "bug_fix",
  "prompt_summary": "Fix flaky auth middleware tests",
  "prompt_hash": "sha256:a1b2c3...",
  "files_hinted": ["src/auth/middleware.ts", "src/auth/middleware.test.ts"],
  "prompt_features": {
    "included_file_paths": true,
    "included_error_logs": true,
    "included_test_examples": false,
    "word_count": 180
  },
  "outcome": "merged",
  "ci_attempts": 1,
  "review_rounds": 0,
  "human_edits": 0,
  "duration_min": 12,
  "cost_tokens": 45000,
  "branch": "fix/auth-flaky",
  "pr": 142
}
```

### Field Reference

| Field | Type | Description |
|-------|------|-------------|
| `ts` | ISO 8601 | When outcome was recorded |
| `run_id` | string | Unique identifier from ai_orch |
| `cli` | enum | `claude` \| `codex` \| `gemini` \| `cursor` |
| `repo` | string | Repository name |
| `task_type` | string | Classified by jleechanclaw: `bug_fix`, `feature`, `refactor`, `test`, `docs`, `ci_fix`, `design` |
| `prompt_summary` | string | One-line summary of what was asked |
| `prompt_hash` | string | SHA-256 of full prompt (for dedup/replay) |
| `files_hinted` | string[] | File paths included in the prompt |
| `prompt_features` | object | Boolean/numeric features for correlation analysis |
| `outcome` | enum | Terminal state: `merged`, `stuck`, `errored`, `killed`, `done` |
| `ci_attempts` | int | Number of CI runs before success (or final failure) |
| `review_rounds` | int | Number of review cycles |
| `human_edits` | int | Number of human commits on the PR after agent |
| `duration_min` | int | Wall-clock time from spawn to terminal state |
| `cost_tokens` | int | Total token usage (if available from CLI) |
| `branch` | string | Git branch name |
| `pr` | int \| null | PR number if created |

### Outcome Values

| Outcome | Meaning | Source |
|---------|---------|--------|
| `merged` | PR merged successfully | lifecycle `merged` state |
| `done` | Task completed without PR (e.g., analysis) | lifecycle `done` state |
| `stuck` | Agent hit retry limit, escalated to human | lifecycle `stuck` state |
| `errored` | Agent crashed or exited non-zero | lifecycle `errored` state |
| `killed` | Manually terminated | lifecycle `killed` state |

## Module: `orchestration/outcome_ledger.py`

```python
"""Agent Outcome Ledger — structured learning from agent runs."""

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

OUTCOMES_DIR = Path.home() / ".openclaw" / "workspace" / "outcomes"

Outcome = Literal["merged", "done", "stuck", "errored", "killed"]
CLI = Literal["claude", "codex", "gemini", "cursor"]


@dataclass
class OutcomeRecord:
    run_id: str
    cli: CLI
    repo: str
    task_type: str
    prompt_summary: str
    outcome: Outcome
    ts: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    prompt_hash: str = ""
    files_hinted: list[str] = field(default_factory=list)
    prompt_features: dict = field(default_factory=dict)
    ci_attempts: int = 0
    review_rounds: int = 0
    human_edits: int = 0
    duration_min: int = 0
    cost_tokens: int = 0
    branch: str = ""
    pr: int | None = None


def record_outcome(record: OutcomeRecord, outcomes_dir: Path = OUTCOMES_DIR) -> Path:
    """Append an outcome record to the current month's JSONL file."""
    outcomes_dir.mkdir(parents=True, exist_ok=True)
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    path = outcomes_dir / f"{month}.jsonl"
    with open(path, "a") as f:
        f.write(json.dumps(asdict(record), default=str) + "\n")
    return path


def hash_prompt(prompt: str) -> str:
    """SHA-256 hash of the full prompt for dedup/replay."""
    return f"sha256:{hashlib.sha256(prompt.encode()).hexdigest()[:16]}"


def get_recent_outcomes(
    months: int = 1, outcomes_dir: Path = OUTCOMES_DIR
) -> list[OutcomeRecord]:
    """Read outcomes from recent months."""
    records = []
    now = datetime.now(timezone.utc)
    for i in range(months):
        month_dt = now.replace(month=max(1, now.month - i))
        path = outcomes_dir / f"{month_dt.strftime('%Y-%m')}.jsonl"
        if path.exists():
            for line in path.read_text().splitlines():
                if line.strip():
                    data = json.loads(line)
                    records.append(OutcomeRecord(**data))
    return records
```

## Integration Point: lifecycle_reactions.py

Single hook at terminal state transitions:

```python
# In lifecycle_reactions.py — at each terminal state handler
from orchestration.outcome_ledger import OutcomeRecord, record_outcome, hash_prompt

def _on_terminal_state(agent_state: AgentState, outcome: str):
    record = OutcomeRecord(
        run_id=agent_state.run_id,
        cli=agent_state.cli,
        repo=agent_state.repo,
        task_type=agent_state.task_type,
        prompt_summary=agent_state.prompt_summary,
        prompt_hash=hash_prompt(agent_state.full_prompt),
        outcome=outcome,
        ci_attempts=agent_state.ci_attempts,
        review_rounds=agent_state.review_rounds,
        duration_min=agent_state.elapsed_minutes(),
        branch=agent_state.branch,
        pr=agent_state.pr_number,
    )
    record_outcome(record)
```

## Pattern Synthesis Cron Job

Added to `genesis/cron.py` alongside the existing MEMORY.md curation job:

```json
{
  "id": "genesis-outcome-patterns",
  "name": "Outcome pattern synthesis",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 21 * * 0",
    "tz": "America/Los_Angeles"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "Read all outcomes/*.jsonl files from the last 30 days. Analyze agent run outcomes and update outcomes/PATTERNS.md with: (1) CLI success rates with sample sizes, (2) prompt feature correlations with outcome, (3) anti-patterns to avoid, (4) task type routing recommendations. Use actual counts. Be concise. Do not hallucinate statistics — only report what the data shows."
  },
  "delivery": {
    "mode": "none",
    "channel": "last"
  }
}
```

Schedule: **Sunday 9PM PST** (1 hour before MEMORY.md curation at 10PM).

## PATTERNS.md Template

Initial seed (before any data exists):

```markdown
# Agent Outcome Patterns

> Auto-generated weekly from outcomes/*.jsonl by genesis-outcome-patterns cron.
> Last updated: (not yet run)

## CLI Success Rates (last 30 days)

No data yet. Patterns will appear after agent runs are recorded.

## Prompt Feature Correlations

Tracking which prompt features correlate with success:
- File paths included
- Error logs included
- Test examples included
- Prompt word count

## Anti-Patterns

Known failure modes will be logged here as data accumulates.

## Task Type → CLI Recommendations

Routing heuristics will emerge from outcome data.
```

## Config: memorySearch.extraPaths

Add to `~/.openclaw/openclaw.json`:

```jsonc
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "extraPaths": [
          // ... existing paths ...
          "/Users/jleechan/.openclaw/workspace/outcomes/PATTERNS.md"
        ]
      }
    }
  }
}
```

## What This Enables (Downstream)

### Superpower 2: Self-Improving Prompts (ORCH-04k)
With the ledger, jleechanclaw can query: "What prompt features correlated with success for `bug_fix` tasks in `worldarchitect.ai`?" and construct prompts accordingly. The PATTERNS.md provides pre-computed heuristics; the raw JSONL enables ad-hoc queries.

### Superpower 4: Cost Dashboard (ORCH-vvh)
`cost_tokens` per record enables: total spend by CLI, cost per successful merge, cost trends over time. Mission Control can ingest the JSONL for visualization.

### Superpower 5: Replay Failed Agents (ORCH-431)
`prompt_hash` enables exact replay. `outcome=stuck|errored` records include the context needed for informed retry. The ledger stores what was tried; the lifecycle engine handles the retry.

### Superpower 6: Cross-Repo Coordination (ORCH-8z2)
`repo` field enables cross-repo analysis: "When tasks span worldarchitect.ai + ai_universe, what decomposition patterns succeed?"

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| JSONL not SQLite | Markdown-first. OpenClaw philosophy: files are source of truth, sqlite is just an index. JSONL is grep-able, git-trackable, human-readable. |
| Monthly rotation | Keeps individual files under ~1000 lines even at high agent throughput. Old months available for historical analysis. |
| Pattern synthesis is an LLM task | The LLM analyzing its own performance is the whole point. Grounded in real data, not self-hallucination. |
| `prompt_features` is freeform dict | Features will evolve as we learn what correlates. No rigid schema that needs migration. |
| Outcomes dir in workspace, not repo | Agent outcomes are operational data, not source code. Indexed by memorySearch, not committed to git. |
| Zero new infrastructure | No new databases, servers, or processes. Just files. |

## Open Questions

1. **Token cost tracking**: Not all CLIs expose token counts. Start with what's available (Claude via API response headers, others estimated)?
2. **Prompt classification**: Should `task_type` be agent-classified at spawn time, or post-hoc during pattern synthesis?
3. **Human edit tracking**: How to detect post-agent human commits on a branch? `git log --author` filtering?
4. **Replay threshold**: How many outcomes before pattern synthesis produces meaningful statistics? (Probably ~20-30 runs minimum)
5. **Privacy**: Should full prompts be stored alongside hashes for replay, or just hashes to save space?
