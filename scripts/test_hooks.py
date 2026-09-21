#!/usr/bin/env python3
"""Run the hook scripts and the baseline's test-diff check against a scratch git repo.

CI runs this. It builds a throwaway repo on `main`, drives the command guard with
payloads in both harnesses' shapes on main and on a branch, and asserts the answer:
ask, deny or allow. Then the stop gate, the session-start line, and
check_test_diff.py on a weakened and a clean test change.

Usage: python scripts/test_hooks.py
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOKS = ROOT / "scripts" / "hooks"
GUARD = HOOKS / "guard_command.py"
TEST_DIFF = ROOT / "skills" / "py-baseline" / "templates" / "check_test_diff.py"
FAILURES: list[str] = []
ORIGINAL_TESTS = (
    "def test_one():\n    assert 1 == 1\n    assert 2 == 2\n\n\n"
    "def test_two():\n    assert 3 == 3\n"
)
GIT_ID = ["-c", "user.name=t", "-c", "user.email=t@t"]


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
    subprocess.run(["git", *GIT_ID, *args], cwd=cwd, check=True, capture_output=True)


def make_repo(tmp: Path) -> Path:
    repo = tmp / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "pyproject.toml").write_text('[project]\nname = "x"\n', encoding="utf-8")
    (repo / "src" / "x.py").write_text("X = 1\n", encoding="utf-8")
    (repo / "tests" / "test_x.py").write_text(ORIGINAL_TESTS, encoding="utf-8")
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "init")
    return repo


def bash(command: str, session: str, *, copilot: bool = False) -> dict:
    if copilot:
        return {
            "sessionId": session,
            "toolName": "shell",
            "toolArgs": json.dumps({"command": command}),
        }
    return {"session_id": session, "tool_name": "Bash", "tool_input": {"command": command}}


def guard(command: str, repo: Path, session: str, **kw) -> str:
    env = kw.pop("env", None)
    return decision_of(run(GUARD, bash(command, session, **kw), repo, env=env))


def check_guard(repo: Path) -> None:
    s = f"t-{uuid.uuid4()}"
    # on main: anything that lands on main asks
    expect("main: commit asks", guard("git commit -m 'x'", repo, s), "ask")
    expect("main: merge asks", guard("git merge ticket/1", repo, s), "ask")
    expect("main: bare push asks", guard("git push", repo, s), "ask")
    expect("main: push origin main asks", guard("git push origin main", repo, s), "ask")
    expect("main: copilot payload asks too", guard("git commit -m x", repo, s, copilot=True), "ask")
    expect(
        "main: reading commands pass", guard("git status && git log --oneline", repo, s), "allow"
    )
    expect("main: switch to a branch passes", guard("git switch -c ticket/1", repo, s), "allow")
    expect(
        "env off: commit on main passes",
        guard("git commit -m x", repo, s, env={"PYTHON_DEV_GUARD": "off"}),
        "allow",
    )
    expect(
        "env off: force-push still denied",
        guard("git push --force", repo, s, env={"PYTHON_DEV_GUARD": "off"}),
        "deny",
    )
    # on a branch: commit, push and syncing from main are free
    git(repo, "switch", "-q", "-c", "ticket/1")
    expect("branch: commit passes", guard("git commit -m 'task-1: adapter'", repo, s), "allow")
    expect(
        "branch: push to the branch passes", guard("git push -u origin ticket/1", repo, s), "allow"
    )
    expect("branch: merging main in passes", guard("git merge origin/main", repo, s), "allow")
    expect("branch: push to main asks", guard("git push origin ticket/1:main", repo, s), "ask")
    expect(
        "branch: switch to main and merge asks",
        guard("git switch main && git merge ticket/1", repo, s),
        "ask",
    )
    expect("branch: gh pr merge asks", guard("gh pr merge 12 --merge", repo, s), "ask")
    expect("branch: glab mr merge asks", guard("glab mr merge 12", repo, s), "ask")
    # the never list, on any branch
    expect("force-push denied", guard("git push --force origin ticket/1", repo, s), "deny")
    expect("rebase denied", guard("git rebase main", repo, s), "deny")
    expect("amend denied", guard("git commit --amend --no-edit", repo, s), "deny")
    expect("no-verify denied", guard("git commit -n -m x", repo, s), "deny")
    expect("hard reset denied", guard("git reset --hard HEAD~1", repo, s), "deny")
    expect(
        "edit tool payload ignored by the command guard",
        decision_of(run(GUARD, {"tool_name": "Edit", "tool_input": {"file_path": "x"}}, repo)),
        "allow",
    )
    expect("garbage payload fails open", decision_of(run(GUARD, {"tool_input": 5}, repo)), "allow")
    git(repo, "switch", "-q", "main")


def check_stop_and_start(repo: Path) -> None:
    expect(
        "stop gate passes on a clean tree",
        decision_of(run(HOOKS / "stop_gate.py", {"session_id": "s"}, repo)),
        "allow",
    )
    if shutil.which("ruff"):
        (repo / "pyproject.toml").write_text(
            '[project]\nname = "x"\n[tool.ruff]\nline-length = 100\n', encoding="utf-8"
        )
        (repo / "src" / "y.py").write_text("import os\n", encoding="utf-8")
        expect(
            "stop gate blocks red ruff",
            decision_of(run(HOOKS / "stop_gate.py", {"session_id": "s"}, repo)),
            "block",
        )
        expect(
            "stop gate never blocks twice",
            decision_of(
                run(HOOKS / "stop_gate.py", {"session_id": "s", "stop_hook_active": True}, repo)
            ),
            "allow",
        )
        (repo / "src" / "y.py").unlink()
        git(repo, "checkout", "--", "pyproject.toml")
    else:
        print("skip stop gate ruff check: ruff not on PATH")
    start = run(HOOKS / "session_start.py", {}, repo).stdout
    expect(
        "session start names the guard",
        "named" if "python-dev guards active" in start else "silent",
        "named",
    )
    expect(
        "session start names the branch", "named" if "Branch: main" in start else "silent", "named"
    )


def test_diff(repo: Path) -> str:
    result = run(TEST_DIFF, None, repo, ["main...HEAD"])
    return "passed" if result.returncode == 0 else "refused"


def check_test_diff(repo: Path) -> None:
    tests = repo / "tests" / "test_x.py"
    git(repo, "switch", "-q", "-c", "ticket/2")
    (repo / "src" / "x.py").write_text("X = 2\n", encoding="utf-8")
    git(repo, "commit", "-q", "-am", "src only")
    expect("test-diff: source-only change passes", test_diff(repo), "passed")
    tests.write_text("def test_one():\n    assert 1 == 1\n    assert 2 == 2\n", encoding="utf-8")
    git(repo, "commit", "-q", "-am", "drop test_two")
    expect("test-diff: deleted test refused", test_diff(repo), "refused")
    git(repo, "switch", "-q", "main")
    git(repo, "branch", "-q", "-D", "ticket/2")
    git(repo, "switch", "-q", "-c", "ticket/3")
    tests.write_text(
        "import pytest\n\n\n@pytest.mark.skip(reason='later')\n" + ORIGINAL_TESTS, encoding="utf-8"
    )
    git(repo, "commit", "-q", "-am", "skip test_one")
    expect("test-diff: added skip refused", test_diff(repo), "refused")
    git(
        repo,
        "commit",
        "-q",
        "--allow-empty",
        "-m",
        "task-3\n\ntest-override: the user said test_one waits on the vendor fixture",
    )
    expect("test-diff: override in a commit message passes", test_diff(repo), "passed")
    git(repo, "switch", "-q", "main")
    git(repo, "branch", "-q", "-D", "ticket/3")
    git(repo, "switch", "-q", "-c", "ticket/4")
    tests.write_text(
        "def test_one():\n    assert 1 == 1\n\n\ndef test_two():\n    assert 3 == 3\n",
        encoding="utf-8",
    )
    git(repo, "commit", "-q", "-am", "fewer asserts")
    expect("test-diff: fewer assertions refused", test_diff(repo), "refused")
    git(repo, "switch", "-q", "main")
    git(repo, "branch", "-q", "-D", "ticket/4")
    git(repo, "switch", "-q", "-c", "ticket/5")
    tests.write_text(
        ORIGINAL_TESTS + "\n\ndef test_three():\n    assert 4 == 4\n", encoding="utf-8"
    )
    git(repo, "commit", "-q", "-am", "add test_three")
    expect("test-diff: added test passes", test_diff(repo), "passed")
    git(repo, "switch", "-q", "main")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(Path(tmp))
        check_guard(repo)
        check_stop_and_start(repo)
        check_test_diff(repo)
    if FAILURES:
        print("\nHOOK TESTS FAILED:")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    print("\nall hook checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
