"""guard_command.py in a shared checkout: a command that moves the branch asks while another
session is live in the same folder. A worktree is its own checkout (ticket #41)."""

import os
from pathlib import Path

NOTES = "python-dev-sessions"


def test_guard_leaves_a_note(guard, repo: Path) -> None:
    assert guard("git status") == "allow"
    assert (repo / ".git" / NOTES / str(os.getpid())).exists()
    assert guard("git switch -c ticket/1") == "allow"
