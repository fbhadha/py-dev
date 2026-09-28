"""repowise_gate.py: a change passes unless it made a Python file it touched worse.

Drives this repo's copy under scripts/; the last test proves it is the template.
Expected values: the script's exit codes (its docstring) and the edge-case tables of
issues #19 and #27.
"""

from pathlib import Path
from types import ModuleType

import pytest
from repowise.core.test_paths import is_test_related_path

SCRIPT = "scripts/repowise_gate.py"
TEMPLATE = "skills/py-baseline/templates/repowise_gate.py"
TEST_FILE = "tests/test_x.py"  # literal-ok: in the scratch repo (conftest's `repo`), not this tree
CLEAN = "X = 2\n"
SWALLOWS = "def load(path):\n    try:\n        return open(path).read()\n    except Exception:\n        pass\n"  # noqa: E501
NOTES = {"NOTES.md": "# notes\n"}
# One primitive_obsession and one dry_violation; the first needs a file of 60 lines.
WIDE = "def five(a, b, c, d, e):\n    return a\n" + "V = 0\n" * 60
NOT_HELD = "2 finding(s) in test files not held (dry_violation, primitive_obsession)"


@pytest.mark.parametrize(
    ("files", "exit_code"),
    [
        ({"src/x.py": CLEAN}, 0),
        ({"src/x.py": CLEAN, **NOTES}, 0),
        (NOTES, 0),
        ({"src/x.py": None, **NOTES}, 0),
        ({"src/x.py": SWALLOWS}, 1),
        ({"src/x.py": SWALLOWS, **NOTES}, 1),
        ({TEST_FILE: WIDE}, 0),
        ({"src/x.py": WIDE}, 1),
        ({TEST_FILE: SWALLOWS}, 1),
        ({TEST_FILE: WIDE, "src/x.py": SWALLOWS}, 1),
    ],
    ids=[
        "python only passes",
        "python beside notes passes",
        "docs only passes",
        "deleted python beside notes passes",
        "introduced finding refused",
        "introduced finding beside notes refused",
        "both types in a test file pass",
        "both types in a source file refused",
        "another type in a test file refused",
        "held finding beside test findings refused",
    ],
)
def test_change(check, committed, files: dict[str, str | None], exit_code: int) -> None:
    committed(files)
    assert check(SCRIPT, "main..HEAD").returncode == exit_code


def test_not_held_counted(check, committed) -> None:
    committed({TEST_FILE: WIDE})
    assert NOT_HELD in check(SCRIPT, "main..HEAD").stdout


def test_nothing_dropped_prints_no_count(check, committed) -> None:
    committed({"src/x.py": WIDE})
    assert "not held" not in check(SCRIPT, "main..HEAD").stdout


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


@pytest.mark.parametrize(
    ("finding", "kept"),
    [
        ({"path": TEST_FILE, "biomarker_type": "dry_violation"}, False),
        ({"path": "src/x.py", "biomarker_type": "primitive_obsession"}, True),
        ({"path": TEST_FILE, "biomarker_type": "error_handling"}, True),
    ],
    ids=[
        "worsened in a test file",
        "either type in a source file",
        "another type in a test file",
    ],
)
def test_held(gate: ModuleType, finding: dict[str, str], kept: bool) -> None:
    worsened = {**finding, "change_kind": "worsened"}
    assert gate.held([worsened], is_test_related_path) == ([worsened] if kept else [])


def test_copy_matches_template(root: Path) -> None:
    assert (root / SCRIPT).read_bytes() == (root / TEMPLATE).read_bytes()
