# Natural Language Task Dispatch

**Goal:** Send a short natural-language message to openclaw and have the full
orchestration pipeline — openclaw → Mission Control → minimax agents — execute it
correctly without needing a hand-crafted prompt.

Example:
```
use the orchestration system with minimax agents to build the discord bot we discussed
```
...should just work.

---

## The Vision (Zoe Pattern)

The Elvis/@eRvissun setup (ref email 2026-03-01) captures this exactly:

> OpenClaw acts as the orchestration layer. It holds all business context — meeting notes,
> past decisions, what worked, what failed — and translates that into precise prompts for
> each coding agent. The agents stay focused on code. The orchestrator stays at the high
> strategy level.

The two-tier split:

| Layer | Holds | Does |
|-------|-------|------|
| openclaw (jleechanclaw) | Conversation history, prior decisions, project context | Expands short prompts → precise agent tasks |
| minimax agent | Task prompt only | Writes code, builds output |

The user should only ever need to speak to the top layer in natural language. The bottom
layer should never see an underspecified prompt.

---

## What's Missing Today

### 1. SOUL.md doesn't retrieve conversation context

When jleechanclaw gets "build the discord bot we discussed", it creates a Mission Control
task with that literal string as the title/description. The minimax agent receives:

```
Build the discord bot we discussed
```

...and has zero context about what was discussed.

**Fix needed:** SOUL.md should instruct jleechanclaw to:
- Recognize "we discussed" / "as discussed" / "from our conversation" triggers
- Fetch recent DM history (last N messages) from Slack
- Summarize the relevant spec into the MC task description before dispatching

### 2. No context attachment in MC task payload

The MC task schema only has `title` and `description`. There's no structured way to
attach supporting context (conversation excerpts, prior decisions, file references).

**Fix needed:** Add optional `context` field to MC task payload that gets prepended to
the agent prompt.

### 3. task_poller dispatches the raw prompt verbatim

`task_poller.py` sends `{title}: {description}` directly to the agent subprocess. No
expansion, no context injection.

**Fix needed:** task_poller should pass `context` field (if present) as additional stdin
or prepend it to the prompt.

---

## Target State

```
User → "build the discord bot we discussed"
         ↓
jleechanclaw (SOUL.md)
  - fetches last 20 DM messages
  - identifies discord bot spec: eng_qa agent, tool denylist,
    sandbox non-main, slash cmds /docs /status /reset
  - creates MC task with full spec in description
         ↓
Mission Control inbox
         ↓
task_poller.py → claudem (minimax)
  - receives full spec
  - builds /tmp/discord-eng-bot/openclaw.json
  - posts wc/verification output back to Slack
         ↓
User sees: config file + verification output in DM
```

---

## Immediate Discord Bot Project

What jleechanclaw needs to know to dispatch this correctly right now
(until the SOUL.md fix lands):

**Agent:** eng_qa
**Sandbox:** non-main, workspaceAccess none
**Tools allowed:** web_search, web_fetch only
**Tools blocked:** read, write, edit, exec, process, browser, canvas, nodes, cron, gateway
**Discord scopes:** message content, read/send/history only — no admin
**Guild policy:** allowlist (placeholder guild/channel IDs)
**Slash commands:** /docs, /status, /reset
**Anti-spam:** mention-required, short session TTL
**Output:** /tmp/discord-eng-bot/openclaw.json

---

## Beads

- `ORCH-w9e` — Natural language task dispatch (this feature)
