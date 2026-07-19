# reflect

**Skills that make your agent better at being your agent.**

Every session with a coding agent produces two things: the work, and a trail
of friction — corrections you had to repeat, facts the agent rediscovered by
trial and error, tokens burned on output nobody read. The work ships. The
friction evaporates, and you pay for it again tomorrow.

`reflect` is a family of agent skills that captures that friction and
compounds it into durable improvements. Run it at the end of a session or on
a schedule; it applies safe improvements itself, queues risky ones for your
approval, and tracks everything so the next run builds on the last.

## Install

```bash
# everything
npx skills add ckorhonen/reflect

# or individually
npx skills add ckorhonen/reflect@reflect
npx skills add ckorhonen/reflect@reflect-feedback
npx skills add ckorhonen/reflect@reflect-memory
npx skills add ckorhonen/reflect@reflect-skills
```

Works with any harness that reads the open [SKILL.md format](https://skills.sh)
(Claude Code, Codex, and others).

## The loop

```
   session ──▶ signals ──▶ classify ──▶ gate ──▶ apply ──▶ next session
      ▲            corrections    8 lanes    evidence,   rules, skills,     │
      │            retries        (below)    durability  commands, scripts  │
      └────────────────────── compounds ◀──────────────────────────────────┘
```

`reflect` reviews what actually happened and routes each finding into one of
eight **improvement lanes**:

| Lane | What it produces |
| --- | --- |
| Agent rules | One-line additions to `AGENTS.md` / `CLAUDE.md` the agent should never rediscover |
| Skills | New or sharpened `SKILL.md` files for workflows worth a trigger |
| Slash commands | Repeated requests turned into one keystroke of intent |
| Deterministic scripts | Fragile hand-repeated parsing/checking encoded as code |
| Sub-agent delegation | Bounded work routed to smaller, cheaper models; the main thread orchestrates |
| Context-bloat reduction | Verbose tool output wrapped, filtered, or capped |
| Observations | Maybe-patterns logged until they earn promotion |
| No action | A confident, recorded "not worth it" |

Selectivity is the core mechanic: every change must be evidence-backed,
durable, non-duplicate, and testable. An empty reflection beats a noisy one.

## The skills

### `reflect` — the core loop

Reviews the current session (or a transcript you point it at), finds the
signals, and applies the smallest change per lane. Ships
`session_inventory.py`, a deterministic transcript analyzer that surfaces
tool errors and the largest context hogs so the model reads evidence, not
the whole log.

### `reflect-feedback` — did it work?

Reflection without feedback just accumulates. This skill audits the ledger
of past improvements: verifies the ones that demonstrably fire, watches the
young ones, and prunes dead weight. Honest about evidence quality —
`observed`, `inferred`, or `unknown`, never invented.

### `reflect-memory` — the garbage collector

Compounding's failure mode is unbounded growth. This skill dedupes, merges,
expires, and de-contradicts accumulated rules and state, and reports the
context-token load before and after.

### `reflect-skills` — the portfolio manager

Scans your local session logs (Claude Code, Codex) across weeks, clusters
recurring failure patterns, and treats your skill collection as the fix
surface: fix a vague trigger description, install an existing ecosystem
skill (`npx skills find` before authoring), write a new one, or propose
removing one that misfires. Ships `scan_sessions.py` for the cross-session
aggregation.

## State: the `.reflect/` folder

Cross-session memory is plain markdown, readable and reviewable like any
other file:

- **In a project:** `.reflect/` at the repo root — commit it; it is shared
  team memory.
- **Outside a project:** `~/.reflect/` for cross-project patterns.

Two files: `observations.md` (tentative patterns with sighting counts) and
`applied.md` (a ledger of every improvement with status:
`proposed → applied → verified | pruned`). Format spec in
[`skills/reflect/reference/state-format.md`](skills/reflect/reference/state-format.md).

## Running it hands-off

The intended cadence:

- **`reflect`** — end of each working session, or scheduled daily.
- **`reflect-feedback`** — weekly, or every ~10 sessions.
- **`reflect-memory`** — monthly, or when instruction files feel heavy.
- **`reflect-skills`** — every week or two.

In Claude Code you can automate the session-end run with a hook or a
scheduled agent, e.g.:

```jsonc
// .claude/settings.json — nudge a reflection when a session ends
{
  "hooks": {
    "SessionEnd": [{
      "hooks": [{ "type": "command",
                  "command": "echo 'Consider running the reflect skill on this session.'" }]
    }]
  }
}
```

or simply end sessions with `/reflect`, or schedule
`claude -p "run the reflect skill on recent sessions"` via cron or your
harness's scheduler.

## Testing and evals

`tests/test_scripts.py` covers the deterministic helpers (runs in CI).
`evals/run_eval.py` covers the skill's *behavior*: it gives an agent the
reflect SKILL.md plus a transcript with planted signals (a repeated
correction, a context-hogging verbose log, a twice-repeated deploy
sequence, and a one-off distractor) and deterministically grades whether
the reflection surfaces each signal in the right lane — and skips the
distractor. One model call per run; not wired into CI.

## Safety model

- **Applies directly:** additive edits to agent instruction files; new
  skill/command/script files; its own `.reflect/` state and prior changes.
- **Proposes only:** rewriting or deleting anything it didn't create;
  hooks, settings, permissions, CI; skill installs and removals.
- **Never:** deletes user content, writes outside the project (except
  `~/.reflect/`), or stores secrets or personal transcript text in state.

## License

MIT
