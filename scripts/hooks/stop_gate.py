#!/usr/bin/env python3
"""Stop hook: the turn does not end with unapproved changes to protected files, or with red ruff.

Two checks, in this order:

1. `git status` lists a tracked, protected file as modified, deleted or renamed,
   and no approved edit to it was recorded this session. Block, naming the files:
   revert them, or redo the change through the edit tool so the harness can ask
   the human.
2. `uv run ruff check` is red on the .py files this session changed, in a repo
   that has the baseline ([tool.ruff] in pyproject.toml). Block with the first
   lines of output.

Honours stop_hook_active (Claude Code) so it never blocks twice in a row; Copilot
caps block loops itself. Exits 0 silently on any error of its own.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import _common as c


def status_lines() -> list[str]:
    out = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    ).stdout
    return out.splitlines()


def unapproved_protected(lines: list[str], session: str, mode: str) -> list[str]:
    if mode == "off":
        return []
    done = c.approved(session)
    found: list[str] = []
    for line in lines:
        code, path = line[:2], line[3:].split(" -> ")[-1].strip()
        if code.strip() in ("", "??"):
            continue  # untracked: creating files is allowed
        if c.needs_approval(path, mode) and path not in done:
            found.append(path)
    return sorted(found)


def changed_python_files(lines: list[str]) -> list[str]:
    files = []
    for line in lines:
        path = line[3:].split(" -> ")[-1].strip()
        if path.endswith(".py") and Path(path).exists():
            files.append(path)
    return files


def run_ruff(prefix: list[str], files: list[str]) -> subprocess.CompletedProcess[str] | None:
    """Run ruff; exit codes 0 clean, 1 violations, 2 ruff error. None when it could not start."""
    try:
        return subprocess.run(
            [*prefix, "check", "--output-format", "concise", *files],
            capture_output=True,
            text=True,
            timeout=45,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def block(reason: str) -> None:
    json.dump({"decision": "block", "reason": reason}, sys.stdout)


def protected_problem(lines: list[str], session: str) -> str | None:
    pending = unapproved_protected(lines, session, c.guard_mode())
    if not pending:
        return None
    return (
        "python-dev: these existing protected files were changed without the human's "
        "approval this session:\n  " + "\n  ".join(pending) + "\n"
        "Do not end the turn like this. For each file: revert it "
        "(`git checkout -- <file>`) and, if the change is wanted, show the user what "
        "will change and why, then make it through the edit tool so the harness can "
        "ask them. A command that must write the file (`uv add`, "
        "`repowise generate-claude-md`) is run only after that explanation; once "
        "approved, everything it changed counts as approved."
    )


def ruff_problem(lines: list[str]) -> str | None:
    pyproject = Path("pyproject.toml")
    if not pyproject.exists() or "[tool.ruff" not in pyproject.read_text(encoding="utf-8"):
        return None
    files = changed_python_files(lines)
    if not files:
        return None
    result = run_ruff(["uv", "run", "--no-sync", "ruff"], files)
    if result is None or result.returncode not in (0, 1):
        result = run_ruff(["ruff"], files)
    if result is None or result.returncode != 1 or not result.stdout.strip():
        return None  # clean, or ruff itself could not run: never block on our own failure
    head = "\n".join(result.stdout.splitlines()[:15])
    return (
        "ruff is red on files changed this session. Fix these before stopping "
        "(never with --no-verify or by editing the rule):\n" + head
    )


def main() -> int:
    try:
        payload = c.read_payload()
        if payload.get("stop_hook_active") or c.repo_root() is None:
            return 0
        lines = status_lines()
        reason = protected_problem(lines, c.session_id(payload)) or ruff_problem(lines)
        if reason:
            block(reason)
    except Exception:  # noqa: BLE001 - a hook must fail open
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
