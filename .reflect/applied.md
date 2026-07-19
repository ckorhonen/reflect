# Applied Improvements

> Feedback pass 2026-07-19: both prior rows graded `verified` — the ANSI fix
> is exercised by CI and two subsequent real scans; the test suite fired on
> every push (4 green CI runs). Evidence quality: observed.

| Date | Lane | Change | Target | Status | Evidence |
| --- | --- | --- | --- | --- | --- |
| 2026-07-19 | script | Negation-aware error detection ("0 error(s)", "no leaks found" no longer flagged) in both analyzers; 4 new tests | skills/*/scripts | applied | observation hit 3rd sighting in a 40-session scan (gitleaks + lint success output flagged); Bash false positives dropped 276→247 |
| 2026-07-19 | script | Strip ANSI escape sequences in error-signature normalization | skills/reflect-skills/scripts/scan_sessions.py | verified | dogfood scan of 15 real sessions produced garbled signature rows from TUI output; clean in all scans since; regression-tested in CI |
| 2026-07-19 | script | Fixture-based deterministic test suite replacing repeated manual smoke-testing of both scripts | tests/test_scripts.py | verified | fired on every push; 4 green CI runs; now 19 checks |
