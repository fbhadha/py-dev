"""The command guard and heredocs: text that is only written passes; text that runs is denied.

Ticket 46. The guard does not read a heredoc's body when the whole command is one of a few
exact shapes that only write text: `git commit`, `gh issue|pr create|comment|edit` or `cat`
to a file, plain arguments, a single-quoted delimiter (`<<'EOF'`), nothing after the closing
line. Every other command is read whole, as before.
"""

from __future__ import annotations

import pytest

RESET = "git reset --hard HEAD~1"


@pytest.fixture(autouse=True)
def on_branch(git) -> None:
    git("switch", "-q", "-c", "ticket/1")


@pytest.mark.parametrize(
    "command",
    [
        "cat > body.md <<'EOF'\nDo not use git commit --no-verify here.\nEOF",
        f"cat <<'EOF' > body.md\nnever {RESET}\nEOF\n",
        f"gh issue create --title t --body-file - <<'EOF'\nnever {RESET}\nEOF",
        "git commit -F - <<'EOF'\ndocs: say why git push --force is denied\nEOF",
        "git add . && git commit -F - <<'EOF'\ndocs: git rebase is denied\nEOF",
        f"gh pr create --title \"46: the guard's rule\" --body-file - <<'EOF'\n{RESET}\nEOF",
    ],
    ids=[
        "to a file",
        "redirect after the opener",
        "issue body",
        "commit message",
        "after another command",
        "quoted title",
    ],
)
def test_heredoc_text_allowed(guard, command: str) -> None:
    assert guard(command) == "allow"


@pytest.mark.parametrize(
    "command",
    [
        f"bash <<'EOF'\n{RESET}\nEOF",
        f"cat <<'EOF' | sh\n{RESET}\nEOF",
        f"bash -c \"$(cat <<'EOF'\n{RESET}\nEOF\n)\"",
        f"cat > body.md <<EOF\n$({RESET})\nEOF",
        f"git commit -F - <<'EOF'\nmessage\nEOF\n{RESET}",
        "git commit --no-verify -F - <<'EOF'\nmessage\nEOF",
        "git commit -m \"$(cat <<'EOF'\nmessage\nEOF\n)\" --no-verify",
        f"cat <<A <<'B'\n$({RESET})\nA\ntext\nB",
        f"cat <<< 'x'\n{RESET}\nx",
        f"cat > s.sh <<'EOF'\n{RESET}\nEOF\nsh s.sh",
        f"cat > >(sh) <<'EOF'\n{RESET}\nEOF",
        f"tee >(sh) <<'EOF'\n{RESET}\nEOF",
        f"git status & bash <<'EOF'\n{RESET}\nEOF",
        f"git -c alias.x='!sh' x <<'EOF'\n{RESET}\nEOF",
        f"git bisect run sh <<'EOF'\n{RESET}\nEOF",
        f"gh alias import - <<'EOF'\nx: '!{RESET}'\nEOF\ngh x",
        f"git commit -m 'a <<\"EOF\" b'\n{RESET}\nEOF",
        f"git commit -m \"see <<'EOF'\"\n{RESET}\nEOF",
        f"cat x # <<'EOF'\n{RESET}",
        f"cat <<'EOF' \\\n| sh\n{RESET}\nEOF",
        f"git commit -m \"$(cat <<'EOF'\none\nEOF) two\"; {RESET}; echo \"$(cat <<'EOF'\nEOF\n)\"",
        f"git commit -F - <<'EOF'\n{RESET}",
        f"git commit -m \"$(cat <<'EOF'\nmsg\n)\"\n{RESET}\n: \"\nEOF\n)\"",
        f"git commit -m \"$(cat <<'EOF'\nnever {RESET}\nEOF\n)\"",
        f"git commit -F - <<'EOF'\nEOF\n{RESET}\nEOF",
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
        "file written then run",
        "cat into a process substitution",
        "tee into a process substitution",
        "background separator",
        "git alias runs a shell",
        "git bisect runs a shell",
        "gh alias import",
        "opener inside single quotes",
        "opener inside double quotes",
        "opener inside a comment",
        "line continuation",
        "terminator followed by a bracket",
        "no terminator",
        "bracket closes a substitution early",
        "substituted message is read",
        "body ends before the last line",
    ],
)
def test_heredoc_that_runs_denied(guard, command: str) -> None:
    assert guard(command) == "deny"
