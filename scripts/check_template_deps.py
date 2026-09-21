#!/usr/bin/env python3
"""The baseline's dev dependency group must resolve as one set, with Repowise in it.

Builds a scratch pyproject.toml from the `[dependency-groups]` table in
skills/py-baseline/templates/pyproject-tools.toml and runs `uv lock` on it. A
floor that names a version that does not exist, or one that conflicts with
Repowise's own pins (it pins rich and pathspec), fails here instead of in a
user's intake, where the agent would spend a session's worth of turns on it.

Usage: python scripts/check_template_deps.py     (needs uv and network)
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "skills" / "py-baseline" / "templates" / "pyproject-tools.toml"


def dev_group(text: str) -> str:
    start = text.index("[dependency-groups]")
    end = text.index("\n[", start + 1)
    return text[start:end]


def main() -> int:
    group = dev_group(TEMPLATE.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp) / "pyproject.toml"
        project.write_text(
            '[project]\nname = "x"\nversion = "0"\nrequires-python = ">=3.12"\n\n' + group + "\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            ["uv", "lock"], cwd=tmp, capture_output=True, text=True, check=False, timeout=600
        )
    if result.returncode != 0:
        print("TEMPLATE DEV GROUP DOES NOT RESOLVE:")
        print(result.stderr[-3000:])
        return 1
    print("template dev group resolves:", result.stderr.strip().splitlines()[-1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
