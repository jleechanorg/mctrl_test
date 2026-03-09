# Hard Memory + PR Questions Run — 2026-03-09

Date: 2026-03-09  
Method: OpenClaw CLI (`openclaw agent --agent main --thinking low --json`)  
Question set: `testing_llm/hard_memory_pr_questions_20260309.md`

## Artifacts

- `testing_llm/artifacts/openclaw_hard_questions_batch_20260309_main.json` (successful batched ask, includes all 12 answers)
- `testing_llm/artifacts/openclaw_hard_q01_20260309.json` … `openclaw_hard_q12_20260309.json` (initial failed attempts without explicit routing)
- `testing_llm/artifacts/openclaw_hard_q01_20260309_main.json` … `openclaw_hard_q12_20260309_main.json` (partial per-question rerun attempts before interruption)

## Proved

- Hard question set was saved in-repo under `testing_llm/hard_memory_pr_questions_20260309.md`.
- OpenClaw was asked the full 12-question set in one batch and returned a full answer payload.
- Successful run produced a durable artifact with model/session metadata and response text:
  - `meta.durationMs=126548` (~126.5s)
  - `meta.aborted=false`
  - 12 numbered answers present in `payloads[0].text`

## Not Proved

- No external cross-check was performed to validate each citation/claim in the OpenClaw answer.

## Strict Rubric (Applied)

Pass criteria used per question:

1. Must answer the asked task directly (no evasive/general answer).
2. Must include at least one concrete, checkable anchor (file/path/date/ID/line/command/artifact).
3. Must avoid unsupported claims to files/artifacts that do not exist in this workspace context.

Scoring:

- `PASS`: all 3 criteria met.
- `PARTIAL`: criteria (1) and either (2) or (3) met.
- `FAIL`: misses (1), or makes key unsupported claims.

## Re-Grade of Batch Artifact

Source graded:

- `testing_llm/artifacts/openclaw_hard_questions_batch_20260309_main.json` (`payloads[0].text`)

Results:

| Q | Grade | Why |
|---|---|---|
| Q1 | PASS | Direct dependency graph with concrete anchors (`MEMORY.md` dated sections/line refs). |
| Q2 | PASS | Direct model-change answer with concrete retrieval-failure claim and anchors. |
| Q3 | PARTIAL | Answers directly and cites config-first direction, but PR-specific scope evidence is weak. |
| Q4 | PASS | Provides stale vs current claim and resolution rule; includes checkable file anchor. |
| Q5 | FAIL | Uses non-present test/doc artifacts in this workspace context; key evidence is unsupported. |
| Q6 | PARTIAL | Distinguishes policy vs enforcement, but runtime/CI proof remains generic. |
| Q7 | PASS | Clear trigger→registry→supervisor→Slack trace with concrete paths/sections. |
| Q8 | PARTIAL | Gives deterministic principles, but lacks concrete reproducible check anchor. |
| Q9 | FAIL | Mostly speculative race narrative with no concrete local proof artifact. |
| Q10 | PASS | Strong mixed-recency conflict example with explicit disambiguation policy. |
| Q11 | PASS | Clear single-sentence policy and placement recommendation. |
| Q12 | PARTIAL | Good bundle shape, but describes proposed files rather than existing verified bundle. |

Strict total: `6 PASS`, `4 PARTIAL`, `2 FAIL`.

## Main Failure Modes

- Unsupported references: answer cites artifacts not present in this workspace context (`Q5`).
- Over-speculation without proof anchors (`Q9`).
- Good policy synthesis but weak reproducibility anchors (`Q3`, `Q6`, `Q8`, `Q12`).

## Next Hardening Step

- Re-run the same 12 questions with an explicit instruction: "Only cite artifacts that currently exist in this workspace; if missing, say unknown."
- Auto-fail any answer that references absent files or non-checkable IDs.

## Guardrail Added (2026-03-09)

- Verifier script: `scripts/validate-memory-answer-evidence.sh`
- Purpose: fail closed when a generated answer cites non-existent file paths, invalid commit SHAs, or unknown `ORCH-*` IDs.

Baseline run against current batch artifact:

```bash
scripts/validate-memory-answer-evidence.sh \
  testing_llm/artifacts/openclaw_hard_questions_batch_20260309_main.json
```

Outcome: `FAIL` (expected on current artifact), with unsupported citations:

- `docs/streaming-evidence/pr-5849-openrouter-streaming-evidence.md`
- `project_jleechanclaw/jleechanclaw/docs/GENESIS_DESIGN.md`
- `testing_mcp/streaming/test_openrouter_streaming_real.py`

## Strict Rerun (with Answer Contract)

- Artifact: `testing_llm/artifacts/openclaw_hard_questions_batch_20260309_020253_strict.json`
- Command used:

```bash
openclaw agent --agent main --thinking low --json \
  --message "$(cat testing_llm/hard_memory_pr_questions_20260309.md)" \
  > testing_llm/artifacts/openclaw_hard_questions_batch_20260309_020253_strict.json
```

- Validation command:

```bash
scripts/validate-memory-answer-evidence.sh \
  testing_llm/artifacts/openclaw_hard_questions_batch_20260309_020253_strict.json
```

Validation outcome: `FAIL` with unsupported citations:

- `/automation-publish`
- `/tmp/e2e-memory-proof/01-query-before.txt`
- `/tmp/e2e-memory-proof/02-memory-snapshot.txt`
- `/tmp/e2e-memory-proof/03-query-after.txt`
- `/tmp/e2e-memory-proof/04-conflict-resolution.txt`
- `/tmp/e2e-memory-proof/05-citations.json`
- `testing_mcp/streaming/test_openrouter_streaming_real.py`

Interpretation:

- The stricter prompt improved behavior (`unknown` was used for uncertain items), but citation discipline is still incomplete.
- Remaining failures are mostly hypothetical paths (especially `/tmp` bundle paths) and one non-existent test path citation.

## Strict Rerun v2 (no hypothetical `/tmp` evidence)

- Artifact: `testing_llm/artifacts/openclaw_hard_questions_batch_20260309_020622_strict2.json`
- Prompt change: added rule in `hard_memory_pr_questions_20260309.md` to forbid hypothetical evidence files unless they already exist.
- Verifier update: `workspace/...` references are now validated against `~/.openclaw/workspace/...`.

Validation command:

```bash
scripts/validate-memory-answer-evidence.sh \
  testing_llm/artifacts/openclaw_hard_questions_batch_20260309_020622_strict2.json
```

Validation outcome: `PASS` (all cited paths/IDs/SHAs verifiable).
