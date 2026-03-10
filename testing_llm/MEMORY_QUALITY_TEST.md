# Memory Quality Test — OpenClaw RAG

**Date:** 2026-03-09
**Purpose:** Prove (or disprove) that the new synthesized memory files enable genuine decision-support recall.

Each question should be answerable from RAG over `~/.openclaw/memory/` + SOUL.md + MEMORY.md.
Questions are ordered by difficulty. Answers recorded below each question after running.

---

## Category 1: Decision History (high value)

**Q1.** Why did we move PR automation off system crontab onto openclaw gateway cron? When did that happen?

> Expected: Mentions crontab migration, approximate date (W10/early March 2026), reason (macOS launchd, gateway cron is canonical)

---

**Q2.** We considered Mission Control for the mctrl loop — why did we decide against it?

> Expected: MC is frozen/optional mirror only, not in lifecycle path, demoted to optional upgrade

---

**Q3.** What's the story behind the mass-deletion incident? What exactly went wrong and what's the rule now?

> Expected: commit 7d5b9e1efd, git rm -r used to untrack .openclaw-backups/, deleted entire repo structure, rule is git rm --cached only

---

## Category 2: Technical Specifics (fact-checking)

**Q4.** What was wrong with the streaming classifier and how was it fixed? What was the actual bug?

> Expected: len > 20 gate was dropping short valid narratives; removed the min-length gate

---

**Q5.** Why does the jleechanclaw supervisor only mark a task done when the branch is reviewable — not just when the session exits?

> Expected: Prevent premature task_finished; session exit != work reviewable on origin; hardened in W11

---

**Q6.** What is DISPATCHING state in the session registry and why does it exist?

> Expected: Atomic state to prevent double-dispatch; ORCH-qxw; prevents two agents spawning for same bead

---

## Category 3: Cross-repo Patterns (synthesis)

**Q7.** Which features were built in worldai_claw first and then ported to worldarchitect.ai?

> Expected: Dragon welcome screen, ember particle background, theme palette (Arcane Scholar), Ralph dashboard/scripts

---

**Q8.** What automation toolchains have been validated for PR fixing, and when did we test each one?

> Expected: gemini-automation-commit, codex-automation-commit (W03 2026), copilot, CodeRabbit

---

## Category 4: "Replace Me" Quality (judgment)

**Q9.** If a new CI failure shows up on worldarchitect.ai right now, what's the correct response based on past patterns?

> Expected: Investigate root cause first, don't retry blindly; check if streaming/classifier related; real fix not workaround

---

**Q10.** Jeffrey is about to merge a PR that has tests but they're all mocked. What would he say?

> Expected: Real tests only — no mocks, monkeypatching, stub registries; this is a hard rule; don't merge

---

## Category 5: Gotchas (adversarial — should fail gracefully)

**Q11.** What is the worldai_claw Dolt server port and why is that specific number?

> Expected: Should say "I don't know" or "not in memory" — this detail is NOT in the memory files

---

**Q12.** What did Jeffrey work on in week 7 of 2026?

> Expected: Should say no memory for that week — W07 file doesn't exist

---

## Results

| Q | Pass/Fail | Notes |
|---|-----------|-------|
| Q1 | PASS | Correct: 2026-03-04, centralize scheduling, avoid crontab drift |
| Q2 | PASS | Correct: MC decommissioned, mctrl is canonical path |
| Q3 | PARTIAL | Only got "archive vs git rm" pattern — didn't surface 7d5b9e1efd incident details |
| Q4 | PASS | Exact: len > 20 gate dropped short valid narratives, gate removed |
| Q5 | PASS | Correct: prevent premature closure, must be reviewable on origin |
| Q6 | FAIL | "Not enough explicit memory" — DISPATCHING state not in synthesized summaries |
| Q7 | PASS | Correct: Arcane Scholar palette, dragon/ember assets, FOUC prevention |
| Q8 | PASS | Correct: gemini + codex dual-tool validated W03 2026 |
| Q9 | PASS | Correct pattern: fetch logs, root cause, don't merge until blockers clear |
| Q10 | PASS | High confidence: "real tests only, no mocks" |
| Q11 | PASS (graceful fail) | Correctly said "I don't know" — didn't hallucinate |
| Q12 | PASS (graceful fail) | Correctly said "no W07 memory file" — didn't hallucinate |
