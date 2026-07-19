# `.reflect/` State Format

Cross-session memory for the reflect skill family. Plain markdown so humans
can read, edit, and review it like any other file.

## Location

- Inside a git project: `.reflect/` at the repo root. Commit it by default —
  it is shared team memory. Add it to `.gitignore` only if the project
  treats agent state as personal.
- Outside a project (or for cross-project patterns): `~/.reflect/`.

When both exist, project state wins for project learnings; reserve the home
folder for patterns that are genuinely about the user or machine, not the
repo.

## `observations.md`

Tentative patterns — seen, not yet proven. One table:

```markdown
# Observations

| First seen | Last seen | Sightings | Pattern | Evidence |
| --- | --- | --- | --- | --- |
| 2026-07-01 | 2026-07-18 | 2 | User rewrites summaries into bullet form | sessions 07-01, 07-18 |
```

Rules:

- One row per pattern. On re-sighting, update `Last seen` and increment
  `Sightings` — never add a duplicate row.
- At ~3 consistent sightings, promote to a real improvement lane and move
  the row's outcome to `applied.md`.
- Prune rows untouched for ~90 days or contradicted by newer evidence.
- Evidence is a short pointer (date, file, moment) — never raw transcript
  text.

## `applied.md`

Ledger of every improvement applied or proposed. One table, newest first:

```markdown
# Applied Improvements

| Date | Lane | Change | Target | Status | Evidence |
| --- | --- | --- | --- | --- | --- |
| 2026-07-19 | rule | Test-timeout rule added | AGENTS.md | applied | 3 hung runs this session |
| 2026-07-19 | script | Proposed log-filter wrapper | scripts/testlog.sh | proposed | test log was 40% of context |
```

Status lifecycle:

- `proposed` — recorded with a ready-to-apply body; awaiting approval.
- `applied` — change is live in the target file.
- `verified` — `reflect-feedback` later found evidence it fired and helped.
- `pruned` — removed as dead weight or superseded; keep the row, note why.

Rules:

- Every reflect run appends here, even if only to record no-change (a
  single `none` row per run is fine and keeps cadence visible).
- For `proposed` rows, put the full proposed content in a fenced block
  directly under the table row's section, or in
  `.reflect/proposals/<slug>.md` when it is long.
- Never store secrets, credentials, or personal message text.

## `proposals/` (optional)

Long-form proposed changes referenced from `applied.md`, one file per
proposal, deleted when applied or rejected.
