"""guard_command.py on a shaping branch: a commit carrying src/ or tests/ asks; docs pass.

A prototype branch is free. Shaping decides; it never builds (persona section 3).
"""

from pathlib import Path

import pytest


@pytest.fixture
def shaping(repo: Path, git) -> Path:
    git("switch", "-q", "-c", "shaping/idea")
    (repo / "docs").mkdir()
    (repo / "docs" / "note.md").write_text("# note\n", encoding="utf-8")
    git("add", "docs/note.md")  # literal-ok: a path in the scratch repo
    return repo


def test_commit_of_docs_passes(guard, shaping: Path) -> None:
    assert guard("git commit -m 'term: note'") == "allow"


def test_staged_docs_only_unstaged_src_plain_commit_passes(guard, shaping: Path) -> None:
    (shaping / "src" / "x.py").write_text("X = 3\n", encoding="utf-8")
    assert guard("git commit -m 'term: note'") == "allow"


def test_commit_all_with_src_asks(guard, shaping: Path) -> None:
    (shaping / "src" / "x.py").write_text("X = 3\n", encoding="utf-8")
    assert guard("git commit -am 'build it'") == "ask"


def test_staged_src_asks(guard, shaping: Path, git) -> None:
    (shaping / "src" / "x.py").write_text("X = 3\n", encoding="utf-8")
    git("add", "src/x.py")
    assert guard("git commit -m 'build it'") == "ask"


def test_staged_src_copilot_payload_asks_too(guard, shaping: Path, git) -> None:
    (shaping / "src" / "x.py").write_text("X = 3\n", encoding="utf-8")
    git("add", "src/x.py")
    assert guard("git commit -m x", copilot=True) == "ask"


def test_prototype_branch_commit_with_src_passes(guard, repo: Path, git) -> None:
    git("switch", "-q", "-c", "prototype/idea")
    (repo / "src" / "x.py").write_text("X = 3\n", encoding="utf-8")
    git("add", "src/x.py")
    assert guard("git commit -m 'proto'") == "allow"
