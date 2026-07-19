---
name: reflect-memory
description: >-
  Lifecycle maintenance for accumulated agent memory: dedupe, merge, expire,
  and resolve contradictions across AGENTS.md/CLAUDE.md agent rules,
  .reflect/ state, and other agent instruction files reflect maintains. Use
  monthly, when instruction files feel bloated or contradictory, when the
  agent cites stale rules, or after many reflect runs have accumulated. Not
  for extracting new learnings — that is the reflect skill.
---

# Reflect Memory

Compounding has a failure mode: unbounded growth. Rules pile up, duplicate
each other, go stale, and start contradicting — and every one of them is
loaded into context on every session. This skill is the garbage collector
and compactor for the memory reflect builds.

## Surfaces

Work over, in order of impact:

1. The project's `AGENTS.md` / `CLAUDE.md` (agent-rule sections).
2. `.reflect/observations.md` and `.reflect/applied.md`.
3. Skill descriptions and command files reflect maintains (per the ledger).
4. `~/.reflect/` when run outside a project or when asked.

Only restructure freely inside `.reflect/`. For instruction files, apply
safe mechanical fixes directly (exact duplicates, dead references) and
propose everything judgment-shaped.

## Workflow

1. **Inventory the load.** Measure each surface: line counts, rule counts,
   and rough token estimate (chars/4, labeled as estimate). This gives the
   before/after for the report.

2. **Find decay**, in five classes:
   - **Duplicates** — same rule stated twice, or a rule restating harness
     or tool defaults.
   - **Merge candidates** — three narrow rules that are one general rule
     (e.g., per-command timeout rules → one testing section).
   - **Stale** — references to files, tools, commands, or versions that no
     longer exist; check, don't assume.
   - **Contradictions** — rules that disagree with each other or with
     observed recent behavior; the newer, evidence-backed one usually wins,
     but flag rather than silently pick when both look intentional.
   - **Wrong altitude** — session-specific trivia in durable files, or a
     paragraph-long rule that should be a skill (and vice versa).

3. **Fix.** Apply direct fixes within boundaries; write proposals for the
   rest (into `.reflect/applied.md` as `proposed` rows, long bodies under
   `.reflect/proposals/`). Every removal or merge must preserve meaning —
   when in doubt, propose.

4. **Compact state.** In `observations.md`, prune expired rows (untouched
   ~90 days). In `applied.md`, collapse ancient `pruned` rows into a single
   archive line per quarter; never drop `verified` history.

5. **Report.**

```markdown
## Memory Maintenance

**Load**: <surface>: ~n tokens → ~n tokens (estimates)

**Fixed** — duplicates removed, merges applied, stale refs corrected
**Proposed** — contradictions and judgment merges awaiting a decision
**State** — observations pruned n, ledger compacted n rows
```

## Boundaries

- Never delete a rule you cannot show is duplicated, stale, or superseded —
  "seems unnecessary" is a proposal, not a deletion.
- Preserve authorship: content the user wrote by hand gets propose-only
  treatment even inside sections reflect usually maintains.
- Keep a one-line dated note at the top of `applied.md` after each pass so
  cadence is visible to future runs.
