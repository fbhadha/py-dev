"""stop_gate.py and session_start.py.

The turn cannot end with red ruff on the files the session changed, and the gate
never blocks twice. Session start prints JSON both harnesses read, naming the
guard, the branch from the payload's cwd and the plugin's scripts folder.
"""

import json
from pathlib import Path

import pytest


def test_stop_gate_passes_on_a_clean_tree(hook) -> None:
    assert hook("stop_gate.py", {"session_id": "s"}).decision == "allow"


@pytest.fixture
def red_ruff(repo: Path) -> Path:
    (repo / "pyproject.toml").write_text(
        '[project]\nname = "x"\n[tool.ruff]\nline-length = 100\n', encoding="utf-8"
    )
    (repo / "src" / "y.py").write_text("import os\n", encoding="utf-8")
    return repo


@pytest.mark.usefixtures("red_ruff")
def test_stop_gate_blocks_red_ruff(hook) -> None:
    assert hook("stop_gate.py", {"session_id": "s"}).decision == "block"


def test_stop_gate_blocks_red_ruff_when_started_outside_the_repo(hook, red_ruff: Path) -> None:
    payload = {"sessionId": "s", "cwd": str(red_ruff)}
    assert hook("stop_gate.py", payload, outside=True).decision == "block"


@pytest.mark.usefixtures("red_ruff")
def test_stop_gate_never_blocks_twice(hook) -> None:
    payload = {"session_id": "s", "stop_hook_active": True}
    assert hook("stop_gate.py", payload).decision == "allow"


@pytest.fixture
def session_start(hook, repo: Path) -> dict:
    out = hook("session_start.py", {"sessionId": "s", "cwd": str(repo)}, outside=True).stdout
    return json.loads(out) if out.strip() else {}


def test_session_start_is_json_copilot_reads(session_start: dict) -> None:
    assert session_start.get("additionalContext")


def test_session_start_is_json_claude_code_reads(session_start: dict) -> None:
    nested = (session_start.get("hookSpecificOutput") or {}).get("additionalContext")
    assert nested == session_start["additionalContext"]


def test_session_start_names_the_guard(session_start: dict) -> None:
    assert "python-dev guards active" in session_start["additionalContext"]


def test_session_start_names_the_branch_from_the_payload_cwd(session_start: dict) -> None:
    assert "Branch: main" in session_start["additionalContext"]


def test_session_start_names_another_session(hook, repo: Path) -> None:
    notes = repo / ".git" / "python-dev-sessions"
    notes.mkdir()
    (notes / str(os.getppid())).touch()
    out = hook("session_start.py", {"sessionId": "s", "cwd": str(repo)}, outside=True).stdout
    assert "Another session is live in this folder" in json.loads(out)["additionalContext"]


def test_session_start_alone_names_no_session(session_start: dict) -> None:
    assert "Another session is live in this folder" not in session_start["additionalContext"]


def test_session_start_names_the_plugin_scripts(session_start: dict, root: Path) -> None:
    assert f"Plugin scripts: {root / 'scripts'}" in session_start["additionalContext"]
