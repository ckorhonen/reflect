# Improvement Taxonomy

Detailed guidance for classifying reflection signals into lanes. Each lane
lists the signal that selects it, what a good extraction looks like, and a
worked example. The unit of output is always the smallest change that would
have prevented the friction.

## 1. Agent rules (AGENTS.md / CLAUDE.md)

**Signal:** the agent made a wrong first assumption a one-line rule would
have prevented; the user repeated a correction they have given before; an
environment fact (build command, port, tool quirk, naming convention) was
rediscovered by trial and error.

**Extraction:** one imperative, testable sentence in the project's agent
instructions file. Follow the file the repo already uses; if neither
`AGENTS.md` nor `CLAUDE.md` exists, offer to create `AGENTS.md`. Keep rules
in existing sections; create a section only when none fits.

**Good:** `Run tests with 'bun test --timeout 30000'; plain 'bun test' hangs
on the websocket suite.`
**Bad:** `Be careful with tests.` (not testable, prevents nothing)

**Test:** would this rule, present at session start, have changed the
agent's first attempt? If not, it is noise.

## 2. Skills (create or edit)

**Signal:** a workflow required multiple steps, judgment calls, or discovered
knowledge, and would take a future agent real effort to re-derive; or an
existing skill under- or over-triggered because its description is vague.

**Extraction:** a new `SKILL.md` in the project's skills directory, or an
edit to an existing one. The description drives matching — include exact
symptoms, error messages, and "use when" conditions. Before creating,
search existing skills; prefer updating over near-duplicating.

**Good description:** `Debug getServerSideProps errors in Next.js. Use when
a page shows a generic error but the browser console is empty, or API
routes return 500 with no details.`
**Bad description:** `Helps with Next.js problems.`

Rule vs. skill: a rule is one sentence the agent should always know; a
skill is a procedure worth loading only when triggered. If it fits in a
sentence, it is a rule.

## 3. Slash commands

**Signal:** the user has typed variants of the same request across sessions
("summarize this PR the usual way", "do the weekly cleanup"), or a workflow
always starts with the same parameterized prompt.

**Extraction:** a command file in the project's commands directory (for
Claude Code, `.claude/commands/<name>.md`) containing the full prompt with
`$ARGUMENTS` where the variable part goes. Name it what the user would
naturally type.

**Example:** user repeatedly asks for release notes in a house style →
`.claude/commands/release-notes.md` capturing the style rules once.

## 4. Deterministic scripts

**Signal:** the agent performed the same parsing, counting, validation,
scoring, or formatting by hand more than once; output from a hand-rolled
step varied between runs; a multi-command pipeline was reconstructed from
scratch each time.

**Extraction:** a small script (prefer stdlib-only, no new dependencies)
committed to the project's scripts directory, plus a rule or skill line
naming exactly when to run it. The script owns the repeatable mechanics;
the model keeps the judgment.

**Test:** could this step's correctness be checked without an LLM? If yes,
it should not be done by an LLM twice.

## 5. Sub-agent delegation and model routing

**Signal:** the main thread spent many turns on bounded, verifiable work —
bulk file reads, summarization, mechanical edits across files, triage,
classification — while higher-judgment work waited; or a task's output was
fully checkable (tests, schema, diff review) making cheap-model errors
recoverable.

**Extraction:** a rule or skill line naming the task shape, the delegation
("run X in a sub-agent"), the model class, and the validation boundary.
Name model classes, not versions — "smallest model that passes the
validation" ages better than a model ID:

- **Small/fast (Haiku-class, mini-class):** extraction, triage,
  summarization, classification, mechanical transforms — anything
  deterministically checkable.
- **Mid (Sonnet-class):** scoped implementation with tests, structured
  research, first-pass review.
- **Frontier:** ambiguous judgment, architecture, security, final
  synthesis — and orchestration of the above.

The compounding goal: each reflection nudges the main thread further
toward orchestrator — dispatching bounded work down, keeping judgment.
Every delegation suggestion must include its validation boundary; cheap
execution without a checkable result is not a win.

## 6. Context-bloat reduction

**Signal:** the session inventory shows a few tool calls dominating context
(one giant `git diff`, a full test log, a verbose API response); the same
large output was re-fetched instead of saved; context filled with content
never referenced afterward.

**Extraction ladder** (prefer the earliest that works):

1. **Quieter invocation:** `--stat`, `--name-only`, `--quiet`, `-c` counts,
   path-scoping, `head`/`tail` slices. Encode as a rule: "use `git diff
   --stat` first; full diff only for files you will edit."
2. **Output to file + targeted reads:** redirect big output to a log, then
   grep/read the relevant slice. Rule: "run the suite with `> test.log
   2>&1`, then read failures only."
3. **Wrapper script:** when the same tool is always noisy, a script that
   runs it and emits only the signal (failures, counts, top-N). This is
   lane 4 applied to context.
4. **Hook or tool-level cap:** for harnesses that support hooks, a
   PostToolUse-style filter that truncates or summarizes known-noisy tools.
   Propose, don't auto-apply — hooks are configuration.

Report bloat findings with numbers from the inventory ("this call was ~18%
of session tokens"), not vibes.

## 7. Observations

**Signal:** something looks like a pattern but has appeared once, or twice
with differing shape. Recording it as a rule now would be speculation.

**Extraction:** a row in `.reflect/observations.md` with the pattern, the
evidence, and a sighting count. On later reflections, increment sightings;
promote to a real lane at ~3 consistent sightings; prune observations
untouched after ~90 days or contradicted by newer evidence.

## 8. No action

**Signal:** one-off events, things already documented (check before
claiming), tool failures outside anyone's control, or friction that cost
less than any fix would.

**Extraction:** a line in the report's "No-change calls" with the reason.
This is a first-class outcome — it is what keeps the other seven lanes
trustworthy.
