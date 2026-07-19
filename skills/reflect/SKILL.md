---
name: reflect
description: >-
  Review a work session, transcript, or tool-call log and compound the learnings
  into durable improvements: agent rules (AGENTS.md/CLAUDE.md), new or updated
  skills, slash commands, deterministic scripts, sub-agent delegation, and
  context-bloat reduction. Use when the user says "reflect", at the end of a
  work session, on a schedule, or when asked how to make the agent faster,
  cheaper, or more reliable in this project. Do not use for ordinary code
  review unless the requested output is agent/process improvement.
---

# Reflect

Turn one session's friction into every future session's head start. Reflect
reviews what actually happened — corrections, retries, rediscovered facts,
wasted tokens — and converts it into small, concrete improvements that
compound: rules, skills, commands, scripts, delegation, and leaner context.

Designed to be hands-off: run it at the end of a session or on a schedule,
and it applies safe improvements itself, queues risky ones as proposals, and
tracks everything in `.reflect/` so the next run builds on the last.

## Inputs

Accept any of these; with no argument, reflect on the current conversation
and working directory:

- The current visible session (default).
- A path to a session transcript (JSONL or plain text).
- A pasted transcript or log excerpt.
- A scope hint like "last 3 sessions" or "this week" when state exists.

For JSONL transcripts, build a neutral inventory first instead of reading the
raw file:

```bash
python3 scripts/session_inventory.py <transcript.jsonl>
```

(Resolve `scripts/` relative to this skill's directory.) The inventory shows
turns, tool-call frequency, errors/retries, and the largest tool outputs —
use it to target which raw evidence to read. Never keyword-scan a whole
transcript.

## State: the `.reflect/` folder

Cross-session memory lives in a `.reflect/` directory:

- In a git project: `.reflect/` at the repo root (commit it — it is shared
  team memory — unless the project prefers it ignored).
- Outside a project: `~/.reflect/` for cross-project patterns.

Files (create on first run; formats in `reference/state-format.md`):

- `observations.md` — tentative patterns seen once or twice, not yet worth a
  rule. Promote after repeated sightings; prune when stale.
- `applied.md` — ledger of every improvement applied or proposed: date,
  lane, target file, status (`applied` / `proposed` / `verified` / `pruned`).

Read both files before analyzing so you promote repeat observations instead
of re-deriving them, and never re-apply something already logged.

## Workflow

1. **Inventory.** Establish scope. Run the inventory script for JSONL input;
   for the live session, review it directly. Read `.reflect/` state.
2. **Find signals.** Look for: repeated user corrections; wrong first
   assumptions; facts about the environment rediscovered by trial and error;
   the same multi-step sequence performed manually more than once; fragile or
   noisy commands; verbose tool output dominating context; work a smaller
   model could have done; missing validation before "done" claims.
3. **Classify into lanes.** Assign each signal to one improvement lane (see
   below and `reference/improvement-taxonomy.md`). One signal, one lane, one
   smallest-possible change.
4. **Gate.** Keep a candidate only if it is evidence-backed (cite the moment
   in the session), durable (still true in 3 months), non-duplicate (check
   the target file and `applied.md`), and actionable (imperative and
   testable, not vague encouragement). Single sightings of a maybe-pattern
   go to `observations.md`, not into rules.
5. **Apply or propose.** Apply low-risk improvements directly (see Autonomy
   below). Record risky ones as `proposed` in `applied.md` with a ready-to-
   apply diff or file body. If the user asked for analysis only, propose
   everything.
6. **Log and report.** Append to `applied.md`, update `observations.md`,
   then report using the Output format.

## Improvement lanes

Full guidance with worked examples: `reference/improvement-taxonomy.md`.

1. **Agent rules** — additions to the project's `AGENTS.md` or `CLAUDE.md`
   (follow whichever the repo already uses; offer to create `AGENTS.md` if
   neither exists). For conventions, commands, and constraints the agent
   should never rediscover.
2. **Skills** — create or edit a skill when a workflow has enough steps or
   judgment to deserve its own trigger. Prefer updating an existing skill
   over creating a near-duplicate, and check the ecosystem
   (`npx skills find <keywords>`) before authoring from scratch.
3. **Slash commands** — when the user keeps typing variants of the same
   request, create a command file so it becomes one keystroke of intent.
4. **Deterministic scripts** — when the agent repeats fragile parsing,
   scoring, checking, or formatting by hand, encode it as a small script and
   add a rule or skill line naming when to run it.
5. **Sub-agent delegation** — when bounded, verifiable work ran in the main
   thread, recommend routing it to a sub-agent — ideally a smaller, cheaper
   model (Haiku-class / mini-class) — so the main thread orchestrates
   instead of executes.
6. **Context-bloat reduction** — when a tool's verbose output dominated
   context, wrap it: quieter flags, output-to-file plus targeted reads, a
   filtering wrapper script, or a hook that trims known-noisy tools.
7. **Observation** — real but unproven pattern: log it to `observations.md`
   with a sighting count.
8. **No action** — one-off, already documented, or too speculative. Say so
   explicitly; a confident no-change call is a valid outcome.

## Autonomy boundaries

Hands-off means safe-by-default, not unlimited:

- **Apply directly:** additive edits to `AGENTS.md`/`CLAUDE.md`; new skill,
  command, or script files; edits to files reflect itself created earlier
  (check `applied.md`); all `.reflect/` state.
- **Propose only:** rewriting or deleting content reflect did not create;
  changes to hooks, settings, permissions, or CI; anything touching secrets,
  deploy, or external services; large restructures.
- **Never:** delete user content, edit outside the project (except
  `~/.reflect/`), or store secrets/credentials/personal message text in any
  state file or report.

## Output format

```markdown
## Reflection

**Applied**
| Lane | Change | Target | Evidence |
| --- | --- | --- | --- |

**Proposed** (ready to apply on approval)
| Lane | Change | Target | Why gated |
| --- | --- | --- | --- |

**Observations logged** — n new, n promoted, n pruned

**No-change calls**
- <signal considered and rejected, with reason>
```

Every row cites evidence from the session. If nothing cleared the gate,
report that plainly — an empty reflection that keeps state clean beats a
noisy one that clutters it.

## Companions

- `reflect-feedback` — audits `applied.md`: are past improvements actually
  firing, or dead weight? Run weekly or every ~10 sessions.
- `reflect-memory` — lifecycle for accumulated state and rules: dedupe,
  merge, expire, resolve contradictions. Run monthly or when files feel
  bloated.
- `reflect-skills` — scans local session logs across many sessions for
  recurring failure patterns and manages the skill portfolio: install,
  create, fix, or remove skills. Use it when the evidence spans sessions
  rather than living in this one.
