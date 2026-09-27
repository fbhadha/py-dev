"""guard_command.py: what lands on main asks, the never list is denied, a branch is free.

The same decisions arrive in Claude Code's payload shape and Copilot CLI's. Sending
content to another repo is `test_guard_other_repo.py`.
"""

import json
from pathlib import Path

import pytest

OFF = {"PYTHON_DEV_GUARD": "off"}


@pytest.mark.parametrize(
    ("command", "decision"),
    [
        ("git commit -m 'x'", "ask"),
        ("git merge ticket/1", "ask"),
        ("git push", "ask"),
        ("git push origin main", "ask"),
        ("git status && git log --oneline", "allow"),
        ("git switch -c ticket/1", "allow"),
    ],
    ids=[
        "commit asks",
        "merge asks",
        "bare push asks",
        "push origin main asks",
        "reads pass",
        "switch passes",
    ],
)
def test_on_main(guard, command: str, decision: str) -> None:
    assert guard(command) == decision


def test_on_main_copilot_payload_asks_too(guard) -> None:
    assert guard("git commit -m x", copilot=True) == "ask"


def test_on_main_copilot_string_tool_args_asks(hook, repo: Path) -> None:
    payload = {
        "cwd": str(repo),
        "toolName": "shell",
        "toolArgs": json.dumps({"command": "git commit -m x"}),
    }
    assert hook("guard_command.py", payload, outside=True).decision == "ask"


def test_env_off_commit_on_main_passes(guard) -> None:
    assert guard("git commit -m x", env=OFF) == "allow"


def test_env_off_force_push_still_denied(guard) -> None:
    assert guard("git push --force", env=OFF) == "deny"


@pytest.fixture
def on_branch(git) -> None:
    git("switch", "-q", "-c", "ticket/1")


@pytest.mark.usefixtures("on_branch")
@pytest.mark.parametrize(
    ("command", "decision"),
    [
        ("git commit -m 'task-1: adapter'", "allow"),
        ("git push -u origin ticket/1", "allow"),
        ("git merge origin/main", "allow"),
        ("git push origin ticket/1:main", "ask"),
        ("git switch main && git merge ticket/1", "ask"),
        ("gh pr merge 12 --merge", "ask"),
        ("glab mr merge 12", "ask"),
    ],
    ids=[
        "commit",
        "push branch",
        "merge main in",
        "push to main",
        "switch and merge",
        "gh merge",
        "glab merge",
    ],
)
def test_on_a_branch(guard, command: str, decision: str) -> None:
    assert guard(command) == decision


@pytest.mark.usefixtures("on_branch")
@pytest.mark.parametrize(
    "command",
    [
        "git push --force origin ticket/1",
        "git rebase main",
        "git commit --amend --no-edit",
        "git commit -n -m x",
        "git reset --hard HEAD~1",
        "PYTHON_DEV_GUARD=off git merge --no-ff ticket/1",
        "uv run pre-commit uninstall",
    ],
    ids=[
        "force-push",
        "rebase",
        "amend",
        "no-verify",
        "hard reset",
        "guard off inline",
        "pre-commit uninstall",
    ],
)
def test_never_list_denied(guard, command: str) -> None:
    assert guard(command) == "deny"


@pytest.mark.usefixtures("on_branch")
def test_edit_tool_payload_ignored(hook) -> None:
    payload = {"tool_name": "Edit", "tool_input": {"file_path": "x"}}
    assert hook("guard_command.py", payload).decision == "allow"


@pytest.mark.usefixtures("on_branch")
def test_garbage_payload_fails_open(hook) -> None:
    assert hook("guard_command.py", {"tool_input": 5}).decision == "allow"
