---
name: reflect-skills
description: >-
  Scan local agent session logs (Claude Code, Codex) across many sessions,
  cluster the common failure and friction patterns, then manage the skill
  portfolio to address them: find and install existing ecosystem skills,
  create or modify local skills, fix under- or over-triggering descriptions,
  and remove skills that misfire. Use when the user asks to scan session
  logs for failure patterns, audit or tune their skills, or asks why a skill
  never fires. For single-session extraction use reflect instead.
---

# Reflect Skills

The portfolio manager. Where `reflect` learns from one session, this skill
looks across your recent session history, finds what keeps going wrong, and
treats your installed skills as the fix surface: install one, write one,
sharpen one, or delete one.

## Step 1 — Discover and scan session logs

Find recent transcripts with the bundled scanner (resolve `scripts/`
relative to this skill's directory):

```bash
python3 scripts/scan_sessions.py --days 14
```

It searches the standard local locations when present — Claude Code
(`~/.claude/projects/*/`) and Codex (`~/.codex/sessions`,
`~/.codex/archived_sessions`) — plus any `--root` you pass, and aggregates
across sessions: tool-error counts, repeated error signatures, and the
noisiest tools. Treat its output as a map; open specific transcripts only
to confirm a pattern, and never copy raw transcript text, secrets, or
personal message content into any durable file.

Privacy rule: session logs are sensitive. Read locally, summarize
patterns, discard specifics.

## Step 2 — Cluster into failure patterns

Group what the scan surfaces into named patterns with counts, e.g.:

- "Agent hand-rolls PDF text extraction, fails, retries — 4 sessions"
- "Same 3-step deploy sequence reconstructed from scratch — 6 sessions"
- "Skill X never fired despite 5 sessions doing exactly its job"
- "Skill Y fired on unrelated requests twice and derailed the turn"

A pattern needs at least 2–3 independent sightings; single incidents go
back to `reflect`'s observation ledger, not here.

## Step 3 — Resolve each pattern via the portfolio

For each pattern, pick the cheapest fix that addresses it, in this order:

1. **Fix an existing local skill.** Under-triggering is usually a vague
   description — rewrite it with exact symptoms, error messages, and "use
   when" conditions. Over-triggering usually needs "do not use for..."
   exclusions.
2. **Install an ecosystem skill.** Search before authoring:

   ```bash
   npx skills find <pattern keywords>
   ```

   If a well-maintained skill matches, propose installing it
   (`npx skills add <owner/repo@skill>`) rather than writing a duplicate.
   Prefer skills whose scope matches the pattern narrowly.
3. **Create a new skill.** When the pattern is real, recurring, and nothing
   exists: author it following the ecosystem format (directory +
   `SKILL.md`, symptom-rich description). House it in the project for
   project patterns, user-level for cross-project ones.
4. **Remove or merge.** A skill that repeatedly misfires, duplicates
   another, or addresses a tool that no longer exists is context cost with
   no return. Propose removal with the evidence; delete only on approval.

If the fix is a rule, command, or script rather than a skill, hand the
finding to the `reflect` taxonomy instead of forcing it into this lane.

## Step 4 — Record and report

Log outcomes to `.reflect/applied.md` (project-level fixes) or
`~/.reflect/applied.md` (user-level), same ledger format as `reflect`.
Installs and removals are always `proposed` unless the user pre-approved
portfolio changes for the run.

```markdown
## Skill Portfolio Review

Scanned: n sessions over n days (n Claude Code, n Codex)

**Patterns found** (with sightings)
| Pattern | Sessions | Resolution | Status |
| --- | --- | --- | --- |

**Portfolio changes** — modified n, created n, install-proposed n,
removal-proposed n

**Healthy** — patterns checked with no action needed
```

## Boundaries

- Installing and removing skills changes what runs on every future session:
  propose with evidence, apply on approval.
- Modifying descriptions of skills you (the reflect family) previously
  created is fair game; modifying hand-written or third-party skills is
  propose-only.
- Never send transcript content anywhere external — ecosystem search
  queries are keywords, not log excerpts.
