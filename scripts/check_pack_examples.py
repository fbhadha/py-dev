#!/usr/bin/env python3
"""Run the data-engineering pack's example package the way a target repo gets it.

py-intake copies `skills/pack-data-engineering/references/example/orders` to
`src/<package>/examples/orders/` and its tests to `tests/unit/examples/` and
`tests/integration/examples/`, replacing the placeholder package name `yourpkg`.
This script builds that layout in a scratch directory under the package name
`yourpkg`, writes a pyproject.toml carrying the baseline's own tool tables, and runs:

  - pytest, with the baseline's settings (warnings are errors, strict markers)
  - ruff check and ruff format --check, when ruff is on PATH
  - mypy --strict on src/, when mypy is on PATH

so what intake copies into a repo is green on day one under that repo's checks.
CI runs it with all three installed.

Usage: python scripts/check_pack_examples.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "skills" / "pack-data-engineering" / "references" / "example"
TOOLS = ROOT / "skills" / "py-baseline" / "templates" / "pyproject-tools.toml"
PACKAGE = "yourpkg"
PYTHON = f"{sys.version_info.major}.{sys.version_info.minor}"


def build(scratch: Path) -> None:
    src = scratch / "src" / PACKAGE
    (src / "examples").mkdir(parents=True)
    (src / "__init__.py").write_text('"""Scratch package for the pack example."""\n')
    (src / "examples" / "__init__.py").write_text('"""Worked examples, one per shape."""\n')
    shutil.copytree(EXAMPLE / "orders", src / "examples" / "orders")
    for tier in ("unit", "integration"):
        shutil.copytree(EXAMPLE / "tests" / tier, scratch / "tests" / tier / "examples")
    tools = TOOLS.read_text(encoding="utf-8")
    tools = tools.replace("{{PACKAGE}}", PACKAGE).replace(
        "{{PYTHON_NODOT}}", PYTHON.replace(".", "")
    )
    tools = tools.replace("{{PYTHON}}", PYTHON)
    tools = tools.replace("[project]\n", f'[project]\nname = "{PACKAGE}"\nversion = "0"\n', 1)
    (scratch / "pyproject.toml").write_text(tools, encoding="utf-8")


def step(label: str, command: list[str], scratch: Path) -> bool:
    env = {**os.environ, "PYTHONPATH": str(scratch / "src")}
    result = subprocess.run(
        command, cwd=scratch, env=env, capture_output=True, text=True, check=False
    )
    if result.returncode == 0:
        print(f"ok   {label}")
        return True
    print(f"FAIL {label}\n{result.stdout[-4000:]}{result.stderr[-2000:]}")
    return False


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp)
        build(scratch)
        checks = [("pytest", [sys.executable, "-m", "pytest", "-p", "no:cacheprovider"])]
        if shutil.which("ruff"):
            checks.append(("ruff check", ["ruff", "check", "--no-cache", "src", "tests"]))
            checks.append(
                ("ruff format", ["ruff", "format", "--check", "--no-cache", "src", "tests"])
            )
        else:
            print("skip ruff: not on PATH")
        if shutil.which("mypy"):
            checks.append(("mypy --strict src", ["mypy", "--no-incremental"]))
        else:
            print("skip mypy: not on PATH")
        results = [step(label, command, scratch) for label, command in checks]
    if all(results):
        print("\npack example green under the baseline's checks")
        return 0
    print("\nPACK EXAMPLE CHECK FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
