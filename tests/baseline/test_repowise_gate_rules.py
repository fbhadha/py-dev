"""repowise_gate.py applies the repo's own rules file, .repowise/health-rules.json.

Expected values: the script's exit codes (its docstring) and the edge-case table of
issue #56. The rule name is the one the gate prints for SWALLOWS.
"""

from collections.abc import Callable
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

SCRIPT = "scripts/repowise_gate.py"
SWALLOWS = "def load(path):\n    try:\n        return open(path).read()\n    except Exception:\n        pass\n"  # noqa: E501
RULES = ".repowise/health-rules.json"  # literal-ok: in the scratch repo (conftest's `repo`)
OFF_IN_SRC = '{"rules":[{"path":"src/**","disabled_biomarkers":["error_handling"]}]}'
OFF_IN_DOCS = '{"rules":[{"path":"docs/**","disabled_biomarkers":["error_handling"]}]}'
BROKEN = "{not json"


@pytest.fixture
def rules(repo: Path) -> Callable[[str], None]:
    """Write this text as the scratch repo's rules file; the gate reads it uncommitted."""

    def call(text: str) -> None:
        (repo / RULES).parent.mkdir(exist_ok=True)
        (repo / RULES).write_text(text, encoding="utf-8")

    return call


@pytest.mark.parametrize(
    ("text", "exit_code"),
    [(OFF_IN_SRC, 0), (OFF_IN_DOCS, 1), (BROKEN, 1)],
    ids=[
        "rule switched off for the path passes",
        "rule for another path refused",
        "broken rules file refused",
    ],
)
def test_rules(check, committed, rules, text: str, exit_code: int) -> None:
    rules(text)
    committed({"src/x.py": SWALLOWS})
    assert check(SCRIPT, "main..HEAD").returncode == exit_code


def test_unknown_revision_with_rules_fails_closed(check, rules) -> None:
    rules(OFF_IN_SRC)
    assert check(SCRIPT, "nosuchref..HEAD").returncode == 3


def test_changed_paths(gate: ModuleType) -> None:
    changes = [
        SimpleNamespace(head_path="src/b.py", base_path="src/a.py"),
        SimpleNamespace(head_path=None, base_path="src/gone.py"),
        SimpleNamespace(head_path="src/b.py", base_path="src/b.py"),
    ]
    assert gate.changed_paths(changes) == ["src/a.py", "src/b.py", "src/gone.py"]


def test_rules_in_force_printed(check, committed, rules) -> None:
    rules(OFF_IN_SRC)
    committed({"src/x.py": SWALLOWS})
    assert "rules in force: .repowise/health-rules.json" in check(SCRIPT, "main..HEAD").stdout


def test_no_rules_file_prints_no_rules_line(check, committed) -> None:
    committed({"src/x.py": SWALLOWS})
    assert "rules in force" not in check(SCRIPT, "main..HEAD").stdout
