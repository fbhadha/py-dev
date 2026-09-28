"""guard_command.py in a shared checkout: a command that moves the branch asks while another
session is live in the same folder. A worktree is its own checkout (ticket #41)."""

import os
import subprocess
import sys
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


@pytest.mark.usefixtures("other_session")
@pytest.mark.parametrize(
    "command",
    ["git worktree add ../w -b ticket/1 origin/main", "git status"],
    ids=["worktree add", "status"],
)
def test_staying_put_passes(guard, command: str) -> None:
    assert guard(command) == "allow"


@pytest.mark.usefixtures("other_session")
def test_env_off_passes(guard) -> None:
    assert guard("git switch -c ticket/1", env={"PYTHON_DEV_GUARD": "off"}) == "allow"


@pytest.mark.usefixtures("other_session")
def test_copilot_payload_asks_too(guard) -> None:
    assert guard("git switch -c ticket/1", copilot=True) == "ask"


@pytest.mark.usefixtures("other_session")
def test_worktree_is_its_own_checkout(hook, git, repo: Path) -> None:
    git("worktree", "add", "-q", "../w", "-b", "ticket/1")
    payload = {
        "sessionId": "s",
        "timestamp": 0,
        "cwd": str(repo.parent / "w"),
        "toolName": "bash",
        "toolArgs": {"command": "git switch -c ticket/2", "description": "run"},
    }
    assert hook("guard_command.py", payload, outside=True).decision == "allow"


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
