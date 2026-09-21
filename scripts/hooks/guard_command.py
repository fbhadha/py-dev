#!/usr/bin/env python3
"""PreToolUse guard for the shell tool.

Denied outright (no asking): force-push, hard reset, history rewrite, --no-verify,
force-deleting a branch. These are on the persona's never list.

Asked (the harness prompts the human): a command that would write a protected,
tracked file without going through the edit tool: a redirection, `sed -i`, `tee`,
`cp`, `mv`, `rm`, `uv add`, `uv init`, `uv python pin`, `repowise
generate-claude-md`, and so on. Before any shell command runs, the set of files
git already reports modified is snapshotted, so record_edit.py can tell exactly
which tracked files the command changed and record them once it was approved.
Formatters never ask. This is a heuristic; stop_gate.py catches what it misses.

Reads either harness's payload. Any failure exits 0 with no output.
"""

from __future__ import annotations

import re
import sys

import _common as c

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


def unapproved_targets(command: str, session: str) -> list[str]:
    root = c.repo_root()
    mode = c.guard_mode()
    if root is None or mode == "off":
        return []
    done = c.approved(session)
    return sorted(
        rel
        for rel in c.command_targets(command, root)
        if c.needs_approval(rel, mode) and rel not in done
    )


def main() -> int:
    try:
        payload = c.read_payload()
        command = str(c.tool_args(payload).get("command", ""))
        if not is_shell_tool(c.tool_name(payload)) or not command:
            return 0
        if c.repo_root() is not None:
            c.take_snapshot(c.session_id(payload))
        reason = denied(command)
        if reason:
            c.decision("deny", reason)
            return 0
        pending = unapproved_targets(command, c.session_id(payload))
        if pending:
            c.decision(
                "ask",
                "python-dev: this command writes existing protected file(s): "
                + ", ".join(f"`{rel}`" for rel in pending)
                + ". The agent must have shown you what will change and why before you approve. "
                "Approving is the one yes for these files this session.",
            )
    except Exception:  # noqa: BLE001 - a hook must fail open
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
