"""Fixtures that drive the hooks and the baseline's scripts against a scratch git repo.

Every test gets its own repo on `main`. A hook is a separate process the harness would
start, so `hook` runs it that way: payload on stdin, decision read from its JSON.
`outside=True` starts it from above the repo with the repo only in the payload's `cwd`,
as Copilot CLI does. `check` runs a baseline script on a git range: passed or refused.
The walkthrough is `docs/howto/add-a-hook-test.md`.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple

import pytest

ROOT = Path(__file__).resolve().parent.parent
HOOKS = ROOT / "scripts" / "hooks"
GIT_ID = ["-c", "user.name=t", "-c", "user.email=t@t"]
ORIGINAL_TESTS = (
    "def test_one():\n    assert 1 == 1\n    assert 2 == 2\n\n\n"
    "def test_two():\n    assert 3 == 3\n"
)


class Answer(NamedTuple):
    decision: str  # a hook: allow, ask, deny or block; a check: passed or refused
    stdout: str
    returncode: int


def decision_of(stdout: str) -> str:
    """A hook that prints nothing allows; otherwise the decision is in its JSON."""
    if not stdout.strip():
        return "allow"
    data = json.loads(stdout)
    return data.get("permissionDecision") or data.get("decision") or "allow"


def run_script(
    script: Path,
    payload: dict | None,
    cwd: Path,
    args: list[str] | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *(args or [])],
        input=json.dumps(payload) if payload is not None else "",
        capture_output=True,
        text=True,
        cwd=cwd,
        env={**os.environ, **(env or {})},
        check=False,
    )


def bash_payload(command: str, session: str, repo: Path, *, copilot: bool) -> dict:
    """A Bash tool call, in the shape Claude Code sends or the one Copilot CLI 1.0.88 sends."""
    if copilot:
        return {
            "sessionId": session,
            "timestamp": 0,
            "cwd": str(repo),
            "toolName": "bash",
            "toolArgs": {"command": command, "description": "run"},
        }
    return {"session_id": session, "tool_name": "Bash", "tool_input": {"command": command}}


@pytest.fixture
def root() -> Path:
    return ROOT


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A scratch git repo on main: src/x.py, tests/test_x.py, remotes `origin` and `fork`."""
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "pyproject.toml").write_text('[project]\nname = "x"\n', encoding="utf-8")
    (repo / "src" / "x.py").write_text("X = 1\n", encoding="utf-8")
    (repo / "tests" / "test_x.py").write_text(ORIGINAL_TESTS, encoding="utf-8")
    for args in (
        ("init", "-q", "-b", "main"),
        ("remote", "add", "origin", "git@github.com:me/proj.git"),
        ("remote", "add", "fork", "https://github.com/other/proj.git"),
        ("add", "."),
        ("commit", "-q", "-m", "init"),
    ):
        subprocess.run(["git", *GIT_ID, *args], cwd=repo, check=True, capture_output=True)
    return repo


@pytest.fixture
def git(repo: Path) -> Callable[..., None]:
    def call(*args: str) -> None:
        subprocess.run(["git", *GIT_ID, *args], cwd=repo, check=True, capture_output=True)

    return call


@pytest.fixture
def hook(repo: Path) -> Callable[..., Answer]:
    """`hook("stop_gate.py", payload)` runs that hook in the repo; `outside=True` from above it."""

    def call(
        name: str,
        payload: dict | None,
        *,
        outside: bool = False,
        env: dict[str, str] | None = None,
    ) -> Answer:
        result = run_script(HOOKS / name, payload, repo.parent if outside else repo, env=env)
        return Answer(decision_of(result.stdout), result.stdout, result.returncode)

    return call


@pytest.fixture
def guard(hook: Callable[..., Answer], repo: Path) -> Callable[..., str]:
    """`guard("git commit -m x")`: the command guard's decision; `copilot=True` for its shape."""
    session = f"t-{uuid.uuid4()}"

    def call(command: str, *, copilot: bool = False, env: dict[str, str] | None = None) -> str:
        payload = bash_payload(command, session, repo, copilot=copilot)
        return hook("guard_command.py", payload, outside=copilot, env=env).decision

    return call


@pytest.fixture
def check(repo: Path) -> Callable[..., Answer]:
    """`check("scripts/check_literals.py", "main...HEAD")` runs a baseline script in the repo."""

    def call(script: str, *args: str) -> Answer:
        result = run_script(ROOT / script, None, repo, list(args))
        verdict = "passed" if result.returncode == 0 else "refused"
        return Answer(verdict, result.stdout, result.returncode)

    return call
