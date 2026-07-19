#!/usr/bin/env python3
"""Behavioral eval for the reflect skill: planted-signal grading.

Feeds the reflect SKILL.md plus a fixture transcript with known planted
signals to an agent CLI, then grades the resulting reflection report with
deterministic keyword checks (no LLM judge). This evaluates the skill's
prose behavior, complementing tests/test_scripts.py which covers the
deterministic helpers.

Usage:
    python3 evals/run_eval.py                       # uses: claude -p
    python3 evals/run_eval.py --agent "claude -p --model haiku"
    python3 evals/run_eval.py --report out.md       # grade a saved report
    python3 evals/run_eval.py --print-prompt        # show prompt, no run

Costs one model call per run, so it is NOT wired into CI — run it after
changing skills/reflect/SKILL.md. Exit 0 = all expectations met.
"""

import argparse
import json
import os
import shlex
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "reflect", "SKILL.md")
FIXTURE = os.path.join(ROOT, "evals", "fixtures", "planted_session.jsonl")
EXPECTED = os.path.join(ROOT, "evals", "expected.json")


def build_prompt():
    skill = open(SKILL).read()
    transcript = open(FIXTURE).read()
    return (
        "You are an agent running the following skill. Apply it exactly as "
        "written, in REPORT-ONLY mode: do not read or write any files, do "
        "not run tools; base the reflection purely on the transcript below "
        "and produce the skill's Output format as markdown.\n\n"
        "----- SKILL.md -----\n" + skill +
        "\n----- SESSION TRANSCRIPT (JSONL) -----\n" + transcript +
        "\n----- END TRANSCRIPT -----\n\n"
        "Produce the reflection report now."
    )


def grade(report):
    spec = json.load(open(EXPECTED))
    text = report.lower()
    passed, failed = [], []

    for exp in spec["expectations"]:
        ok_all = all(k.lower() in text for k in exp.get("must_match_all", []))
        any_terms = exp.get("must_match_any", [])
        ok_any = (not any_terms) or any(k.lower() in text for k in any_terms)
        (passed if (ok_all and ok_any) else failed).append(exp["name"])

    for rej in spec.get("must_not", []):
        hit = all(k.lower() in text for k in rej.get("reject_if_all", []))
        (failed if hit else passed).append(rej["name"])

    return passed, failed


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--agent", default="claude -p",
                    help="agent command reading prompt on stdin (default: 'claude -p')")
    ap.add_argument("--report", help="grade an existing report file instead of running")
    ap.add_argument("--print-prompt", action="store_true")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()

    if args.print_prompt:
        print(build_prompt())
        return 0

    if args.report:
        report = open(args.report).read()
    else:
        cmd = shlex.split(args.agent)
        print("running: %s  (this makes one model call)" % args.agent)
        try:
            proc = subprocess.run(cmd, input=build_prompt(), text=True,
                                  capture_output=True, timeout=args.timeout)
        except FileNotFoundError:
            print("agent command not found: %s" % cmd[0], file=sys.stderr)
            print("re-run with --agent '<your agent CLI> -p' or grade a "
                  "saved report via --report", file=sys.stderr)
            return 2
        except subprocess.TimeoutExpired:
            print("agent timed out after %ds" % args.timeout, file=sys.stderr)
            return 2
        if proc.returncode != 0:
            print("agent failed: %s" % proc.stderr[:500], file=sys.stderr)
            return 2
        report = proc.stdout
        out_path = os.path.join(ROOT, "evals", "last_report.md")
        open(out_path, "w").write(report)
        print("report saved to %s (%d chars)" % (out_path, len(report)))

    passed, failed = grade(report)
    print()
    for name in passed:
        print("PASS  %s" % name)
    for name in failed:
        print("FAIL  %s" % name)
    print()
    print("%d/%d expectations met" % (len(passed), len(passed) + len(failed)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
