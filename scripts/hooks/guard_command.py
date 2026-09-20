#!/usr/bin/env python3
"""PreToolUse guard for Bash: deny the git commands the persona says are never allowed.

Denied outright (no asking): force-push, hard reset, history rewrite, --no-verify.
Everything else passes through untouched; the persona's "ask first" list is a
conversation rule, not a hook.

Reads the hook payload on stdin: Claude Code's (`tool_input.command`) or Copilot's
(`toolArgs` / `tool_args`, object or JSON string, with a `command`). The answer
carries both harnesses' decision keys. Any failure to parse exits 0 with no
output, so a broken hook can never block ordinary work.
"""

from __future__ import annotations

import json
import re
import sys

DENY: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            r"\bgit\b[^|;&]*\bpush\b[^|;&]*(\s--force(-with-lease)?\b|\s-f\b|\s-[a-zA-Z]*f[a-zA-Z]*\b)"
        ),
        "force-push",
    ),
    (re.compile(r"\bgit\b[^|;&]*\breset\b[^|;&]*\s--hard\b"), "hard reset"),
    (re.compile(r"\bgit\b[^|;&]*\brebase\b"), "history rewrite (rebase)"),
    (re.compile(r"\bgit\b[^|;&]*\bcommit\b[^|;&]*\s--amend\b"), "history rewrite (amend)"),
    (re.compile(r"\bgit\b[^|;&]*\b(filter-branch|filter-repo)\b"), "history rewrite"),
    (
        re.compile(r"\bgit\b[^|;&]*\b(commit|push|merge)\b[^|;&]*\s(--no-verify|-n)\b"),
        "skipping the commit hooks",
    ),
    (re.compile(r"\bgit\b[^|;&]*\bbranch\b[^|;&]*\s-D\b"), "force-deleting a branch"),
]


def extract_command(payload: dict) -> str:
    for key in ("tool_input", "toolArgs", "tool_args"):
        args = payload.get(key)
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except ValueError:
                return ""
        if isinstance(args, dict) and args.get("command"):
            return str(args["command"])
    return ""


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        command = extract_command(payload)
    except Exception:  # noqa: BLE001 - a hook must fail open
        return 0
    if not command:
        return 0

    for pattern, label in DENY:
        if pattern.search(command):
            reason = (
                f"python-dev blocks {label}. This is on the never list: it destroys history "
                "the user or a teammate may depend on. Make a new commit instead, or ask the "
                "user to run it themselves."
            )
            json.dump(
                {
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": reason,
                    }
                },
                sys.stdout,
            )
            return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
