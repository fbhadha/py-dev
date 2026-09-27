"""guard_eval.py: the eval author reads and writes under tests/evals/ only; nobody else is."""

from pathlib import Path

import pytest

EVAL_AGENT = "python-dev:py-eval"


def eval_tool(hook, tool: str, args: dict, agent: str = EVAL_AGENT) -> str:
    payload = {"tool_name": tool, "tool_input": args, "agent_type": agent}
    return hook("guard_eval.py", payload).decision


def test_src_denied(hook, repo: Path) -> None:
    assert eval_tool(hook, "Read", {"file_path": str(repo / "src" / "x.py")}) == "deny"


def test_evals_allowed(hook, repo: Path) -> None:
    targets = str(
        repo / "tests" / "evals" / "orders" / "targets-12.md"
    )  # literal-ok: a path in the scratch repo
    assert eval_tool(hook, "Read", {"file_path": targets}) == "allow"


def test_write_under_evals_passes(hook, repo: Path) -> None:
    case = str(repo / "tests" / "evals" / "orders" / "12.test.json")
    assert eval_tool(hook, "Write", {"file_path": case}) == "allow"


def test_write_elsewhere_denied(hook, repo: Path) -> None:
    assert eval_tool(hook, "Write", {"file_path": str(repo / "tests" / "test_x.py")}) == "deny"


def test_relative_evals_path_passes(hook) -> None:
    path = "tests/evals/orders/targets-12.md"  # literal-ok: a path in the scratch repo
    assert eval_tool(hook, "Read", {"file_path": path}) == "allow"


@pytest.mark.parametrize(
    ("tool", "args"),
    [
        ("Grep", {"pattern": "x", "path": "{repo}"}),
        ("Bash", {"command": "cat src/x.py"}),
    ],
    ids=["search denied", "shell denied"],
)
def test_search_and_shell_denied(hook, repo: Path, tool: str, args: dict) -> None:
    args = {k: v.replace("{repo}", str(repo)) for k, v in args.items()}
    assert eval_tool(hook, tool, args) == "deny"


def test_outside_the_repo_denied(hook, repo: Path) -> None:
    assert eval_tool(hook, "Read", {"file_path": str(repo.parent / "elsewhere.md")}) == "deny"


def test_main_session_passes(hook, repo: Path) -> None:
    payload = {"tool_name": "Read", "tool_input": {"file_path": str(repo / "src" / "x.py")}}
    assert hook("guard_eval.py", payload).decision == "allow"


def test_another_agent_passes(hook, repo: Path) -> None:
    src = str(repo / "src" / "x.py")
    assert eval_tool(hook, "Read", {"file_path": src}, agent="python-dev:py-reviewer") == "allow"


def test_garbage_payload_fails_open(hook) -> None:
    assert hook("guard_eval.py", {"agent_type": "py-eval", "tool_input": 5}).decision == "allow"
