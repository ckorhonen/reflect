# Observations

| First seen | Last seen | Sightings | Pattern | Evidence |
| --- | --- | --- | --- | --- |
| 2026-07-19 | 2026-07-19 | 2 | session_inventory's error heuristic false-positives on tool results that merely contain marker words (e.g. a Read of a file discussing "errors"); consider weighting the is_error flag above keyword markers, or requiring markers near the start of output | smoke test flagged a SKILL.md Read as error-looking; cross-session scan attributed 29/103 Read calls as errors, mostly implausible |
