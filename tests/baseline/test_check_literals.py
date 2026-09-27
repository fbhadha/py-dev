"""check_literals.py: a path that names nothing in the tree, a key missing from .env.example.

Drives this repo's copy under scripts/; the last test proves it is the template. The
`# literal-ok:` markers below are for this repo's own literal check: the keys and paths
belong to the scratch repo, not to this tree.
"""

from collections.abc import Callable
from pathlib import Path

import pytest

SCRIPT = "scripts/check_literals.py"
TEMPLATE = "skills/py-baseline/templates/check_literals.py"
RANGE = "main...HEAD"


@pytest.fixture
def on_branch(repo: Path, git) -> Callable[[str, str], None]:
    """`on_branch("ticket/l1", code)`: a branch whose one commit appends `code` to src/x.py."""
    (repo / ".env.example").write_text("# the one key\nA_KEY=\n", encoding="utf-8")
    git("add", ".env.example")
    git("commit", "-q", "-m", "env example")

    def call(name: str, code: str, message: str = "change") -> None:
        git("switch", "-q", "-c", name)
        (repo / "src" / "x.py").write_text("X = 1\n" + code, encoding="utf-8")
        git("commit", "-q", "-am", message)

    return call


@pytest.mark.parametrize(
    ("code", "decision"),
    [
        ('P = "src/missing.py"\n', "refused"),
        ('Q = "out/report.json"\n', "passed"),
        ('U = "https://example.com/a.json"\nG = "src/*.py"\nF = "src/{name}.py"\n', "passed"),
        ('import os\nK = os.environ["B_KEY"]\n', "refused"),  # literal-ok: the scratch repo's key
        (
            'import os\nK = os.getenv("C_KEY", "x")\n',  # literal-ok: the scratch repo's key
            "refused",
        ),
        (
            'import os\nK = os.environ.get("A_KEY")\n',  # literal-ok: the scratch repo's key
            "passed",
        ),
        ('P = "src/missing.py"  # literal-ok: written by the first run\n', "passed"),
    ],
    ids=[
        "a path that names nothing refused",
        "runtime path passes",
        "url, glob and format string pass",
        "a key not in .env.example refused",
        "getenv key refused",
        "a key in .env.example passes",
        "literal-ok comment passes",
    ],
)
def test_added_literal(check, on_branch, code: str, decision: str) -> None:
    on_branch("ticket/l", code)
    assert check(SCRIPT, RANGE).decision == decision


def test_created_path_passes(check, repo: Path, git, on_branch) -> None:
    git("switch", "-q", "-c", "ticket/l3")
    (repo / "src" / "new.py").write_text("Y = 2\n", encoding="utf-8")
    (repo / "src" / "x.py").write_text('X = 1\nN = "src/new.py"\n', encoding="utf-8")
    git("add", "src/new.py")
    git("commit", "-q", "-am", "adds and names src/new.py")
    assert check(SCRIPT, RANGE).decision == "passed"


def test_override_passes(check, on_branch) -> None:
    reason = "task-9\n\nliteral-override: the user keeps the old path until the loader moves"
    on_branch("ticket/l9", 'P = "src/missing.py"\n', reason)
    assert check(SCRIPT, RANGE).decision == "passed"


def test_no_env_example_keys_not_checked_and_said(check, repo: Path, git, on_branch) -> None:
    git("switch", "-q", "-c", "ticket/l10")
    git("rm", "-q", ".env.example")
    code = 'X = 1\nimport os\nK = os.environ["B_KEY"]\n'  # literal-ok: the scratch repo's key
    (repo / "src" / "x.py").write_text(code, encoding="utf-8")
    git("commit", "-q", "-am", "no env example")
    said = check(SCRIPT, RANGE)
    assert said.decision == "passed"
    assert "not checked" in said.stdout


def test_copy_matches_template(root: Path) -> None:
    assert (root / SCRIPT).read_bytes() == (root / TEMPLATE).read_bytes()
