#!/usr/bin/env python3
"""Stop hook: the turn does not end with red ruff on the files this session changed.

`uv run ruff check` runs on the modified .py files, in a repo that has the baseline
([tool.ruff] in pyproject.toml). Red blocks the turn with the first lines of output.

Honours stop_hook_active (Claude Code) so it never blocks twice in a row; Copilot
caps block loops itself. Runs in the project from the payload's cwd, not where the
harness started it. Exits 0 silently on any error of its own.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import _common as c


def changed_python_files() -> list[str]:
    out = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    ).stdout
    files = []
    for line in out.splitlines():
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


def ruff_problem() -> str | None:
    pyproject = Path("pyproject.toml")
    if not pyproject.exists() or "[tool.ruff" not in pyproject.read_text(encoding="utf-8"):
        return None
    files = changed_python_files()
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
        c.enter_project(payload)
        root = c.repo_root()
        if payload.get("stop_hook_active") or root is None:
            return 0
        os.chdir(root)
        reason = ruff_problem()
        if reason:
            json.dump({"decision": "block", "reason": reason}, sys.stdout)
    except Exception:  # noqa: BLE001 - a hook must fail open
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
