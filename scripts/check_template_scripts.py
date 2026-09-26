#!/usr/bin/env python3
"""Every Python template the baseline ships must pass the ruff config the baseline installs.

py-intake copies `skills/py-baseline/templates/*.py` into a target repo's `scripts/` and
`templates/pyproject-tools.toml` into its `pyproject.toml`. A template that fails that
config is refused by the target repo's own commit hook, at intake, in a user's session.
This script builds that layout in a scratch directory (the templates under `scripts/`,
so the config's `scripts/**` per-file ignores apply, under the rendered tool tables) and
runs `ruff check` and `ruff format --check` there. Ruff is the whole job here, so a
missing ruff is a failure, not a skip.

The sibling of `scripts/check_pack_examples.py`, which does the same for the pack's
example package; each check stands alone (docs/architecture.md).

Usage: python scripts/check_template_scripts.py     (needs ruff on PATH)
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "skills" / "py-baseline" / "templates"
TOOLS = TEMPLATES / "pyproject-tools.toml"
PACKAGE = "yourpkg"
PYTHON = f"{sys.version_info.major}.{sys.version_info.minor}"


def render_config(scratch: Path) -> int:
    """Lay the templates out as a target repo gets them; returns how many scripts were copied."""
    scripts = scratch / "scripts"
    scripts.mkdir()
    copied = [shutil.copy(path, scripts / path.name) for path in sorted(TEMPLATES.glob("*.py"))]
    tools = TOOLS.read_text(encoding="utf-8")
    tools = tools.replace("{{PACKAGE}}", PACKAGE).replace(
        "{{PYTHON_NODOT}}", PYTHON.replace(".", "")
    )
    tools = tools.replace("{{PYTHON}}", PYTHON)
    (scratch / "pyproject.toml").write_text(tools, encoding="utf-8")
    return len(copied)


def run(label: str, command: list[str], scratch: Path) -> bool:
    result = subprocess.run(command, cwd=scratch, capture_output=True, text=True, check=False)
    if result.returncode == 0:
        print(f"ok   {label}")
        return True
    print(f"FAIL {label}\n{result.stdout[-4000:]}{result.stderr[-2000:]}")
    return False


def main() -> int:
    if shutil.which("ruff") is None:
        print("check_template_scripts: ruff is not on PATH")
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp)
        count = render_config(scratch)
        results = [
            run("ruff check", ["ruff", "check", "--no-cache", "scripts"], scratch),
            run("ruff format", ["ruff", "format", "--check", "--no-cache", "scripts"], scratch),
        ]
    if all(results):
        print(f"every baseline template passes the baseline's own ruff ({count} files)")
        return 0
    print("\nTEMPLATE SCRIPTS FAIL THE BASELINE'S RUFF")
    return 1


if __name__ == "__main__":
    sys.exit(main())
