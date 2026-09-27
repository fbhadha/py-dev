"""adr_sync.py's shape check: the template copy is skipped, the short form is reported.

Imports this repo's copy under scripts/; the last test proves it is the template.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = "scripts/adr_sync.py"
TEMPLATE = "skills/py-baseline/templates/adr_sync.py"
ADR_TEMPLATE = "skills/py-baseline/templates/adr-template.md"


@pytest.fixture
def adr_sync(root: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("adr_sync", root / SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_skips_the_template_copy(adr_sync: ModuleType, root: Path, tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text((root / ADR_TEMPLATE).read_text(encoding="utf-8"), encoding="utf-8")
    assert adr_sync.is_template(readme, readme.read_text(encoding="utf-8"))


def test_reports_the_short_form(adr_sync: ModuleType, tmp_path: Path) -> None:
    short = tmp_path / "0001-short.md"
    short.write_text("# Use one queue\n\nWe picked one queue because it is simpler.\n")
    assert adr_sync.format_problem(short, short.read_text(encoding="utf-8"))


def test_accepts_the_governing_form(adr_sync: ModuleType, tmp_path: Path) -> None:
    full = tmp_path / "0002-full.md"
    full.write_text("# Use one queue\n\n## Status\n\nAccepted\n\n## Scope\n\n- src/q/\n")
    assert adr_sync.format_problem(full, full.read_text(encoding="utf-8")) is None


def test_copy_matches_template(root: Path) -> None:
    assert (root / SCRIPT).read_bytes() == (root / TEMPLATE).read_bytes()
