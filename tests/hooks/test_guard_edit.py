"""guard_command.py on an edit: no ticket, no code, in a python-dev repo only.

An edit to src/, tests/ or any .py outside prototypes/ asks unless the branch is
ticket/, prototype/ or intake/; on a shaping/ branch the reason says shaping decides.
A repo without docs/agents/mode.md was never set up, so it is never asked.
"""

from collections.abc import Callable
from pathlib import Path

import pytest


@pytest.fixture
def edit(hook, repo: Path) -> Callable[..., str]:
    def call(tool: str, args: dict, *, copilot: bool = False, env: dict | None = None) -> str:
        if copilot:
            payload = {"sessionId": "s", "cwd": str(repo), "toolName": tool, "toolArgs": args}
            return hook("guard_command.py", payload, outside=True, env=env).decision
        return hook("guard_command.py", {"tool_name": tool, "tool_input": args}, env=env).decision

    return call


@pytest.fixture
def src(repo: Path) -> str:
    return str(repo / "src" / "x.py")


@pytest.fixture
def guided(repo: Path) -> Path:
    """The repo after intake: docs/agents/mode.md exists."""
    mode = repo / "docs" / "agents" / "mode.md"
    mode.parent.mkdir(parents=True)
    mode.write_text("mode: guide\n", encoding="utf-8")
    return repo


def test_a_repo_without_mode_md_is_never_asked(edit, src: str) -> None:
    assert edit("Edit", {"file_path": src}) == "allow"


@pytest.mark.usefixtures("guided")
def test_src_on_main_asks(edit, src: str) -> None:
    assert edit("Edit", {"file_path": src}) == "ask"


@pytest.mark.usefixtures("guided")
@pytest.mark.parametrize(
    ("tool", "path", "decision"),
    [
        ("Write", "tests/test_new.py", "ask"),
        ("Edit", "docs/agents/x.md", "allow"),
        ("Write", "prototypes/try.py", "allow"),
    ],
    ids=["relative tests path asks", "docs pass", "prototypes pass"],
)
def test_paths_on_main(edit, tool: str, path: str, decision: str) -> None:
    assert edit(tool, {"file_path": path}) == decision


@pytest.mark.usefixtures("guided")
def test_a_file_outside_the_repo_passes(edit, repo: Path) -> None:
    assert edit("Write", {"file_path": str(repo.parent / "elsewhere.py")}) == "allow"


@pytest.mark.usefixtures("guided")
def test_copilot_create_on_main_asks(edit, src: str) -> None:
    assert edit("create", {"path": src, "file_text": "X = 2\n"}, copilot=True) == "ask"


@pytest.mark.usefixtures("guided")
def test_copilot_apply_patch_on_main_asks(edit) -> None:
    patch = "*** Begin Patch\n*** Update File: src/x.py\n@@\n-X = 1\n+X = 2\n*** End Patch\n"
    assert edit("apply_patch", {"input": patch}, copilot=True) == "ask"


@pytest.mark.usefixtures("guided")
def test_str_replace_editor_view_passes(edit, src: str) -> None:
    assert edit("str_replace_editor", {"command": "view", "path": src}, copilot=True) == "allow"


@pytest.mark.usefixtures("guided")
def test_guard_off_passes(edit, src: str) -> None:
    assert edit("Edit", {"file_path": src}, env={"PYTHON_DEV_GUARD": "off"}) == "allow"


@pytest.mark.usefixtures("guided")
def test_src_on_a_ticket_branch_passes(edit, src: str, git) -> None:
    git("switch", "-q", "-c", "ticket/7-adapter")
    assert edit("Edit", {"file_path": src}) == "allow"


@pytest.mark.usefixtures("guided")
def test_copilot_edit_on_a_ticket_branch_passes(edit, src: str, git) -> None:
    git("switch", "-q", "-c", "ticket/7-adapter")
    assert edit("edit", {"path": src}, copilot=True) == "allow"


@pytest.mark.usefixtures("guided")
def test_src_on_a_shaping_branch_asks_with_the_shaping_reason(hook, src: str, git) -> None:
    git("switch", "-q", "-c", "shaping/idea2")
    said = hook("guard_command.py", {"tool_name": "Edit", "tool_input": {"file_path": src}})
    assert said.decision == "ask"
    assert "Shaping decides" in said.stdout
