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
        'git add . && git commit -m "$(cat <<\'EOF\'\ndocs: git rebase is denied\nEOF\n)"',
        "cat > body.md <<-'EOF'\n\tgit commit --amend is on the never list\n\tEOF",
    ],
    ids=["to a file", "issue body", "commit message", "substituted message", "tab-stripped"],
)
def test_heredoc_text_allowed(guard, command: str) -> None:
    assert guard(command) == "allow"
