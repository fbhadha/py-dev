"""repowise_gate.py: a change passes unless it made a Python file it touched worse.

Drives this repo's copy under scripts/; the last test proves it is the template.
Expected values: the script's exit codes (its docstring) and issue #19's edge-case table.
"""

import importlib.util
from collections.abc import Callable
from pathlib import Path

import pytest

SCRIPT = "scripts/repowise_gate.py"
TEMPLATE = "skills/py-baseline/templates/repowise_gate.py"
CLEAN = "X = 2\n"
SWALLOWS = "def load(path):\n    try:\n        return open(path).read()\n    except Exception:\n        pass\n"  # noqa: E501
NOTES = {"NOTES.md": "# notes\n"}


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


@pytest.mark.parametrize(
    ("files", "exit_code"),
    [
        ({"src/x.py": CLEAN}, 0),
        ({"src/x.py": CLEAN, **NOTES}, 0),
        (NOTES, 0),
        ({"src/x.py": None, **NOTES}, 0),
        ({"src/x.py": SWALLOWS}, 1),
        ({"src/x.py": SWALLOWS, **NOTES}, 1),
    ],
    ids=[
        "python only passes",
        "python beside notes passes",
        "docs only passes",
        "deleted python beside notes passes",
        "introduced finding refused",
        "introduced finding beside notes refused",
    ],
)
def test_change(check, committed, files: dict[str, str | None], exit_code: int) -> None:
    committed(files)
    assert check(SCRIPT, "main..HEAD").returncode == exit_code


@pytest.mark.parametrize(
    "revisions", ["main..main", "nosuchref..HEAD"], ids=["empty range", "unknown revision"]
)
def test_nothing_compared_fails_closed(check, revisions: str) -> None:
    assert check(SCRIPT, revisions).returncode == 3


@pytest.mark.parametrize(
    "payload",
    [
        {"skipped": {"src/x.py": "parse_failed"}, "scope": {"failed": 0}},
        {"skipped": {"NOTES.md": "deleted"}, "scope": {"failed": 1}},
    ],
    ids=["a reason outside the allowlist", "a file Repowise failed on"],
)
def test_missed_file_fails_closed(gate: ModuleType, payload: dict) -> None:
    assert gate.degraded("partial", payload) is True


def test_copy_matches_template(root: Path) -> None:
    assert (root / SCRIPT).read_bytes() == (root / TEMPLATE).read_bytes()
