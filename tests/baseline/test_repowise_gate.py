"""repowise_gate.py: a change passes unless it made a Python file it touched worse.

Drives this repo's copy under scripts/; the last test proves it is the template.
Expected values: the script's exit codes (its docstring) and issue #19.
"""

from pathlib import Path

SCRIPT = "scripts/repowise_gate.py"
TEMPLATE = "skills/py-baseline/templates/repowise_gate.py"
RANGE = "main..HEAD"


def test_python_only_change_passes(check, repo: Path, git) -> None:
    git("switch", "-q", "-c", "ticket/1")
    (repo / "src" / "x.py").write_text("X = 2\n", encoding="utf-8")
    git("commit", "-q", "-am", "src only")
    assert check(SCRIPT, RANGE).returncode == 0


def test_python_beside_a_file_repowise_cannot_analyse_passes(check, repo: Path, git) -> None:
    git("switch", "-q", "-c", "ticket/2")
    (repo / "src" / "x.py").write_text("X = 2\n", encoding="utf-8")
    (repo / "NOTES.md").write_text("# notes\n", encoding="utf-8")
    git("add", ".")
    git("commit", "-q", "-m", "src and notes")
    assert check(SCRIPT, RANGE).returncode == 0


def test_copy_matches_template(root: Path) -> None:
    assert (root / SCRIPT).read_bytes() == (root / TEMPLATE).read_bytes()
