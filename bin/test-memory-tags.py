#!/usr/bin/env python3
"""Dry-run check that Claude Code tags memories per agents/AGENT.md.

Starts a fresh headless `claude -p` session from the repo root (so it loads the
real user-level CLAUDE.md and sees `agent-skills` as the project), hands it a
fixed set of candidate facts, and asks how it would tag each one -- no tool
calls, nothing written to the memory server. Each answer is scored against the
expected tag set (or a list of acceptable sets for genuinely ambiguous facts);
"ASK" means the fact needs Ray's consent first.

Usage: CLAUDE_CONFIG_DIR=~/.claude-personal bin/test-memory-tags.py [--runs 3] [--model sonnet]\n\nAnswers vary run to run, so use --runs to see per-case pass rates.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Expected value for facts that need a topic tag: exactly one tag the model names
# itself, and not one of the reserved ones.
TOPIC = "TOPIC"
RESERVED = {"general", "preference", "agent-skills", "coding", "science", "writing", "language", "travel"}

CASES = [
    # Cross-project facts get a topic tag the model names itself; the repo tag also fits here.
    ("Ray's Linux host runs LibreChat in Docker; the Mac connects to it over SSH.", [TOPIC, {"agent-skills"}]),
    # Ambiguous: a setup fact or a coding-tool preference -- either recalls sensibly.
    ("Ray does not use Zed's native agent; only Claude Code and LibreChat.", [TOPIC, {"agent-skills"}, {"preference", "coding"}]),
    ("The GPU server gpgpu2 needs /etc/resolv.conf linked to the systemd stub to resolve names.", TOPIC),
    # `general` is only for index memories pointing at a topic tag.
    ("Index: Ray's Japanese tax facts (year-end adjustment, tax return, stocks) are tagged `tax`; search it when taxes come up.", {"general"}),
    ("2026-10-28: chose bge-m3 on Cloudflare for this repo's memory service because memories are often Japanese.", {"agent-skills"}),
    ("This repo's memory sync stays at the default hourly pull; Ray found 5 minutes too frequent.", {"agent-skills"}),
    ("LibreChat in this repo reaches the memory server at http://mcp-memory:8000/mcp.", {"agent-skills"}),
    ("Ray prefers TypeScript over plain JavaScript for new code.", {"preference", "coding"}),
    ("Ray wants commit messages in the imperative mood.", {"preference", "coding"}),
    ("When learning physics, Ray wants step-by-step derivations with a running formula ledger.", {"preference", "science"}),
    ("Ray likes terse bullet-point docs with no marketing tone.", {"preference", "writing"}),
    ("Ray prefers window seats and avoids red-eye flights.", {"preference", "travel"}),
    ("When explaining Japanese, list kanji readings after the text, not inline.", {"preference", "language"}),
    # Project-specific preferences stay project-scoped: work-type tags are recalled in every project.
    ("For this repo, Ray wants every shared agent prompt kept under 200 words.", {"agent-skills"}),
    ("mcp-memory-service sync timing (2026-10-28): push ~5 s, pull hourly. Ray rejected a 5-minute pull as too frequent.", {"agent-skills"}),
    ("Ray lives in Tokyo.", "ASK"),
]

PROMPT = """Do not call any tools. This is a dry run of your memory rules.
For each candidate memory below, decide exactly what you would pass as `tags` to
`memory_store`, following your CLAUDE.md memory rules. The current project is the
working directory's repo. If a rule says you must ask Ray before storing it,
answer "ASK" instead of tags.

Reply with only a JSON object mapping each number to a list of tags or "ASK".

{cases}"""


def ask(model):
    cases = "\n".join(f"{i}. {fact}" for i, (fact, _) in enumerate(CASES, 1))
    cmd = ["claude", "-p", "--strict-mcp-config", PROMPT.format(cases=cases)]
    if model:
        cmd[1:1] = ["--model", model]
    out = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout
    match = re.search(r"\{.*\}", out, re.S)
    return json.loads(match.group(0)) if match else {}


def passes(got, expected) -> bool:
    if isinstance(expected, list):
        return any(passes(got, e) for e in expected)
    if got == "ASK" or expected == "ASK":
        return got == expected
    tags = set(got or [])
    if expected == TOPIC:
        return len(tags) == 1 and not tags & RESERVED
    return tags == expected


def main() -> int:
    args = sys.argv[1:]
    model = args[args.index("--model") + 1] if "--model" in args else None
    runs = int(args[args.index("--runs") + 1]) if "--runs" in args else 1

    results = [ask(model) for _ in range(runs)]
    all_ok = True
    for i, (fact, expected) in enumerate(CASES, 1):
        answers = [r.get(str(i)) for r in results]
        ok = sum(passes(a, expected) for a in answers)
        all_ok &= ok == runs
        print(f"{'PASS' if ok == runs else 'FAIL'} {ok}/{runs}  {i:>2}. {fact[:60]}")
        for a in answers:
            if not passes(a, expected):
                print(f"           expected {expected}, got {a}")
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
