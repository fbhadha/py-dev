#!/usr/bin/env python3
"""Fail when a change to an agent's package ships no fresh eval report.

The eval itself runs off CI (a live model, a key, a cost): `py-build` runs it before the
review and commits the report under `tests/evals/<agent>/reports/`. This check is what
makes "no report, no merge" hold on the server, for every harness and for the default
agent: a pull request that touches `src/<package>/entrypoints/agents/<agent>/` must also
touch a report for that agent, and the report's `commit:` line must name an ancestor of
HEAD after which that package did not change. A repository with no agent package has
nothing to check.

An override is a line `eval-override: <reason>` in a commit message inside the range,
written in the user's words and recorded in the ticket. It prints the reason and passes.

Usage: python scripts/check_eval_report.py [<range>]   (default: origin/main...HEAD)
"""

from __future__ import annotations

import re
import subprocess
import sys

DEFAULT_RANGE = "origin/main...HEAD"
AGENT = re.compile(r"^(src/[^/]+/entrypoints/agents/([^/]+))/")
REPORT = re.compile(r"^tests/evals/([^/]+)/reports/[^/]+\.md$")
COMMIT_LINE = re.compile(r"^commit:\s*([0-9a-fA-F]{7,40})\s*$", re.MULTILINE)
OVERRIDE = re.compile(r"^eval-override:\s*(.+)$", re.MULTILINE)


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False)


def override(rng: str) -> str | None:
    match = OVERRIDE.search(git("log", "--format=%B", rng).stdout)
    return match.group(1).strip() if match else None


def changed_files(rng: str) -> list[str]:
    return git("diff", "--name-only", rng).stdout.split()


def changed_agents(files: list[str]) -> dict[str, str]:
    """Agent name -> package path, for every agent package the range touches."""
    found: dict[str, str] = {}
    for path in files:
        match = AGENT.match(path)
        if match:
            found[match.group(2)] = match.group(1)
    return found


def changed_reports(files: list[str]) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for path in files:
        match = REPORT.match(path)
        if match:
            found.setdefault(match.group(1), []).append(path)
    return found


def report_commit(path: str) -> str | None:
    match = COMMIT_LINE.search(git("show", f"HEAD:{path}").stdout)
    return match.group(1) if match else None


def is_fresh(commit: str, package: str) -> str | None:
    """None when the eval ran on the agent as it is now; else why not."""
    if git("cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
        return f"`{commit}` is not a commit in this repository"
    if git("merge-base", "--is-ancestor", commit, "HEAD").returncode != 0:
        return f"`{commit}` is not an ancestor of HEAD"
    if git("diff", "--quiet", commit, "HEAD", "--", package).returncode != 0:
        return f"`{package}` changed after `{commit}`, so the eval ran on older code"
    return None


def findings_for(agent: str, package: str, reports: dict[str, list[str]]) -> list[str]:
    paths = reports.get(agent)
    if not paths:
        return [
            f"{package}: changed, and no report under tests/evals/{agent}/reports/ changed with it"
        ]
    found: list[str] = []
    for path in sorted(paths):
        commit = report_commit(path)
        if commit is None:
            found.append(
                f"{path}: no `commit: <hash>` line, so nothing says which code the eval ran on"
            )
            continue
        why = is_fresh(commit, package)
        if why:
            found.append(f"{path}: {why}")
    return found


def main(argv: list[str]) -> int:
    rng = argv[1] if len(argv) > 1 else DEFAULT_RANGE
    reason = override(rng)
    if reason:
        print(f"eval-report: override recorded in a commit message: {reason}")
        return 0
    files = changed_files(rng)
    agents = changed_agents(files)
    if not agents:
        print(f"eval-report: no agent package changed over {rng}; nothing to check")
        return 0
    reports = changed_reports(files)
    findings = [
        f
        for agent, package in sorted(agents.items())
        for f in findings_for(agent, package, reports)
    ]
    if not findings:
        print(f"eval-report: every changed agent has a fresh report over {rng}")
        return 0
    print(f"eval-report: an agent changed without the outside user's report ({rng}):")
    for finding in findings:
        print(f"  {finding}")
    print(
        "Run the eval on the agent as it is now (py-build's eval step) and commit the report "
        "with a `commit:` line naming that HEAD. If the user accepts the change untested, put "
        "`eval-override: <their reason>` in the commit message and in the ticket."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
