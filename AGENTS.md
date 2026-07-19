# reflect — repo conventions

This repo publishes agent skills to the open skills ecosystem
(`npx skills add ckorhonen/reflect`). Rules for working in it:

## Portability is the contract

- No machine-specific or user-specific paths, tools, or assumptions in any
  skill, script, or doc. Standard harness locations (`~/.claude`,
  `~/.codex`, `~/.reflect`) are allowed but must degrade gracefully when
  absent.
- Scripts are Python 3 stdlib-only, compatible with Python 3.9 (stock macOS
  `python3`). No dependencies, no `pip install`.
- Each skill directory is self-contained: skills can be installed
  individually, so never reference another skill's files at runtime —
  companions are referenced by name only.

## Layout

- `skills/<name>/SKILL.md` — one skill per directory; frontmatter needs
  `name` (matching the directory) and a symptom-rich `description`.
- Keep SKILL.md lean and imperative; long-form guidance goes in the skill's
  `reference/`, deterministic helpers in its `scripts/`.

## Validation

Before committing:

```bash
python3 -m py_compile skills/*/scripts/*.py
python3 - <<'EOF'
import glob, sys
for path in glob.glob("skills/*/SKILL.md"):
    head = open(path).read().split("---")
    assert len(head) >= 3, path + ": missing frontmatter"
    front = head[1]
    for field in ("name:", "description:"):
        assert field in front, path + ": missing " + field
print("frontmatter ok")
EOF
```

Smoke-test scripts against a real local transcript when available; label
that as a local check, not CI.

After changing any SKILL.md, run the behavioral eval (one model call, not
in CI): `python3 evals/run_eval.py` — it feeds a planted-signal transcript
to an agent running the skill and grades the report deterministically.

## Style

- Skills speak to the agent in the imperative; the README speaks to humans.
- Model references use classes (Haiku-class, mini-class), never version
  IDs that will stale.
- Every autonomy claim in a SKILL.md must match the safety model in the
  README; update both together.
