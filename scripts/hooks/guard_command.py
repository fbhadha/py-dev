#!/usr/bin/env python3
"""PreToolUse guard for the shell tool.

Denied outright (no asking): force-push, hard reset, history rewrite, --no-verify,
force-deleting a branch. These are on the persona's never list.

Asked (the harness prompts the human): a command that would write a protected,
tracked file without going through the edit tool: a redirection, `sed -i`, `tee`,
`cp`, `mv`, `rm`, `uv add`, `uv init`, `uv python pin`, `repowise
generate-claude-md`, and so on. Once approved, record_edit.py remembers the
paths for the session. This is a heuristic; stop_gate.py catches what it misses.

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


def main() -> int:
    try:
        payload = c.read_payload()
        name = c.tool_name(payload).lower()
        if name and not ("bash" in name or "shell" in name or "terminal" in name or name == "run"):
            return 0
        command = str(c.tool_args(payload).get("command", ""))
        if not command:
            return 0

        for pattern, label in DENY:
            if pattern.search(command):
                c.decision(
                    "deny",
                    f"python-dev blocks {label}. This is on the never list: it destroys history "
                    "the user or a teammate may depend on. Make a new commit instead, or ask the "
                    "user to run it themselves.",
                )
                return 0

        root = c.repo_root()
        if root is None:
            return 0
        mode = c.guard_mode()
        if mode == "off":
            return 0
        pending = sorted(
            rel
            for rel in c.command_targets(command, root)
            if c.needs_approval(rel, mode) and rel not in c.approved(c.session_id(payload))
        )
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
