#!/usr/bin/env python3
"""SessionStart hook: one line saying the guards are running, and which branch this is.

The persona looks for this line at session start. If it is missing, the plugin's
hooks are not active on this harness, and the agent says so before touching
anything. Exits 0 silently on any error of its own.
"""

from __future__ import annotations

import sys

import _common as c


def main() -> int:
    try:
        branch = c.current_branch() or "(detached)"
        guard = "OFF for this session (PYTHON_DEV_GUARD)" if c.guard_off() else "ON"
        where = " Start a branch before changing anything." if c.is_main(branch) else ""
        sys.stdout.write(
            f"python-dev guards active. Branch: {branch}.{where} "
            f"Main guard {guard}: a commit, merge or push that lands on main asks you first; "
            "force-push, hard reset, rebase, amend and --no-verify are denied; the turn "
            "cannot end with red ruff.\n"
        )
    except Exception:  # noqa: BLE001 - a hook must fail open
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
