"""guard_command.py: sending content to a repo that is not this project's origin asks.

Reads and writes to the project's own repo (`origin`, here `me/proj`) do not.
"""

import pytest


@pytest.fixture(autouse=True)
def on_branch(git) -> None:
    git("switch", "-q", "-c", "ticket/1")


@pytest.mark.parametrize(
    ("command", "decision"),
    [
        ("gh issue create -R fbhadha/py-dev --title x --body-file d.md", "ask"),
        ("gh api -X POST repos/fbhadha/py-dev/issues -f title=x", "ask"),
        ("gh gist create notes.md", "ask"),
        ("git push fork ticket/1", "ask"),
        ("git push https://github.com/other/x.git ticket/1", "ask"),
        ("gh issue view -R fbhadha/py-dev 12", "allow"),
        ("gh issue create --title x --body y", "allow"),
        ("gh issue create -R me/proj --title x", "allow"),
        ("gh api repos/fbhadha/py-dev/releases/latest", "allow"),
    ],
    ids=[
        "issue create -R other asks",
        "api POST other asks",
        "gist asks",
        "push to a fork asks",
        "push to a URL asks",
        "issue view -R other passes",
        "own issue create passes",
        "issue create -R own passes",
        "api GET passes",
    ],
)
def test_other_repo(guard, command: str, decision: str) -> None:
    assert guard(command) == decision
