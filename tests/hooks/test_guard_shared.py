"""guard_command.py in a shared checkout: a command that moves the branch asks while another
session is live in the same folder. A worktree is its own checkout (ticket #41)."""

import os
from pathlib import Path

import pytest

NOTES = "python-dev-sessions"


@pytest.fixture
def other_session(repo: Path) -> int:
    """A note for a live process that is not the hook's parent: the test's own parent."""
    folder = repo / ".git" / NOTES
    folder.mkdir(exist_ok=True)
    (folder / str(os.getppid())).touch()
    return os.getppid()


@pytest.mark.usefixtures("other_session")
@pytest.mark.parametrize(
    "command",
    ["git switch main", "git switch -c ticket/1", "git checkout main", "git branch -m ticket/2"],
    ids=["switch", "switch -c", "checkout", "branch -m"],
)
def test_moving_the_branch_asks(guard, command: str) -> None:
    assert guard(command) == "ask"


def test_dead_session_passes_and_its_note_goes(guard, repo: Path) -> None:
    ended = subprocess.Popen([sys.executable, "-c", "pass"])
    ended.wait()
    note = repo / ".git" / NOTES / str(ended.pid)
    note.parent.mkdir(exist_ok=True)
    note.touch()
    assert guard("git switch -c ticket/1") == "allow"
    assert not note.exists()


def test_guard_leaves_a_note(guard, repo: Path) -> None:
    assert guard("git status") == "allow"
    assert (repo / ".git" / NOTES / str(os.getpid())).exists()
    assert guard("git switch -c ticket/1") == "allow"
