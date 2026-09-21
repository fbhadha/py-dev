#!/usr/bin/env python3
"""PreToolUse guard for the shell tool: main changes only by a merge the human said yes to.

Denied outright (no asking): force-push, hard reset, history rewrite, --no-verify,
force-deleting a branch. These are on the persona's never list.

Asked (the harness prompts the human): anything that lands on main. A commit while
main is checked out, a merge into main (checked out, or switched to in the same
command), a push to main (explicit, or a bare push while on main), and merging a
pull or merge request from the command line (`gh pr merge`, `glab mr merge`). On
a branch, nothing asks: commit, push and merging main into the branch are free.

Reads either harness's payload. Any failure exits 0 with no output.
"""

from __future__ import annotations

import re
import sys

import _common as c

GIT = r"\bgit\b[^|;&]*"
DENY: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            GIT + r"\bpush\b[^|;&]*(\s--force(-with-lease)?\b|\s-f\b|\s-[a-zA-Z]*f[a-zA-Z]*\b)"
        ),
        "force-push",
    ),
    (re.compile(GIT + r"\breset\b[^|;&]*\s--hard\b"), "hard reset"),
    (re.compile(GIT + r"\brebase\b"), "history rewrite (rebase)"),
    (re.compile(GIT + r"\bcommit\b[^|;&]*\s--amend\b"), "history rewrite (amend)"),
    (re.compile(GIT + r"\b(filter-branch|filter-repo)\b"), "history rewrite"),
    (
        re.compile(GIT + r"\b(commit|push|merge)\b[^|;&]*\s(--no-verify|-n)\b"),
        "skipping the commit hooks",
    ),
    (re.compile(GIT + r"\bbranch\b[^|;&]*\s-D\b"), "force-deleting a branch"),
]

MAIN = r"(main|master|trunk)"
COMMIT = re.compile(GIT + r"\bcommit\b")
MERGE = re.compile(GIT + r"\bmerge\b")
PUSH = re.compile(GIT + r"\bpush\b")
PUSH_TO_MAIN = re.compile(GIT + r"\bpush\b[^|;&]*\s(\S+\s+)?(\S+:)?" + MAIN + r"\b")
SWITCH_TO_MAIN = re.compile(GIT + r"\b(switch|checkout)\s+(-q\s+)?" + MAIN + r"\b")
PR_MERGE = re.compile(r"\b(gh\s+pr\s+merge|glab\s+mr\s+merge)\b")


def is_shell_tool(name: str) -> bool:
    name = name.lower()
    return not name or "bash" in name or "shell" in name or "terminal" in name or name == "run"


def denied(command: str) -> str | None:
    for pattern, label in DENY:
        if pattern.search(command):
            return (
                f"python-dev blocks {label}. This is on the never list: it destroys history "
                "the user or a teammate may depend on. Make a new commit instead, or ask the "
                "user to run it themselves."
            )
    return None


def lands_on_main(command: str, branch: str) -> str | None:
    """What this command would do to main, or None when it stays on a branch."""
    on_main = c.is_main(branch) or bool(SWITCH_TO_MAIN.search(command))
    if PR_MERGE.search(command):
        return "merge a pull request into main"
    if MERGE.search(command) and on_main:
        return "merge into main"
    if PUSH_TO_MAIN.search(command) or (PUSH.search(command) and on_main):
        return "push to main"
    if COMMIT.search(command) and on_main:
        return "commit on main"
    return None


def main() -> int:
    try:
        payload = c.read_payload()
        command = str(c.tool_args(payload).get("command", ""))
        if not is_shell_tool(c.tool_name(payload)) or not command:
            return 0
        reason = denied(command)
        if reason:
            c.decision("deny", reason)
            return 0
        if c.guard_off() or c.repo_root() is None:
            return 0
        action = lands_on_main(command, c.current_branch())
        if action:
            c.decision(
                "ask",
                f"python-dev: this would {action}. Main changes only by a merge you said yes "
                "to, after the checks and the review. If this is that merge, approve it. If "
                "the agent is committing straight to main, it should be on a branch "
                "(`git switch -c ticket/<id>`).",
            )
    except Exception:  # noqa: BLE001 - a hook must fail open
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
