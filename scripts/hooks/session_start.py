#!/usr/bin/env python3
"""SessionStart hook: one line saying the guards are running and in which mode.

The persona looks for this line at session start. If it is missing, the plugin's
hooks are not active on this harness, and the agent says so before touching
anything. Exits 0 silently on any error of its own.
"""

from __future__ import annotations

import sys

import _common as c


def main() -> int:
    try:
        mode = c.guard_mode()
        state = {
            "intake": "ON (repo not set up yet): each protected file needs one yes",
            "on": "ON: the protected list needs one yes per file",
            "ask-once": "ASK-ONCE: the first protected change asks; that yes covers the session",
            "off": "OFF (docs/agents/mode.md or PYTHON_DEV_GUARD)",
        }[mode]
        sys.stdout.write(
            f"python-dev guards active. Protected-file guard {state}. "
            "Stop gate and git guard on. "
            "Modes: on (per file), ask-once (per session), off, set by "
            "`protect-existing-files:` in docs/agents/mode.md (a protected edit, so the harness "
            "asks), or PYTHON_DEV_GUARD=off for one session.\n"
        )
    except Exception:  # noqa: BLE001 - a hook must fail open
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
