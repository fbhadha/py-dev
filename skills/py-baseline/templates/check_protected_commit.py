#!/usr/bin/env python3
"""commit-msg hook: a commit that changes a protected file must say who approved it.

python-dev's in-session guards make the harness ask the human before an existing
protected file is changed. This is the floor under them: whatever harness ran, a
commit that touches one of these files fails unless its message carries a line

    approved: pyproject.toml, .gitignore

naming every protected file in the commit. Off when docs/agents/mode.md says
`protect-existing-files: off` or PYTHON_DEV_GUARD=off is set.

Installed by .pre-commit-config.yaml at the commit-msg stage; pre-commit passes
the path of the message file as the only argument.
"""

from __future__ import annotations

import fnmatch
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

GIT = shutil.which("git") or "git"

PROTECTED = (
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".cursorrules",
    ".cursor/rules/*",
    ".github/copilot-instructions.md",
    ".github/copilot/*",
    ".github/hooks/*",
    ".github/workflows/*",
    ".gitlab-ci.yml",
    ".claude/settings.json",
    ".mcp.json",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements*.txt",
    "Pipfile",
    "poetry.lock",
    ".python-version",
    ".pre-commit-config.yaml",
    ".gitignore",
    ".env.example",
    ".secrets.baseline",
    "README.md",
    "CONTEXT.md",
    "CONTEXT-MAP.md",
    "docs/adr/*",
    "docs/agents/*",
    "docs/architecture.md",
    "docs/howto/*",
    "scripts/repowise_gate.py",
    "scripts/adr_sync.py",
    "scripts/run_readme_blocks.py",
    "scripts/check_protected_commit.py",
)
OFF_VALUES = {"off", "0", "false", "no"}
APPROVED_LINE = re.compile(r"^\s*approved:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)


def guard_off() -> bool:
    if os.environ.get("PYTHON_DEV_GUARD", "").strip().lower() in OFF_VALUES:
        return True
    mode = Path("docs/agents/mode.md")
    if not mode.exists():
        return False
    for line in mode.read_text(encoding="utf-8", errors="replace").splitlines():
        key, _, value = line.partition(":")
        if key.strip() == "protect-existing-files" and value.strip().lower() in OFF_VALUES:
            return True
    return False


def staged_protected() -> list[str]:
    out = subprocess.run(
        [GIT, "diff", "--cached", "--name-only", "--diff-filter=MDR"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    return sorted(
        path for path in out.splitlines() if any(fnmatch.fnmatch(path, p) for p in PROTECTED)
    )


def approved_in(message: str) -> set[str]:
    names: set[str] = set()
    for match in APPROVED_LINE.finditer(message):
        names.update(part.strip().strip("`") for part in match.group(1).split(","))
    return names


def main(argv: list[str]) -> int:
    if guard_off() or len(argv) != 1:
        return 0
    changed = staged_protected()
    if not changed:
        return 0
    message = Path(argv[0]).read_text(encoding="utf-8", errors="replace")
    missing = [path for path in changed if path not in approved_in(message)]
    if not missing:
        return 0
    sys.stderr.write(
        "This commit changes protected files the message does not say were approved:\n  "
        + "\n  ".join(missing)
        + "\nAdd a line to the message naming each one, for example:\n  approved: "
        + ", ".join(missing)
        + "\nOnly do that if the human saw and approved each change.\n"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
