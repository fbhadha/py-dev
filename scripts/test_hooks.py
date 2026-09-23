#!/usr/bin/env python3
"""Run the hook scripts and the baseline's test-diff check against a scratch git repo.

CI runs this. It builds a throwaway repo on `main`, drives the command guard with
payloads in both harnesses' shapes on main, on a branch and on a shaping branch,
and asserts the answer: ask, deny or allow. Copilot-shaped payloads run from a
folder outside the repo with the repo in the payload's `cwd`, because that is how
Copilot CLI starts plugin hooks. Then the edit guard (no ticket, no code), the stop
gate, the session-start line, the hook manifests failing open when the plugin root
is not expanded, and check_test_diff.py on a weakened and a clean test change.

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
ADR_SYNC = ROOT / "skills" / "py-baseline" / "templates" / "adr_sync.py"
ADR_TEMPLATE = ROOT / "skills" / "py-baseline" / "templates" / "adr-template.md"
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
    git(repo, "remote", "add", "origin", "git@github.com:me/proj.git")
    git(repo, "remote", "add", "fork", "https://github.com/other/proj.git")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "init")
    return repo


def bash(command: str, session: str, repo: Path, *, copilot: bool = False) -> dict:
    if copilot:  # the shape Copilot CLI 1.0.88 sends, captured from a live session
        return {
            "sessionId": session,
            "timestamp": 0,
            "cwd": str(repo),
            "toolName": "bash",
            "toolArgs": {"command": command, "description": "run"},
        }
    return {"session_id": session, "tool_name": "Bash", "tool_input": {"command": command}}


def guard(command: str, repo: Path, session: str, *, copilot: bool = False, env=None) -> str:
    # Copilot CLI starts plugin hooks in the plugin's folder; only the payload names the repo
    where = repo.parent if copilot else repo
    return decision_of(run(GUARD, bash(command, session, repo, copilot=copilot), where, env=env))


def check_guard(repo: Path) -> None:
    s = f"t-{uuid.uuid4()}"
    # on main: anything that lands on main asks
    expect("main: commit asks", guard("git commit -m 'x'", repo, s), "ask")
    expect("main: merge asks", guard("git merge ticket/1", repo, s), "ask")
    expect("main: bare push asks", guard("git push", repo, s), "ask")
    expect("main: push origin main asks", guard("git push origin main", repo, s), "ask")
    expect("main: copilot payload asks too", guard("git commit -m x", repo, s, copilot=True), "ask")
    string_args = {
        "cwd": str(repo),
        "toolName": "shell",
        "toolArgs": json.dumps({"command": "git commit -m x"}),
    }
    expect(
        "main: copilot payload with string toolArgs asks",
        decision_of(run(GUARD, string_args, repo.parent)),
        "ask",
    )
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
    # sending content outside this project's repo asks; reads and own-repo writes do not
    expect(
        "other repo: gh issue create -R asks",
        guard("gh issue create -R fbhadha/py-dev --title x --body-file d.md", repo, s),
        "ask",
    )
    expect(
        "other repo: gh api POST asks",
        guard("gh api -X POST repos/fbhadha/py-dev/issues -f title=x", repo, s),
        "ask",
    )
    expect("other repo: gist asks", guard("gh gist create notes.md", repo, s), "ask")
    expect("other repo: push to a fork asks", guard("git push fork ticket/1", repo, s), "ask")
    expect(
        "other repo: push to a URL asks",
        guard("git push https://github.com/other/x.git ticket/1", repo, s),
        "ask",
    )
    expect(
        "other repo: gh issue view -R passes",
        guard("gh issue view -R fbhadha/py-dev 12", repo, s),
        "allow",
    )
    expect(
        "own repo: gh issue create passes",
        guard("gh issue create --title x --body y", repo, s),
        "allow",
    )
    expect(
        "own repo: gh issue create -R me/proj passes",
        guard("gh issue create -R me/proj --title x", repo, s),
        "allow",
    )
    expect(
        "own repo: gh api GET passes",
        guard("gh api repos/fbhadha/py-dev/releases/latest", repo, s),
        "allow",
    )
    # the never list, on any branch
    expect("force-push denied", guard("git push --force origin ticket/1", repo, s), "deny")
    expect("rebase denied", guard("git rebase main", repo, s), "deny")
    expect("amend denied", guard("git commit --amend --no-edit", repo, s), "deny")
    expect("no-verify denied", guard("git commit -n -m x", repo, s), "deny")
    expect("hard reset denied", guard("git reset --hard HEAD~1", repo, s), "deny")
    expect(
        "guard off inline denied",
        guard("PYTHON_DEV_GUARD=off git merge --no-ff ticket/1", repo, s),
        "deny",
    )
    expect("pre-commit uninstall denied", guard("uv run pre-commit uninstall", repo, s), "deny")
    expect(
        "edit tool payload ignored by the command guard",
        decision_of(run(GUARD, {"tool_name": "Edit", "tool_input": {"file_path": "x"}}, repo)),
        "allow",
    )
    expect("garbage payload fails open", decision_of(run(GUARD, {"tool_input": 5}, repo)), "allow")
    git(repo, "switch", "-q", "main")


def check_shaping(repo: Path) -> None:
    """On a shaping branch a commit that carries src/ or tests/ asks; docs pass; prototypes are free."""
    s = f"t-{uuid.uuid4()}"
    git(repo, "switch", "-q", "-c", "shaping/idea")
    (repo / "docs").mkdir(exist_ok=True)
    (repo / "docs" / "note.md").write_text("# note\n", encoding="utf-8")
    git(repo, "add", "docs/note.md")
    expect("shaping: commit of docs passes", guard("git commit -m 'term: note'", repo, s), "allow")
    (repo / "src" / "x.py").write_text("X = 3\n", encoding="utf-8")
    expect(
        "shaping: staged docs only, unstaged src, plain commit passes",
        guard("git commit -m 'term: note'", repo, s),
        "allow",
    )
    expect("shaping: commit -a with src asks", guard("git commit -am 'build it'", repo, s), "ask")
    git(repo, "add", "src/x.py")
    expect("shaping: staged src asks", guard("git commit -m 'build it'", repo, s), "ask")
    expect(
        "shaping: copilot payload asks too", guard("git commit -m x", repo, s, copilot=True), "ask"
    )
    git(repo, "reset", "-q", "--", "src/x.py", "docs/note.md")
    git(repo, "checkout", "--", "src/x.py")
    (repo / "docs" / "note.md").unlink()
    git(repo, "switch", "-q", "-c", "prototype/idea")
    (repo / "src" / "x.py").write_text("X = 3\n", encoding="utf-8")
    git(repo, "add", "src/x.py")
    expect(
        "prototype branch: commit with src passes", guard("git commit -m 'proto'", repo, s), "allow"
    )
    git(repo, "reset", "-q", "--", "src/x.py")
    git(repo, "checkout", "--", "src/x.py")
    git(repo, "switch", "-q", "main")
    git(repo, "branch", "-q", "-D", "shaping/idea", "prototype/idea")


def check_stop_and_start(repo: Path) -> None:
    stop = HOOKS / "stop_gate.py"
    expect(
        "stop gate passes on a clean tree",
        decision_of(run(stop, {"session_id": "s"}, repo)),
        "allow",
    )
    if shutil.which("ruff"):
        (repo / "pyproject.toml").write_text(
            '[project]\nname = "x"\n[tool.ruff]\nline-length = 100\n', encoding="utf-8"
        )
        (repo / "src" / "y.py").write_text("import os\n", encoding="utf-8")
        expect(
            "stop gate blocks red ruff", decision_of(run(stop, {"session_id": "s"}, repo)), "block"
        )
        expect(
            "stop gate blocks red ruff when started outside the repo (Copilot CLI)",
            decision_of(run(stop, {"sessionId": "s", "cwd": str(repo)}, repo.parent)),
            "block",
        )
        expect(
            "stop gate never blocks twice",
            decision_of(run(stop, {"session_id": "s", "stop_hook_active": True}, repo)),
            "allow",
        )
        (repo / "src" / "y.py").unlink()
        git(repo, "checkout", "--", "pyproject.toml")
    else:
        print("skip stop gate ruff check: ruff not on PATH")
    out = run(HOOKS / "session_start.py", {"sessionId": "s", "cwd": str(repo)}, repo.parent).stdout
    data = json.loads(out) if out.strip() else {}
    text = str(data.get("additionalContext", ""))
    nested = (data.get("hookSpecificOutput") or {}).get("additionalContext")
    expect("session start is JSON Copilot reads", "json" if text else "not json", "json")
    expect(
        "session start is JSON Claude Code reads", "json" if nested == text else "missing", "json"
    )
    expect(
        "session start names the guard",
        "named" if "python-dev guards active" in text else "silent",
        "named",
    )
    expect(
        "session start names the branch from the payload's cwd",
        "named" if "Branch: main" in text else "silent",
        "named",
    )
    expect(
        "session start names the plugin scripts",
        "named" if f"Plugin scripts: {ROOT / 'scripts'}" in text else "silent",
        "named",
    )


def edit(tool: str, args: dict, repo: Path, *, copilot: bool = False, env=None) -> str:
    if copilot:
        payload = {"sessionId": "s", "cwd": str(repo), "toolName": tool, "toolArgs": args}
        return decision_of(run(GUARD, payload, repo.parent, env=env))
    return decision_of(run(GUARD, {"tool_name": tool, "tool_input": args}, repo, env=env))


def check_edit_guard(repo: Path) -> None:
    """No ticket, no code: product edits off a build branch ask, in a python-dev repo only."""
    src = str(repo / "src" / "x.py")
    expect(
        "edit: a repo without mode.md is never asked about",
        edit("Edit", {"file_path": src}, repo),
        "allow",
    )
    mode = repo / "docs" / "agents" / "mode.md"
    mode.parent.mkdir(parents=True, exist_ok=True)
    mode.write_text("mode: guide\n", encoding="utf-8")
    expect("edit: src on main asks", edit("Edit", {"file_path": src}, repo), "ask")
    expect(
        "edit: a relative tests path on main asks",
        edit("Write", {"file_path": "tests/test_new.py"}, repo),
        "ask",
    )
    expect(
        "edit: docs on main pass", edit("Edit", {"file_path": "docs/agents/x.md"}, repo), "allow"
    )
    expect(
        "edit: prototypes on main pass",
        edit("Write", {"file_path": "prototypes/try.py"}, repo),
        "allow",
    )
    expect(
        "edit: a file outside the repo passes",
        edit("Write", {"file_path": str(repo.parent / "elsewhere.py")}, repo),
        "allow",
    )
    expect(
        "edit: copilot create on main asks",
        edit("create", {"path": src, "file_text": "X = 2\n"}, repo, copilot=True),
        "ask",
    )
    patch = "*** Begin Patch\n*** Update File: src/x.py\n@@\n-X = 1\n+X = 2\n*** End Patch\n"
    expect(
        "edit: copilot apply_patch on main asks",
        edit("apply_patch", {"input": patch}, repo, copilot=True),
        "ask",
    )
    expect(
        "edit: str_replace_editor view passes",
        edit("str_replace_editor", {"command": "view", "path": src}, repo, copilot=True),
        "allow",
    )
    expect(
        "edit: guard off passes",
        edit("Edit", {"file_path": src}, repo, env={"PYTHON_DEV_GUARD": "off"}),
        "allow",
    )
    git(repo, "switch", "-q", "-c", "ticket/7-adapter")
    expect("edit: src on a ticket branch passes", edit("Edit", {"file_path": src}, repo), "allow")
    expect(
        "edit: copilot edit on a ticket branch passes",
        edit("edit", {"path": src}, repo, copilot=True),
        "allow",
    )
    git(repo, "switch", "-q", "main")
    git(repo, "switch", "-q", "-c", "shaping/idea2")
    said = run(GUARD, {"tool_name": "Edit", "tool_input": {"file_path": src}}, repo).stdout
    expect(
        "edit: src on a shaping branch asks with the shaping reason",
        "shaping reason" if "Shaping decides" in said else said[:80],
        "shaping reason",
    )
    git(repo, "switch", "-q", "main")
    git(repo, "branch", "-q", "-D", "ticket/7-adapter", "shaping/idea2")
    shutil.rmtree(repo / "docs")


def check_manifests_fail_open(repo: Path) -> None:
    """A hook whose plugin root was not expanded exits 0 with no decision, never an error.

    Copilot CLI and VS Code deny every tool call when a pre-tool command hook exits
    non-zero, and VS Code expands no plugin root for an Agent Plugins manifest.
    """
    if not shutil.which("bash"):
        print("skip manifest fail-open check: bash not on PATH")
        return
    copilot = json.loads((ROOT / "com.github.copilot" / "hooks" / "hooks.json").read_text())
    claude = json.loads((ROOT / "hooks" / "hooks.json").read_text())
    cases = (
        ("copilot", copilot["hooks"]["preToolUse"][0]["bash"], "PLUGIN_ROOT"),
        ("claude", claude["hooks"]["PreToolUse"][0]["hooks"][0]["command"], "CLAUDE_PLUGIN_ROOT"),
    )
    payload = json.dumps(bash("git commit -m x", "s", repo, copilot=True))
    base = {k: v for k, v in os.environ.items() if k not in ("PLUGIN_ROOT", "CLAUDE_PLUGIN_ROOT")}
    for name, command, var in cases:
        for root, want in (("", "0:allow"), (str(ROOT), "0:ask")):
            env = {**base, var: root} if root else base
            result = subprocess.run(
                ["bash", "-c", command],
                input=payload,
                capture_output=True,
                text=True,
                cwd=repo.parent,
                env=env,
                check=False,
            )
            label = "expanded" if root else "unexpanded"
            expect(
                f"manifest {name}: {label} plugin root",
                f"{result.returncode}:{decision_of(result)}",
                want,
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


def check_adr_format(tmp: Path) -> None:
    """adr_sync's shape check: the template copy is skipped, the short form is reported."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("adr_sync", ADR_SYNC)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    readme = tmp / "README.md"
    readme.write_text(ADR_TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")
    expect(
        "adr_sync skips the template copy",
        "skipped" if module.is_template(readme, readme.read_text()) else "bound",
        "skipped",
    )
    short = tmp / "0001-short.md"
    short.write_text("# Use one queue\n\nWe picked one queue because it is simpler.\n")
    expect(
        "adr_sync reports the short form",
        "reported" if module.format_problem(short, short.read_text()) else "silent",
        "reported",
    )
    full = tmp / "0002-full.md"
    full.write_text("# Use one queue\n\n## Status\n\nAccepted\n\n## Scope\n\n- src/q/\n")
    expect(
        "adr_sync accepts the governing form",
        "silent" if module.format_problem(full, full.read_text()) is None else "reported",
        "silent",
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        repo = make_repo(Path(tmp))
        check_guard(repo)
        check_shaping(repo)
        check_edit_guard(repo)
        check_manifests_fail_open(repo)
        check_stop_and_start(repo)
        check_test_diff(repo)
        check_adr_format(Path(tmp))
    if FAILURES:
        print("\nHOOK TESTS FAILED:")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    print("\nall hook checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
