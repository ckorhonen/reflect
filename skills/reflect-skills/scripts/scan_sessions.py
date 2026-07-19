#!/usr/bin/env python3
"""Scan local agent session logs and aggregate failure/friction patterns.

Discovers recent JSONL transcripts from standard local locations (when they
exist) and any extra --root paths:

  - Claude Code: ~/.claude/projects/*/*.jsonl
  - Codex:       ~/.codex/sessions, ~/.codex/archived_sessions

Aggregates across sessions: tool-call volume, tool errors, repeated error
signatures, and the noisiest tools by estimated output tokens. Prints a
summary only — no raw transcript text beyond short normalized previews.

Usage:
    python3 scan_sessions.py [--days 14] [--root PATH ...] [--limit 200]

Token counts are estimates (chars / 4). Stdlib only.
"""

import argparse
import glob
import json
import os
import re
import sys
import time


def est_tokens(text):
    return len(text) // 4


def walk_strings(node, budget=100000):
    out = []
    stack = [node]
    total = 0
    while stack and total < budget:
        cur = stack.pop()
        if isinstance(cur, str):
            out.append(cur)
            total += len(cur)
        elif isinstance(cur, dict):
            stack.extend(cur.values())
        elif isinstance(cur, list):
            stack.extend(cur)
    return "".join(out)


ERROR_MARKERS = (
    "error", "traceback", "exception", "failed", "failure",
    "denied", "refused", "timed out", "timeout",
)


ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]|\[[0-9;]{1,6}m")


def normalize_signature(text):
    """Reduce an error preview to a stable signature for clustering."""
    text = ANSI_RE.sub("", text[:400])
    sig = " ".join(text[:200].split()).lower()
    sig = re.sub(r"/[^ ]+", "<path>", sig)          # paths
    sig = re.sub(r"\d+", "<n>", sig)                # numbers, line nos
    sig = re.sub(r"[a-f0-9]{8,}", "<hex>", sig)     # hashes, ids
    return sig[:120]


def discover(roots, days, limit):
    cutoff = time.time() - days * 86400
    home = os.path.expanduser("~")
    candidates = []
    default_globs = [
        os.path.join(home, ".claude", "projects", "*", "*.jsonl"),
        os.path.join(home, ".codex", "sessions", "**", "*.jsonl"),
        os.path.join(home, ".codex", "archived_sessions", "**", "*.jsonl"),
    ]
    patterns = default_globs + [os.path.join(r, "**", "*.jsonl") for r in roots]
    seen = set()
    for pattern in patterns:
        for path in glob.glob(pattern, recursive=True):
            base = os.path.basename(path)
            if base.startswith("history"):
                continue
            real = os.path.realpath(path)
            if real in seen:
                continue
            seen.add(real)
            try:
                mtime = os.path.getmtime(path)
            except OSError:
                continue
            if mtime >= cutoff:
                candidates.append((mtime, path))
    candidates.sort(reverse=True)
    return candidates[:limit]


def scan_file(path, tool_calls, tool_errors, tool_out_tokens, signatures):
    pending_tool = None
    session_errors = 0
    try:
        handle = open(path, "r", encoding="utf-8", errors="replace")
    except OSError:
        return None
    with handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except ValueError:
                continue
            if not isinstance(obj, dict):
                continue
            msg = obj.get("message") if isinstance(obj.get("message"), dict) else obj
            content = msg.get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                btype = block.get("type")
                if btype == "tool_use":
                    name = block.get("name", "unknown-tool")
                    tool_calls[name] = tool_calls.get(name, 0) + 1
                    pending_tool = name
                elif btype == "tool_result":
                    owner = pending_tool or "unknown-tool"
                    text = walk_strings(block)
                    tool_out_tokens[owner] = (
                        tool_out_tokens.get(owner, 0) + est_tokens(text)
                    )
                    lowered = text[:2000].lower()
                    is_err = bool(block.get("is_error")) or any(
                        m in lowered for m in ERROR_MARKERS
                    )
                    if is_err:
                        session_errors += 1
                        tool_errors[owner] = tool_errors.get(owner, 0) + 1
                        sig = normalize_signature(text)
                        if sig:
                            entry = signatures.setdefault(
                                sig, {"count": 0, "tool": owner, "sessions": set()}
                            )
                            entry["count"] += 1
                            entry["sessions"].add(os.path.basename(path))
    return session_errors


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--root", action="append", default=[],
                        help="extra directory to search (repeatable)")
    parser.add_argument("--limit", type=int, default=200,
                        help="max session files to scan (default 200)")
    parser.add_argument("--top", type=int, default=15)
    args = parser.parse_args()

    found = discover(args.root, args.days, args.limit)
    if not found:
        print("no session transcripts found in the last %d days" % args.days)
        print("searched: ~/.claude/projects, ~/.codex/sessions%s"
              % (", " + ", ".join(args.root) if args.root else ""))
        return 1

    tool_calls = {}
    tool_errors = {}
    tool_out_tokens = {}
    signatures = {}
    scanned = 0
    for _, path in found:
        result = scan_file(path, tool_calls, tool_errors,
                           tool_out_tokens, signatures)
        if result is not None:
            scanned += 1

    print("# Session Scan (last %d days; token counts are chars/4 estimates)"
          % args.days)
    print()
    print("sessions scanned: %d" % scanned)
    print()
    print("## Tool errors (errors / calls)")
    ranked = sorted(tool_errors, key=tool_errors.get, reverse=True)
    if not ranked:
        print("  none detected")
    for name in ranked[: args.top]:
        print("  %-28s %4d / %d" % (name, tool_errors[name],
                                    tool_calls.get(name, 0)))
    print()
    print("## Repeated error signatures (>= 2 occurrences)")
    repeated = [(v["count"], len(v["sessions"]), v["tool"], sig)
                for sig, v in signatures.items() if v["count"] >= 2]
    repeated.sort(reverse=True)
    if not repeated:
        print("  none repeated")
    for count, nsessions, tool, sig in repeated[: args.top]:
        print("  %3dx in %2d session(s)  [%s]  %s"
              % (count, nsessions, tool, sig))
    print()
    print("## Noisiest tools (est. output tokens)")
    for name in sorted(tool_out_tokens, key=tool_out_tokens.get,
                       reverse=True)[: args.top]:
        print("  %-28s ~%d tokens over %d calls"
              % (name, tool_out_tokens[name], tool_calls.get(name, 0)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
