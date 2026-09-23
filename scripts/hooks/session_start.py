#!/usr/bin/env python3
"""SessionStart hook: the guard state, the branch, and where the plugin's scripts are.

The persona reads this at session start: the version and guard state go on its
status line, and the scripts path is how it runs find_skill.py, because the plugin
root variables reach hooks but not the model's shell. Output is one JSON object in
both shapes: `additionalContext` at the top level for Copilot CLI (which ignores
plain stdout) and under `hookSpecificOutput` for Claude Code. Where no line arrives
(VS Code drops SessionStart output), the persona says the guard state is unknown.
Exits 0 silently on any error of its own.
"""

from __future__ import annotations

import json
import sys

import _common as c


def main() -> int:
    try:
        c.enter_project(c.read_payload())
        branch = c.current_branch() or "(detached)"
        guard = "OFF for this session (PYTHON_DEV_GUARD)" if c.guard_off() else "ON"
        where = " Start a branch before changing anything." if c.is_main(branch) else ""
        text = (
            f"python-dev guards active (plugin {c.plugin_version()}). Branch: {branch}.{where} "
            f"Plugin scripts: {c.PLUGIN_ROOT / 'scripts'}. "
            f"Main guard {guard}: a commit, merge or push that lands on main asks you first, "
            "and so does anything sent to a repo that is not this project's origin; an edit "
            "to product code off a ticket branch asks first; force-push, hard reset, rebase, "
            "amend and --no-verify are denied; the turn cannot end with red ruff."
        )
        json.dump(
            {
                "additionalContext": text,
                "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text},
            },
            sys.stdout,
        )
    except Exception:  # noqa: BLE001 - a hook must fail open
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
