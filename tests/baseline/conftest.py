"""Fixtures the change gate's test files share: the script as a module, a committed change."""

import importlib.util
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = "scripts/repowise_gate.py"


@pytest.fixture
def gate(root: Path) -> ModuleType:
    """The script as a module, for the functions a subprocess cannot reach."""
    spec = importlib.util.spec_from_file_location("repowise_gate", root / SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def committed(repo: Path, git) -> Callable[[dict[str, str | None]], None]:
    """Commit these files on a new branch; a file whose content is None is deleted."""

    def call(files: dict[str, str | None]) -> None:
        git("switch", "-q", "-c", "ticket/19")
        for name, content in files.items():
            if content is None:
                (repo / name).unlink()
            else:
                (repo / name).write_text(content, encoding="utf-8")
        git("add", "-A")
        git("commit", "-q", "-m", "change")

    return call
