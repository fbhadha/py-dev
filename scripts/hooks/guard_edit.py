#!/usr/bin/env python3
"""PreToolUse guard for the edit tools: an existing protected file needs one human yes.

When the agent is about to edit, write or create over a git-tracked file that is
protected (every tracked file while intake is running; the list in _common.py
after that), answer `ask`, so the harness shows the human the file and the
change and waits. Once the edit goes through, record_edit.py remembers the path,
and later edits to the same file in the same session pass without a prompt.

Reads either harness's payload. Any failure exits 0 with no output.
"""

from __future__ import annotations

import sys

import _common as c


def main() -> int:
    try:
        payload = c.read_payload()
        if not c.is_edit_tool(c.tool_name(payload)):
            return 0
        path = c.edit_path(c.tool_args(payload))
        root = c.repo_root()
        if not path or root is None:
            return 0
        rel = c.relative(path, root)
        if rel is None:
            return 0
        mode = c.guard_mode()
        if not c.needs_approval(rel, mode) or c.is_approved(c.session_id(payload), rel):
            return 0
        scope = (
            "Approving covers every protected file for the rest of this session; "
            "say 'ask per file' to the agent to go back."
            if mode == "ask-once"
            else "Approving is the one yes for this file this session."
        )
        c.decision(
            "ask",
            f"python-dev: `{rel}` already exists in this repo and is on the protected list "
            f"(agent files, packaging, checks, CI, docs). The agent must have shown you this "
            f"change and its reason before you approve. {scope}",
        )
    except Exception:  # noqa: BLE001 - a hook must fail open
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
