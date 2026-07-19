#!/usr/bin/env python3
"""Fixture-based checks for the reflect script helpers. Stdlib only.

Run from the repo root:
    python3 tests/test_scripts.py
"""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "sample_session.jsonl")
INVENTORY = os.path.join(ROOT, "skills", "reflect", "scripts",
                         "session_inventory.py")
SCANNER = os.path.join(ROOT, "skills", "reflect-skills", "scripts",
                       "scan_sessions.py")

failures = []


def check(label, condition, detail=""):
    if condition:
        print("ok   %s" % label)
    else:
        print("FAIL %s  %s" % (label, detail))
        failures.append(label)


def run(cmd):
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def test_inventory():
    rc, out, err = run([sys.executable, INVENTORY, FIXTURE, "--top", "3"])
    check("inventory exits 0", rc == 0, err)
    check("inventory counts Bash calls", "Bash" in out and "2 calls" in out, out)
    check("inventory counts Read calls", "Read" in out and "1 calls" in out, out)
    check("inventory flags the error result",
          "Error-looking tool results: 1" in out
          or "Error-looking tool results: 2" in out, out)
    check("inventory finds cannot-find-module error",
          "cannot find module" in out.lower(), out)
    check("largest output is the verbose test log",
          "tests passed" in out.split("Largest tool outputs")[-1], out)
    check("inventory labels estimates", "estimate" in out.lower(), out)


def test_inventory_bad_input():
    rc, out, err = run([sys.executable, INVENTORY, "/nonexistent/x.jsonl"])
    check("inventory fails cleanly on missing file", rc != 0, out)


def test_scanner():
    # Point the scanner at the fixture dir via --root; default locations may
    # not exist on CI, which must be fine.
    fixture_dir = os.path.dirname(FIXTURE)
    rc, out, err = run([sys.executable, SCANNER, "--root", fixture_dir,
                        "--days", "36500", "--limit", "5"])
    check("scanner exits 0 with fixture root", rc == 0, err + out)
    check("scanner scans the fixture", "sessions scanned:" in out
          and "0" not in out.split("sessions scanned:")[1][:3], out)
    check("scanner attributes Bash error", "Bash" in out, out)
    check("scanner labels estimates", "estimate" in out.lower(), out)


def test_signature_normalization():
    sys.path.insert(0, os.path.dirname(SCANNER))
    import scan_sessions
    sig = scan_sessions.normalize_signature(
        "\x1b[31mError\x1b[0m at /Users/x/app.py line 42 hash deadbeef99")
    check("signatures strip ANSI codes", "\x1b" not in sig and "[31m" not in sig, sig)
    check("signatures normalize paths/numbers/hashes",
          "<path>" in sig and "<n>" in sig and "<hex>" in sig, sig)


def test_scanner_empty():
    rc, out, err = run([sys.executable, SCANNER, "--root",
                        os.path.join(ROOT, "tests"), "--days", "0"])
    check("scanner handles no-results without crashing", rc in (0, 1), err)


if __name__ == "__main__":
    test_inventory()
    test_inventory_bad_input()
    test_scanner()
    test_scanner_empty()
    print()
    if failures:
        print("%d failure(s): %s" % (len(failures), ", ".join(failures)))
        sys.exit(1)
    print("all checks passed")
