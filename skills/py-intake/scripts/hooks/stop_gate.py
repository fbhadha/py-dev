#!/usr/bin/env python3
"""Stop hook: do not let the turn end while ruff is red on the Python files this session changed.

Runs `uv run ruff check` on the modified and untracked .py files. If it fails,
blocks the stop with the first lines of output so the agent fixes them. Runs
only in a repo that has a pyproject.toml with a [tool.ruff] table (the baseline),
never blocks twice in a row (honours stop_hook_active), and exits 0 silently on
any error of its own.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


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


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        if payload.get("stop_hook_active"):
            return 0
        pyproject = Path("pyproject.toml")
        if not pyproject.exists() or "[tool.ruff" not in pyproject.read_text(encoding="utf-8"):
            return 0
        files = changed_python_files()
        if not files:
            return 0
        result = run_ruff(["uv", "run", "--no-sync", "ruff"], files)
        if result is None or result.returncode not in (0, 1):
            result = run_ruff(["ruff"], files)
        if result is None or result.returncode != 1 or not result.stdout.strip():
            return 0  # clean, or ruff itself could not run: never block on our own failure
        head = "\n".join(result.stdout.splitlines()[:15])
    except Exception:  # noqa: BLE001 - a hook must fail open
        return 0
    json.dump(
        {
            "decision": "block",
            "reason": "ruff is red on files changed this session. Fix these before stopping "
            "(never with --no-verify or by editing the rule):\n" + head,
        },
        sys.stdout,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
