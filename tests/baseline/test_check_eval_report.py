"""check_eval_report.py: an agent package changed without a fresh eval report is refused.

Nothing else is. Drives the template: this repo has no agents and no copy.
"""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

SCRIPT = "skills/py-baseline/templates/check_eval_report.py"
RANGE = "main...HEAD"
PACKAGE = "src/pkg/entrypoints/agents/orders"


@pytest.fixture
def agent(repo: Path, git) -> Path:
    """The orders agent, committed on main."""
    agent = repo / PACKAGE / "agent.py"
    agent.parent.mkdir(parents=True)
    agent.write_text("ROOT = 1\n", encoding="utf-8")
    git("add", "src/pkg")
    git("commit", "-q", "-m", "the orders agent")
    return agent


@pytest.fixture
def head(repo: Path) -> Callable[[], str]:
    def call() -> str:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()

    return call


@pytest.fixture
def report(repo: Path, git) -> Callable[[str, str], None]:
    """`report("e1", commit)`: a report for the orders agent naming that commit, committed."""
    reports = repo / "tests" / "evals" / "orders" / "reports"

    def call(name: str, commit: str) -> None:
        reports.mkdir(parents=True, exist_ok=True)
        (reports / f"{name}.md").write_text(
            f"# Eval report: {name}\n\nagent: {PACKAGE}\ncommit: {commit}\n"
            "command: uv run pytest -m eval tests/evals/orders\n\n"
            "| target-1 | VAGUE | pass | 1.0 |\n",
            encoding="utf-8",
        )
        git("add", "tests/evals")
        git("commit", "-q", "-m", f"report {name}")

    return call


def change_agent(agent: Path, git, value: int) -> None:
    agent.write_text(f"ROOT = {value}\n", encoding="utf-8")
    git("commit", "-q", "-am", "change the agent")


def test_no_agents_passes(check, repo: Path, git) -> None:
    git("switch", "-q", "-c", "ticket/e0")
    (repo / "src" / "x.py").write_text("X = 5\n", encoding="utf-8")
    git("commit", "-q", "-am", "no agent here")
    assert check(SCRIPT, RANGE).decision == "passed"


def test_changed_agent_without_a_report_is_refused_and_named(check, agent: Path, git) -> None:
    git("switch", "-q", "-c", "ticket/e1")
    change_agent(agent, git, 2)
    said = check(SCRIPT, RANGE)
    assert said.decision == "refused"
    assert "no report" in said.stdout


def test_fresh_report_passes(check, agent: Path, git, head, report) -> None:
    git("switch", "-q", "-c", "ticket/e1")
    change_agent(agent, git, 2)
    report("e1", head())
    assert check(SCRIPT, RANGE).decision == "passed"


def test_stale_report_refused_and_named(check, agent: Path, git, head, report) -> None:
    git("switch", "-q", "-c", "ticket/e1")
    change_agent(agent, git, 2)
    report("e1", head())
    change_agent(agent, git, 3)
    said = check(SCRIPT, RANGE)
    assert said.decision == "refused"
    assert "changed after" in said.stdout


def test_bad_commit_line_refused_and_named(check, agent: Path, git, report) -> None:
    git("switch", "-q", "-c", "ticket/e2")
    change_agent(agent, git, 4)
    report("e2", "nope")
    said = check(SCRIPT, RANGE)
    assert said.decision == "refused"
    assert "commit: <hash>" in said.stdout


def test_foreign_commit_refused_and_named(check, agent: Path, git, head, report) -> None:
    git("switch", "-q", "-c", "other/branch")
    git("commit", "-q", "--allow-empty", "-m", "elsewhere")
    foreign = head()
    git("switch", "-q", "main")
    git("switch", "-q", "-c", "ticket/e3")
    change_agent(agent, git, 5)
    report("e3", foreign)
    said = check(SCRIPT, RANGE)
    assert said.decision == "refused"
    assert "not an ancestor" in said.stdout


def test_two_agents_one_report_refused_and_named(check, agent: Path, git, head, report) -> None:
    git("switch", "-q", "-c", "ticket/e4")
    billing = agent.parent.parent / "billing" / "agent.py"  # agents/billing beside agents/orders
    billing.parent.mkdir(parents=True)
    billing.write_text("ROOT = 1\n", encoding="utf-8")
    agent.write_text("ROOT = 6\n", encoding="utf-8")
    git("add", "src/pkg")
    git("commit", "-q", "-m", "two agents")
    report("e4", head())
    said = check(SCRIPT, RANGE)
    assert said.decision == "refused"
    assert "agents/billing" in said.stdout


def test_override_passes(check, agent: Path, git) -> None:
    git("switch", "-q", "-c", "ticket/e5")
    agent.write_text("ROOT = 7\n", encoding="utf-8")
    reason = "task-5\n\neval-override: the user says the wording change cannot reach a user"
    git("commit", "-q", "-am", reason)
    assert check(SCRIPT, RANGE).decision == "passed"
