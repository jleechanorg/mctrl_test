# Hard Memory + PR Validation Questions (2026-03-09)

Use these to stress-test OpenClaw memory retrieval, source ranking, chronology, and policy-to-implementation traceability.

## Answer Contract (Strict)

- Only cite artifacts that currently exist in this workspace.
- Every non-trivial claim must include at least one checkable anchor (file path, commit SHA, ORCH/bead ID, date, or command output location).
- If the required evidence is missing, answer `unknown`.
- Do not propose hypothetical evidence files (especially under `/tmp/`) unless they already exist right now.
- If sources conflict, cite both and resolve by canonical recency order:
  1) `workspace/MEMORY.md` Project Status/Decisions (newest wins)
  2) `openclaw-config/SOUL.md`
  3) Session logs / ad-hoc notes

## Questions

1. Reconstruct **W9 2026** as a dependency graph: which workstreams blocked or unblocked others, and what concrete artifact proves each edge?
2. What changed in the memory model between the old `worldai_claw` event-log format and the newer `workspace/MEMORY.md` Project Status format, and what retrieval failure does that prevent?
3. Show one example where the **Config-first principle** changed implementation choice in this PR: what code path was avoided, what config file was edited, and why that is more durable.
4. Find a claim in session logs that is now stale or contradicted by current repo state. Give both sources and explain which should win.
5. For the streaming bug fix (`len > 20` gate removal), identify the exact regression risk introduced and the test that would catch it if it reappears.
6. Which behavior rules are enforced by policy text only (`SOUL.md` / `AGENTS.md`), and which are actually enforced in runtime or CI? List one gap and a concrete guardrail to close it.
7. Trace `mctrl supervisor loop` from trigger to final user-visible signal (Slack thread and DM). Where is the weakest observability point?
8. If the same request is replayed in two contexts (fresh thread vs ongoing thread), what deterministic outputs must remain identical under the durable-behavior goal?
9. What is the most likely TOCTOU race still possible in `worldai_claw` after this PR, and what minimal reproducible timing sequence demonstrates it?
10. Name one place where memory retrieval could return a true but misleading answer due to mixed recency layers (session log vs `MEMORY.md` vs `SOUL.md`). How should ranking/disambiguation resolve it?
11. Give a single-sentence policy that would have prevented the “older session log beat newer project memory” confusion, and show where it should live.
12. What evidence bundle under `/tmp/` is sufficient to prove this PR’s memory-related behavior end-to-end, without reading source code?
