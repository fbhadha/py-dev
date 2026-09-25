#!/usr/bin/env python3
"""PreToolUse guard for the py-eval agent: it reads and writes under tests/evals/ only.

The scenario author must not see the agent's code, its prompts or the tests the author
wrote: that is where the happy-path wording lives. Its tool list is Read and Write; this
hook, named in its frontmatter, denies a read, write or edit of any file outside
`tests/evals/`, and any search or shell call, with a reason that says what to do
instead. Runs in Claude Code, whose payload names the agent (`agent_type`, the plugin
scoped `python-dev:py-eval`); a payload with no agent, or another agent, gets no
decision. Copilot CLI's pre-tool payload cannot name the agent, so there the tool list
and the instruction are the guard. Any failure means no decision.
"""

from __future__ import annotations

import sys
from pathlib import Path

import _common as c
import guard_edit

EVAL_AGENT = "py-eval"
ALLOWED = "tests/evals/"
READ_TOOLS = {"read", "notebookread", "view"}
SEARCH_TOOLS = {"grep", "glob", "rg", "search"}
PATH_KEYS = ("file_path", "path", "filePath", "notebook_path", "target_file")
REASON = (
    "python-dev: py-eval reads and writes under tests/evals/ only. The targets file is all it "
    "needs; the agent's code and the tests the author wrote are where the happy-path wording "
    "lives. Open the targets file, write the eval set beside it, and stop."
)


def is_eval_author(payload: dict) -> bool:
    kind = str(
        payload.get("agent_type") or payload.get("agentType") or payload.get("agent_name") or ""
    )
    return kind == EVAL_AGENT or kind.endswith(":" + EVAL_AGENT)


def touched_paths(args: dict) -> list[str]:
    paths = [str(args[key]) for key in PATH_KEYS if isinstance(args.get(key), str) and args[key]]
    return paths or guard_edit.edited_paths(args)


def allowed(path: str, root: Path) -> bool:
    rel = guard_edit.relative(path, root)
    return rel is not None and rel.startswith(ALLOWED)


def check(payload: dict) -> tuple[str, str] | None:
    """("deny", reason) when the eval author reaches outside tests/evals/; else None."""
    if not is_eval_author(payload):
        return None
    root = c.repo_root()
    if root is None:
        return None
    name = c.tool_name(payload).strip().lower()
    if name in SEARCH_TOOLS or "bash" in name or "shell" in name or "terminal" in name:
        return "deny", REASON
    if guard_edit.is_edit_tool(name) or name in READ_TOOLS:
        paths = touched_paths(c.tool_args(payload))
        if paths and all(allowed(p, root) for p in paths):
            return None
        return "deny", REASON
    return None


def main() -> int:
    try:
        payload = c.read_payload()
        c.enter_project(payload)
        found = check(payload)
        if found:
            c.decision(*found)
    except Exception:  # noqa: BLE001 - a hook must fail open
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
