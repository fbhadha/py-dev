#!/usr/bin/env python3
"""PreToolUse rule for file edits: no ticket, no code.

In a repo py-intake has set up (`docs/agents/mode.md` exists), an edit to product
code asks first unless the branch is `ticket/`, `prototype/` or `intake/`. Product
code is anything under `src/` or `tests/`, or any `.py` file outside `prototypes/`.
The reason tells the agent what to do instead: shape the request or open a quick
ticket, then build on `ticket/<id>-<slug>`. A repo without `mode.md` is not a
python-dev repo and is never asked about.

`guard_command.py` calls check() for every edit tool, so each harness needs one
pre-tool hook entry. Tool names and argument keys covered: Claude Code (`Edit`,
`Write`, `MultiEdit`, `NotebookEdit`: `file_path`, `notebook_path`), Copilot CLI
(`edit`, `create`, `str_replace_editor`: `path`; `apply_patch`: the patch text)
and VS Code (`create_file`, `replace_string_in_file` and friends: `filePath`).
PYTHON_DEV_GUARD=off silences it. Any failure means no decision.
"""

from __future__ import annotations

import re
from pathlib import Path

import _common as c

EDIT_TOOLS = {
    "edit",
    "write",
    "multiedit",
    "notebookedit",
    "create",
    "str_replace_editor",
    "str_replace_based_edit_tool",
    "apply_patch",
    "create_file",
    "replace_string_in_file",
    "multi_replace_string_in_file",
    "insert_edit_into_file",
    "edit_file",
    "edit_notebook_file",
}
PATH_KEYS = ("file_path", "path", "filePath", "notebook_path", "target_file")
PATCH_FILE = re.compile(r"^\*\*\* (?:(?:Add|Update|Delete) File|Move to): (.+?)\s*$", re.MULTILINE)
BUILD_BRANCHES = ("ticket/", "prototype/", "intake/")
NOT_PRODUCT = ("prototypes/",)


def is_edit_tool(name: str) -> bool:
    return name.strip().lower() in EDIT_TOOLS


def edited_paths(args: dict) -> list[str]:
    if str(args.get("command", "")).lower() == "view":
        return []  # str_replace_editor's read mode
    paths = [str(args[key]) for key in PATH_KEYS if isinstance(args.get(key), str) and args[key]]
    for value in args.values():
        if isinstance(value, str) and "*** " in value:
            paths += PATCH_FILE.findall(value)
    return paths


def relative(path: str, root: Path) -> str | None:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate
    try:
        return candidate.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return None  # outside the repo


def is_product(rel: str) -> bool:
    if rel.startswith(NOT_PRODUCT):
        return False
    return rel.startswith(("src/", "tests/")) or rel.endswith(".py")


def check(payload: dict) -> tuple[str, str] | None:
    """("ask", reason) when this edit writes product code off a build branch; else None."""
    if c.guard_off():
        return None
    root = c.repo_root()
    if root is None or not (root / "docs" / "agents" / "mode.md").exists():
        return None
    branch = c.current_branch()
    if branch.startswith(BUILD_BRANCHES):
        return None
    rels = [rel for rel in (relative(p, root) for p in edited_paths(c.tool_args(payload))) if rel]
    product = sorted({rel for rel in rels if is_product(rel)})
    if not product:
        return None
    files = ", ".join(product[:5])
    if branch.startswith("shaping/"):
        return (
            "ask",
            f"python-dev: this shaping branch is about to edit product code ({files}). "
            "Shaping decides; a ticket builds. Throwaway code goes on prototype/<slug>; the "
            "real change goes in a ticket. Approve only if the user asked for this edit in "
            "their own words.",
        )
    return (
        "ask",
        f"python-dev: no ticket, no code. This edits {files} on `{branch or 'a detached HEAD'}`, "
        "which is not a ticket branch. Say what kind of request this is (new idea, revision, "
        "ticket, bug); shape it or open a quick ticket (py-shape), then "
        "`git switch -c ticket/<id>-<slug>` and build there. Approve only if the user asked "
        "for this exact edit in their own words.",
    )
