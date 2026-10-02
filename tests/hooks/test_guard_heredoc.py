"""The command guard and heredocs: text that is only written passes; text that runs is denied.

Ticket 46. A heredoc with a quoted delimiter (`<<'EOF'`) that feeds `cat`, `tee`, `git`, `gh`
or `glab` is text; the guard does not read it. Any other heredoc, and every word outside
one, is read as before.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def on_branch(git) -> None:
    git("switch", "-q", "-c", "ticket/1")


@pytest.mark.parametrize(
    "command",
    [
        "cat > body.md <<'EOF'\nDo not use git commit --no-verify here.\nEOF",
        "gh issue create --title t --body-file - <<'EOF'\nnever git reset --hard\nEOF",
        "git commit -F - <<'EOF'\ndocs: say why git push --force is denied\nEOF",
        "git add . && git commit -m \"$(cat <<'EOF'\ndocs: git rebase is denied\nEOF\n)\"",
        "cat > body.md <<-'EOF'\n\tgit commit --amend is on the never list\n\tEOF",
    ],
    ids=["to a file", "issue body", "commit message", "substituted message", "tab-stripped"],
)
def test_heredoc_text_allowed(guard, command: str) -> None:
    assert guard(command) == "allow"


@pytest.mark.parametrize(
    "command",
    [
        "bash <<'EOF'\ngit commit --no-verify -m x\nEOF",
        "cat <<'EOF' | sh\ngit reset --hard HEAD~1\nEOF",
        "bash -c \"$(cat <<'EOF'\ngit push --force origin ticket/1\nEOF\n)\"",
        "cat > body.md <<EOF\n$(git reset --hard HEAD~1)\nEOF",
        "git commit -F - <<'EOF'\nmessage\nEOF\ngit reset --hard HEAD~1",
        "git commit --no-verify -F - <<'EOF'\nmessage\nEOF",
        "git commit -m \"$(cat <<'EOF'\nmessage\nEOF\n)\" --no-verify",
        "cat <<A <<'B'\n$(git reset --hard HEAD~1)\nA\ntext\nB",
        "cat <<< 'x'\ngit reset --hard HEAD~1\nx",
    ],
    ids=[
        "into a shell",
        "piped to a shell",
        "shell runs the substitution",
        "unquoted body substitutes",
        "command after the heredoc",
        "flag on the opening line",
        "flag after the substitution",
        "unquoted heredoc before a quoted one",
        "here-string is not a heredoc",
    ],
)
def test_heredoc_that_runs_denied(guard, command: str) -> None:
    assert guard(command) == "deny"
