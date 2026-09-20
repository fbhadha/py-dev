#!/usr/bin/env python3
"""PostToolUse recorder: a protected file that was just changed counts as approved.

This hook runs only after a tool call succeeded. If the pre-tool guard asked, the
human said yes; so the protected paths the call touched are written to this
session's approval file, and the guards stop asking about them. Edit tools give
the path directly; for the shell tool the same heuristic as guard_command.py
names the paths, so a command that did not trigger a prompt records nothing.

Reads either harness's payload. Any failure exits 0 with no output.
"""

from __future__ import annotations

import sys

import _common as c


def main() -> int:
    try:
        payload = c.read_payload()
        name = c.tool_name(payload)
        args = c.tool_args(payload)
        root = c.repo_root()
        if root is None:
            return 0
        mode = c.guard_mode()
        if mode == "off":
            return 0
        rels: set[str] = set()
        if c.is_edit_tool(name):
            rel = c.relative(c.edit_path(args), root) if c.edit_path(args) else None
            if rel and c.needs_approval(rel, mode):
                rels.add(rel)
        else:
            command = str(args.get("command", ""))
            if command:
                rels = {r for r in c.command_targets(command, root) if c.needs_approval(r, mode)}
        if rels:
            c.approve(c.session_id(payload), rels)
    except Exception:  # noqa: BLE001 - a hook must fail open
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
