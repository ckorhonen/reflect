---
name: reflect-feedback
description: >-
  Audit whether past reflect improvements are actually working. Reads the
  .reflect/applied.md ledger and checks each applied rule, skill, command, or
  script for evidence it fired and helped; grades entries verified, unused,
  or regressed, and prunes dead weight. Use on a schedule (weekly or every
  ~10 sessions), when the user asks "are these improvements working?", or
  before a reflect-memory consolidation pass. Requires prior reflect runs —
  if no .reflect/ ledger exists, run reflect first.
---

# Reflect Feedback

Reflection without feedback just accumulates. This skill closes the loop:
it checks whether the improvements reflect made are earning their keep, and
removes the ones that are not. Prefer a smaller ledger of verified
improvements over a large ledger of hopeful ones.

## Inputs

- `.reflect/applied.md` in the current project (or `~/.reflect/` when run
  outside one). If it does not exist, stop and suggest running `reflect`.
- Optionally, recent session transcripts or the current conversation as
  evidence of what fired.

## Workflow

1. **Read the ledger.** List every row with status `applied` or `verified`.
   Rows already `pruned` are skipped; rows `proposed` are surfaced at the
   end as a reminder queue.

2. **Check existence.** For each entry, confirm the target still exists and
   still contains the change (the rule line is present in AGENTS.md, the
   skill/command/script file exists). Missing → mark `pruned` with reason
   "target removed externally".

3. **Look for firing evidence.** For each surviving entry, gather what
   evidence is available:
   - Rules: did recent sessions follow the rule without being corrected?
     Was the friction it targeted absent?
   - Skills/commands: any sign of invocation (mentions in recent
     transcripts, session state, or the user's account)?
   - Scripts: executed recently, referenced by rules, or imported anywhere?
   - Delegation/context rules: did the pattern they encode show up (smaller
     outputs, sub-agent use)?

   Be honest about evidence quality. Label each judgment as `observed`
   (concrete evidence), `inferred` (indirect), or `unknown` (no evidence
   either way). Never invent usage.

4. **Grade.**
   - `verified` — observed or strongly inferred to fire and help.
   - keep as `applied` — unknown, but young (< ~30 days or < ~10 sessions).
   - `pruned` — unused past its window, superseded, or actively causing
     friction (e.g., a rule the user now contradicts). Remove the change
     from its target file when pruning a rule reflect itself added; for
     skills/commands/scripts, propose deletion rather than deleting.

5. **Update and report.** Rewrite the affected `Status` cells in
   `applied.md`, add a dated feedback note at the top of the file, and
   report:

```markdown
## Reflect Feedback

**Verified** (n) — working, keep
**Still watching** (n) — no evidence yet, within window
**Pruned** (n) — removed or proposed for removal, with reasons
**Proposal queue** (n) — proposed rows still awaiting a decision

Evidence quality: n observed / n inferred / n unknown
```

## Boundaries

- Edit only `.reflect/` state and content reflect itself added (per the
  ledger). Anything else is propose-only.
- Pruning removes a change and keeps its ledger row with the reason — the
  history of what did not work is itself a learning.
- If evidence is thin across the board, say so and recommend the cheapest
  instrumentation that would fix it (e.g., a rule that scripts log a line
  to `.reflect/` when run), rather than guessing.
