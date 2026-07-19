#!/usr/bin/env python3
"""Build a neutral event inventory from an agent session transcript (JSONL).

Works with Claude Code session files and is tolerant of other JSONL agent
transcript shapes (one JSON object per line). Emits a compact summary so the
reviewing agent can target which raw evidence to read instead of scanning
the whole transcript.

Usage:
    python3 session_inventory.py <transcript.jsonl> [--top N]

Output sections:
  - totals: lines, turns by role, estimated tokens
  - tool usage: calls and estimated output tokens per tool
  - errors / retries: lines that look like failures
  - top N largest tool outputs (the context-bloat suspects)

Token counts are estimates (chars / 4) and labeled as such. Stdlib only.
"""

import argparse
import json
import sys


def est_tokens(text):
    return len(text) // 4


def walk_strings(node, budget=200000):
    """Concatenate string leaves of a JSON structure, bounded for safety."""
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


def looks_like_error(text):
    lowered = text[:2000].lower()
    return any(marker in lowered for marker in ERROR_MARKERS)


def classify(obj):
    """Return (role, tool_name, is_tool_result) for a transcript line."""
    role = obj.get("type") or obj.get("role") or "unknown"
    msg = obj.get("message") if isinstance(obj.get("message"), dict) else obj
    content = msg.get("content")
    tool_calls = []
    tool_results = []
    if isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")
            if btype == "tool_use":
                tool_calls.append(block.get("name", "unknown-tool"))
            elif btype == "tool_result":
                tool_results.append(block)
    return role, tool_calls, tool_results


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("transcript", help="path to a .jsonl transcript")
    parser.add_argument("--top", type=int, default=10,
                        help="how many largest outputs to list (default 10)")
    args = parser.parse_args()

    roles = {}
    tool_counts = {}
    tool_out_tokens = {}
    pending_tool = None  # name of most recent tool_use, to attribute results
    largest = []  # (tokens, line_no, tool, preview)
    errors = []
    total_tokens = 0
    line_no = 0
    parse_failures = 0

    try:
        handle = open(args.transcript, "r", encoding="utf-8", errors="replace")
    except OSError as exc:
        print("cannot open transcript: %s" % exc, file=sys.stderr)
        return 2

    with handle:
        for line in handle:
            line_no += 1
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except ValueError:
                parse_failures += 1
                continue
            if not isinstance(obj, dict):
                continue

            role, tool_calls, tool_results = classify(obj)
            roles[role] = roles.get(role, 0) + 1

            text = walk_strings(obj)
            tokens = est_tokens(text)
            total_tokens += tokens

            for name in tool_calls:
                tool_counts[name] = tool_counts.get(name, 0) + 1
                pending_tool = name

            for result in tool_results:
                out_text = walk_strings(result)
                out_tokens = est_tokens(out_text)
                owner = pending_tool or "unknown-tool"
                tool_out_tokens[owner] = tool_out_tokens.get(owner, 0) + out_tokens
                preview = " ".join(out_text[:120].split())
                largest.append((out_tokens, line_no, owner, preview))
                if result.get("is_error") or looks_like_error(out_text):
                    errors.append((line_no, owner, preview))

    largest.sort(reverse=True)
    largest = largest[: args.top]

    print("# Session Inventory (token counts are chars/4 estimates)")
    print()
    print("transcript: %s" % args.transcript)
    print("lines: %d  (unparseable: %d)" % (line_no, parse_failures))
    print("estimated total tokens: ~%d" % total_tokens)
    print()
    print("## Turns by role")
    for role in sorted(roles, key=roles.get, reverse=True):
        print("  %-16s %d" % (role, roles[role]))
    print()
    print("## Tool usage (calls / est. output tokens)")
    if not tool_counts and not tool_out_tokens:
        print("  no tool calls detected")
    for name in sorted(set(tool_counts) | set(tool_out_tokens),
                       key=lambda n: tool_out_tokens.get(n, 0), reverse=True):
        print("  %-28s %4d calls  ~%d tokens out"
              % (name, tool_counts.get(name, 0), tool_out_tokens.get(name, 0)))
    print()
    print("## Error-looking tool results: %d" % len(errors))
    for ln, owner, preview in errors[:20]:
        print("  line %-6d %-20s %s" % (ln, owner, preview[:80]))
    print()
    print("## Largest tool outputs (context-bloat suspects)")
    for tokens, ln, owner, preview in largest:
        share = (100.0 * tokens / total_tokens) if total_tokens else 0.0
        print("  ~%-7d tok  %4.1f%%  line %-6d %-20s %s"
              % (tokens, share, ln, owner, preview[:60]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
