"""guard_command.py and heredocs: text that is only written down is not a command.

A heredoc body that feeds a file or a message is data. A body fed to a shell, piped on,
or able to run a substitution is still read, and so is everything outside the body.
Tickets #46 and #54; the owner chose this narrow rule on 2026-09-28.
"""

import pytest


@pytest.fixture(autouse=True)
def on_branch(git) -> None:
    git("switch", "-q", "-c", "ticket/1")


@pytest.mark.parametrize(
    "command",
    [
        "cat > body.md <<'EOF'\nthe agent must never run git push --force\nEOF",
        "cat > body.md <<EOF\nthe never list names git rebase main\nEOF",
        "git commit -F - <<'EOF'\ntask-1: the guard denies PYTHON_DEV_GUARD=off in a command\nEOF",
    ],
    ids=["quoted heredoc to a file", "plain heredoc to a file", "commit message names the switch"],
)
def test_text_only_written_down_passes(guard, command: str) -> None:
    assert guard(command) == "allow"


@pytest.mark.parametrize(
    "command",
    [
        "bash <<'EOF'\ngit push --force origin ticket/1\nEOF",
        "cat <<'EOF' | sh\ngit reset --hard HEAD~1\nEOF",
        "cat > body.md <<EOF\n$(git push --force origin ticket/1)\nEOF",
        "cat > body.md <<'EOF'\nhello\nEOF\ngit push --force origin ticket/1",
        "git commit --amend -F - <<'EOF'\nhello\nEOF",
    ],
    ids=[
        "heredoc fed to a shell",
        "heredoc piped to a shell",
        "substitution inside a plain heredoc",
        "forbidden command after the heredoc",
        "forbidden flag on the heredoc's own line",
    ],
)
def test_text_that_runs_is_still_denied(guard, command: str) -> None:
    assert guard(command) == "deny"
