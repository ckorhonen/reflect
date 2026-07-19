# Applied Improvements

| Date | Lane | Change | Target | Status | Evidence |
| --- | --- | --- | --- | --- | --- |
| 2026-07-19 | script | Strip ANSI escape sequences in error-signature normalization | skills/reflect-skills/scripts/scan_sessions.py | applied | dogfood scan of 15 real sessions produced garbled signature rows from TUI tool output; clean after fix |
| 2026-07-19 | script | Fixture-based deterministic test suite replacing repeated manual smoke-testing of both scripts | tests/test_scripts.py | applied | both scripts were hand-smoke-tested twice during initial development; now 15 checks run in CI |
