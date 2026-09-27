"""check_test_diff.py: a deleted test, an added skip or fewer assertions refuse the change.

Drives this repo's copy under scripts/; the last test proves it is the template.
"""

from pathlib import Path

SCRIPT = "scripts/check_test_diff.py"
TEMPLATE = "skills/py-baseline/templates/check_test_diff.py"
RANGE = "main...HEAD"


def test_source_only_change_passes(check, repo: Path, git) -> None:
    git("switch", "-q", "-c", "ticket/2")
    (repo / "src" / "x.py").write_text("X = 2\n", encoding="utf-8")
    git("commit", "-q", "-am", "src only")
    assert check(SCRIPT, RANGE).decision == "passed"


def test_deleted_test_refused(check, repo: Path, git) -> None:
    git("switch", "-q", "-c", "ticket/2")
    tests = repo / "tests" / "test_x.py"
    tests.write_text("def test_one():\n    assert 1 == 1\n    assert 2 == 2\n", encoding="utf-8")
    git("commit", "-q", "-am", "drop test_two")
    assert check(SCRIPT, RANGE).decision == "refused"


def test_added_skip_refused(check, repo: Path, git) -> None:
    git("switch", "-q", "-c", "ticket/3")
    tests = repo / "tests" / "test_x.py"
    # built in two parts so this repo's own test-diff check does not read it as a skip
    marker = "@pytest.mark." + "skip(reason='later')\n"
    tests.write_text("import pytest\n\n\n" + marker + tests.read_text(encoding="utf-8"))
    git("commit", "-q", "-am", "skip test_one")
    assert check(SCRIPT, RANGE).decision == "refused"


def test_override_in_a_commit_message_passes(check, repo: Path, git) -> None:
    git("switch", "-q", "-c", "ticket/3")
    tests = repo / "tests" / "test_x.py"
    marker = "@pytest.mark." + "skip(reason='later')\n"
    tests.write_text("import pytest\n\n\n" + marker + tests.read_text(encoding="utf-8"))
    git("commit", "-q", "-am", "skip test_one")
    reason = "task-3\n\ntest-override: the user said test_one waits on the vendor fixture"
    git("commit", "-q", "--allow-empty", "-m", reason)
    assert check(SCRIPT, RANGE).decision == "passed"


def test_fewer_assertions_refused(check, repo: Path, git) -> None:
    git("switch", "-q", "-c", "ticket/4")
    tests = repo / "tests" / "test_x.py"
    tests.write_text(
        "def test_one():\n    assert 1 == 1\n\n\ndef test_two():\n    assert 3 == 3\n",
        encoding="utf-8",
    )
    git("commit", "-q", "-am", "fewer asserts")
    assert check(SCRIPT, RANGE).decision == "refused"


def test_added_test_passes(check, repo: Path, git) -> None:
    git("switch", "-q", "-c", "ticket/5")
    tests = repo / "tests" / "test_x.py"
    original = tests.read_text(encoding="utf-8")
    tests.write_text(original + "\n\ndef test_three():\n    assert 4 == 4\n", encoding="utf-8")
    git("commit", "-q", "-am", "add test_three")
    assert check(SCRIPT, RANGE).decision == "passed"


def test_copy_matches_template(root: Path) -> None:
    assert (root / SCRIPT).read_bytes() == (root / TEMPLATE).read_bytes()
