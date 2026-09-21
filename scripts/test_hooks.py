#!/usr/bin/env python3
"""Run the hook scripts against a scratch git repo and check every decision they make.

CI runs this. It builds a throwaway repo with one protected file (pyproject.toml)
and one source file committed, then drives each hook with payloads in both
harnesses' shapes and asserts the answer: ask, deny, allow, block, or nothing.

Usage: python scripts/test_hooks.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOKS = ROOT / "scripts" / "hooks"
COMMIT_GATE = ROOT / "skills" / "py-baseline" / "templates" / "check_protected_commit.py"
FAILURES: list[str] = []


def run(script: Path, payload: dict | None, cwd: Path, args: list[str] | None = None, env=None):
    return subprocess.run(
        [sys.executable, str(script), *(args or [])],
        input=json.dumps(payload) if payload is not None else "",
        capture_output=True,
        text=True,
        cwd=cwd,
        env={**os.environ, **(env or {})},
        check=False,
    )


def decision_of(result: subprocess.CompletedProcess[str]) -> str:
    if not result.stdout.strip():
        return "allow"
    data = json.loads(result.stdout)
    return data.get("permissionDecision") or data.get("decision") or "allow"


def expect(label: str, got: str, want: str) -> None:
    mark = "ok " if got == want else "FAIL"
    print(f"{mark} {label}: {got}")
    if got != want:
        FAILURES.append(f"{label}: wanted {want}, got {got}")


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def make_repo(tmp: Path) -> Path:
    repo = tmp / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "pyproject.toml").write_text('[project]\nname = "x"\n', encoding="utf-8")
    (repo / "src" / "x.py").write_text("X = 1\n", encoding="utf-8")
    (repo / "README.md").write_text("# x\n", encoding="utf-8")
    git(repo, "init", "-q")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "add", ".")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "init")
    return repo


def edit_payload(path: str, session: str, copilot: bool = False) -> dict:
    if copilot:
        return {"sessionId": session, "toolName": "edit", "toolArgs": json.dumps({"path": path})}
    return {"session_id": session, "tool_name": "Edit", "tool_input": {"file_path": path}}


def bash_payload(command: str, session: str) -> dict:
    return {"session_id": session, "tool_name": "Bash", "tool_input": {"command": command}}


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(Path(tmp))
        s1 = f"t-{uuid.uuid4()}"

        # before intake (no docs/agents/mode.md): the protected list applies, source never does
        expect(
            "intake: edit tracked pyproject asks",
            decision_of(run(HOOKS / "guard_edit.py", edit_payload("pyproject.toml", s1), repo)),
            "ask",
        )
        expect(
            "intake: edit tracked src/x.py allowed (formatters rewrite source)",
            decision_of(run(HOOKS / "guard_edit.py", edit_payload("src/x.py", s1), repo)),
            "allow",
        )
        expect(
            "intake: write new file allowed",
            decision_of(run(HOOKS / "guard_edit.py", edit_payload("src/new.py", s1), repo)),
            "allow",
        )
        expect(
            "copilot payload shape asks too",
            decision_of(
                run(HOOKS / "guard_edit.py", edit_payload("pyproject.toml", s1, copilot=True), repo)
            ),
            "ask",
        )

        # one yes: after a recorded edit, the same path passes
        run(HOOKS / "record_edit.py", edit_payload("pyproject.toml", s1), repo)
        expect(
            "after approval, pyproject passes",
            decision_of(run(HOOKS / "guard_edit.py", edit_payload("pyproject.toml", s1), repo)),
            "allow",
        )
        expect(
            "other session still asks",
            decision_of(
                run(HOOKS / "guard_edit.py", edit_payload("pyproject.toml", "other"), repo)
            ),
            "ask",
        )

        # shell guard
        expect(
            "deny force-push",
            decision_of(
                run(
                    HOOKS / "guard_command.py",
                    bash_payload("git push --force origin main", s1),
                    repo,
                )
            ),
            "deny",
        )
        expect(
            "sed -i on tracked README asks",
            decision_of(
                run(HOOKS / "guard_command.py", bash_payload("sed -i 's/a/b/' README.md", s1), repo)
            ),
            "ask",
        )
        expect(
            "uv add asks (pyproject) unless approved: approved above so allow",
            decision_of(run(HOOKS / "guard_command.py", bash_payload("uv add requests", s1), repo)),
            "allow",
        )
        expect(
            "uv add asks in a fresh session",
            decision_of(
                run(HOOKS / "guard_command.py", bash_payload("uv add requests", "fresh"), repo)
            ),
            "ask",
        )
        expect(
            "plain ls allowed",
            decision_of(run(HOOKS / "guard_command.py", bash_payload("ls -la", s1), repo)),
            "allow",
        )

        # an approved command's side effects are approved too: uv add rewrites uv.lock
        s3 = f"t-{uuid.uuid4()}"
        (repo / "uv.lock").write_text("lock v1\n", encoding="utf-8")
        git(repo, "add", "uv.lock")
        git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "lock")
        expect(
            "uv add asks before running",
            decision_of(run(HOOKS / "guard_command.py", bash_payload("uv add requests", s3), repo)),
            "ask",
        )
        (repo / "pyproject.toml").write_text(
            '[project]\nname = "x"\ndependencies = ["requests"]\n', encoding="utf-8"
        )
        (repo / "uv.lock").write_text("lock v2\n", encoding="utf-8")
        run(HOOKS / "record_edit.py", bash_payload("uv add requests", s3), repo)
        expect(
            "stop gate passes: pyproject and uv.lock covered by the one yes",
            decision_of(run(HOOKS / "stop_gate.py", {"session_id": s3}, repo)),
            "allow",
        )
        git(repo, "checkout", "--", "pyproject.toml", "uv.lock")

        # a formatter never asks, and what it rewrote is approved
        s4 = f"t-{uuid.uuid4()}"
        expect(
            "pre-commit run does not ask",
            decision_of(
                run(
                    HOOKS / "guard_command.py",
                    bash_payload("uv run pre-commit run --all-files", s4),
                    repo,
                )
            ),
            "allow",
        )
        (repo / "README.md").write_text("# x\n\n", encoding="utf-8")
        run(HOOKS / "record_edit.py", bash_payload("uv run pre-commit run --all-files", s4), repo)
        expect(
            "stop gate passes after a formatter touched README",
            decision_of(run(HOOKS / "stop_gate.py", {"session_id": s4}, repo)),
            "allow",
        )
        git(repo, "checkout", "--", "README.md")

        # an unknown command that rewrote a protected file still blocks at stop
        s5 = f"t-{uuid.uuid4()}"
        run(HOOKS / "guard_command.py", bash_payload("python3 mystery.py", s5), repo)
        (repo / "README.md").write_text("# rewritten\n", encoding="utf-8")
        run(HOOKS / "record_edit.py", bash_payload("python3 mystery.py", s5), repo)
        expect(
            "stop gate blocks a protected change from an unknown command",
            decision_of(run(HOOKS / "stop_gate.py", {"session_id": s5}, repo)),
            "block",
        )
        git(repo, "checkout", "--", "README.md")

        # stop gate: modified protected file without approval blocks; with approval passes
        (repo / "README.md").write_text("# changed\n", encoding="utf-8")
        expect(
            "stop gate blocks unapproved README change",
            decision_of(run(HOOKS / "stop_gate.py", {"session_id": s1}, repo)),
            "block",
        )
        run(HOOKS / "record_edit.py", edit_payload("README.md", s1), repo)
        expect(
            "stop gate passes once README approved",
            decision_of(run(HOOKS / "stop_gate.py", {"session_id": s1}, repo)),
            "allow",
        )

        # after intake: mode.md exists, the same list is protected
        (repo / "docs" / "agents").mkdir(parents=True)
        (repo / "docs" / "agents" / "mode.md").write_text(
            "mode: guide\nprotect-existing-files: on\n", encoding="utf-8"
        )
        s2 = f"t-{uuid.uuid4()}"
        expect(
            "on: source file edit allowed",
            decision_of(run(HOOKS / "guard_edit.py", edit_payload("src/x.py", s2), repo)),
            "allow",
        )
        expect(
            "on: pyproject edit asks",
            decision_of(run(HOOKS / "guard_edit.py", edit_payload("pyproject.toml", s2), repo)),
            "ask",
        )

        # off switches
        (repo / "docs" / "agents" / "mode.md").write_text(
            "mode: guide\nprotect-existing-files: off\n", encoding="utf-8"
        )
        expect(
            "mode.md off: pyproject edit allowed",
            decision_of(run(HOOKS / "guard_edit.py", edit_payload("pyproject.toml", s2), repo)),
            "allow",
        )
        (repo / "docs" / "agents" / "mode.md").write_text("mode: guide\n", encoding="utf-8")
        expect(
            "env off: pyproject edit allowed",
            decision_of(
                run(
                    HOOKS / "guard_edit.py",
                    edit_payload("pyproject.toml", s2),
                    repo,
                    env={"PYTHON_DEV_GUARD": "off"},
                )
            ),
            "allow",
        )

        # ask-once: the first protected change asks, that yes covers the session
        msg = repo / "msg.txt"
        (repo / "docs" / "agents" / "mode.md").write_text(
            "mode: guide\nprotect-existing-files: ask-once\n", encoding="utf-8"
        )
        s6 = f"t-{uuid.uuid4()}"
        expect(
            "ask-once: first protected edit asks",
            decision_of(run(HOOKS / "guard_edit.py", edit_payload("pyproject.toml", s6), repo)),
            "ask",
        )
        run(HOOKS / "record_edit.py", edit_payload("pyproject.toml", s6), repo)
        expect(
            "ask-once: a different protected file now passes",
            decision_of(run(HOOKS / "guard_edit.py", edit_payload("README.md", s6), repo)),
            "allow",
        )
        expect(
            "ask-once: a writing command now passes too",
            decision_of(
                run(HOOKS / "guard_command.py", bash_payload("sed -i 's/a/b/' README.md", s6), repo)
            ),
            "allow",
        )
        (repo / "README.md").write_text("# once\n", encoding="utf-8")
        expect(
            "ask-once: stop gate passes on the session's yes",
            decision_of(run(HOOKS / "stop_gate.py", {"session_id": s6}, repo)),
            "allow",
        )
        git(repo, "add", "README.md")
        msg.write_text("update readme, no approved line\n", encoding="utf-8")
        expect(
            "ask-once: commit gate does not demand an approved line",
            "passed" if run(COMMIT_GATE, None, repo, [str(msg)]).returncode == 0 else "refused",
            "passed",
        )
        git(repo, "reset", "-q", "README.md")
        git(repo, "checkout", "--", "README.md")
        (repo / "docs" / "agents" / "mode.md").write_text("mode: guide\n", encoding="utf-8")

        # session start prints the status line
        start = run(HOOKS / "session_start.py", {}, repo)
        expect(
            "session start names the guard",
            "named" if "python-dev guards active" in start.stdout else "silent",
            "named",
        )

        # commit-msg gate in the target repo (mode.md says nothing about the guard: per file)
        (repo / "README.md").write_text("# per file\n", encoding="utf-8")
        git(repo, "add", "README.md")
        msg.write_text("update readme\n", encoding="utf-8")
        expect(
            "commit gate refuses unapproved protected change",
            "refused" if run(COMMIT_GATE, None, repo, [str(msg)]).returncode == 1 else "passed",
            "refused",
        )
        msg.write_text("update readme\n\napproved: README.md\n", encoding="utf-8")
        expect(
            "commit gate passes with approved line",
            "passed" if run(COMMIT_GATE, None, repo, [str(msg)]).returncode == 0 else "refused",
            "passed",
        )

        # garbage never blocks
        broken = subprocess.run(
            [sys.executable, str(HOOKS / "guard_edit.py")],
            input="not json",
            capture_output=True,
            text=True,
            cwd=repo,
            check=False,
        )
        expect(
            "garbage payload fails open",
            "allow" if broken.returncode == 0 and not broken.stdout else "blocked",
            "allow",
        )

    if FAILURES:
        print("\nHOOK TESTS FAILED:")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    print("\nall hook checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
