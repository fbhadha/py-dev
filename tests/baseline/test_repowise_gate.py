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
RANGE = "main..HEAD"
CLEAN = "X = 2\n"
SWALLOWS = "def load(path):\n    try:\n        return open(path).read()\n    except Exception:\n        pass\n"  # noqa: E501
NOTES = {"NOTES.md": "# notes\n"}


@pytest.fixture
def change(repo: Path, git) -> Callable[[dict[str, str | None]], None]:
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


def test_python_only_change_passes(check, change) -> None:
    change({"src/x.py": CLEAN})
    assert check(SCRIPT, RANGE).returncode == 0


def test_python_beside_a_file_repowise_cannot_analyse_passes(check, change) -> None:
    change({"src/x.py": CLEAN, **NOTES})
    assert check(SCRIPT, RANGE).returncode == 0


def test_introduced_finding_beside_notes_refused(check, change) -> None:
    change({"src/x.py": SWALLOWS, **NOTES})
    assert check(SCRIPT, RANGE).returncode == 1


def test_docs_only_change_passes(check, change) -> None:
    change(NOTES)
    assert check(SCRIPT, RANGE).returncode == 0


def test_deleted_python_beside_notes_passes(check, change) -> None:
    change({"src/x.py": None, **NOTES})
    assert check(SCRIPT, RANGE).returncode == 0


def test_introduced_finding_refused(check, change) -> None:
    change({"src/x.py": SWALLOWS})
    assert check(SCRIPT, RANGE).returncode == 1


def test_empty_range_fails_closed(check) -> None:
    assert check(SCRIPT, "main..main").returncode == 3


def test_unknown_revision_fails_closed(check) -> None:
    assert check(SCRIPT, "nosuchref..HEAD").returncode == 3


@pytest.mark.parametrize(
    "payload",
    [
        {"skipped": {"src/x.py": "parse_failed"}, "scope": {"failed": 0}},
        {"skipped": NOTES.keys() and {"NOTES.md": "deleted"}, "scope": {"failed": 1}},
    ],
    ids=["a reason outside the allowlist", "a file Repowise failed on"],
)
def test_unknown_skip_reason_fails_closed(root: Path, payload: dict) -> None:
    spec = importlib.util.spec_from_file_location("repowise_gate", root / SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    assert gate.degraded("partial", payload) is True


def test_copy_matches_template(root: Path) -> None:
    assert (root / SCRIPT).read_bytes() == (root / TEMPLATE).read_bytes()
