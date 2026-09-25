#!/usr/bin/env python3
"""Fail when a change weakens the tests: a deleted test, an added skip, fewer assertions.

Runs in CI on the pull request range and locally before review. It reads the diff
of `tests/` only. Three findings, each fatal:

  deleted test      a `def test_*` removed and not re-added under the same name
  added skip        a `skip`, `xfail` or `pytest.skip(` line added
  fewer assertions  a modified test file lost more `assert` lines than it gained

An override is a line `test-override: <reason>` in a commit message inside the
range, written in the user's words and recorded in the ticket. It prints the
reason and passes.

Usage: python scripts/check_test_diff.py [<range>]   (default: origin/main...HEAD)
"""

from __future__ import annotations

import re
import subprocess
import sys

DEFAULT_RANGE = "origin/main...HEAD"
TEST_DEF = re.compile(r"^[-+]\s*(?:async\s+)?def\s+(test_\w+)")
SKIP = re.compile(r"^\+.*\b(pytest\.mark\.(skip|xfail)|pytest\.(skip|xfail)\(|unittest\.skip)")
ASSERT = re.compile(r"^[-+]\s*assert\b")
OVERRIDE = re.compile(r"^test-override:\s*(.+)$", re.MULTILINE)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False).stdout


def override(rng: str) -> str | None:
    match = OVERRIDE.search(git("log", "--format=%B", rng))
    return match.group(1).strip() if match else None


def changed_test_files(rng: str) -> list[str]:
    names = git("diff", "--name-only", rng, "--", "tests/").split()
    return [name for name in names if name.endswith(".py")]


def findings_for(path: str, rng: str) -> list[str]:
    removed_defs: set[str] = set()
    added_defs: set[str] = set()
    removed_asserts = added_asserts = 0
    found: list[str] = []
    for line in git("diff", rng, "--", path).splitlines():
        if line.startswith(("---", "+++")):
            continue
        definition = TEST_DEF.match(line)
        if definition:
            (added_defs if line[0] == "+" else removed_defs).add(definition.group(1))
        if SKIP.match(line):
            found.append(f"{path}: added skip: {line[1:].strip()}")
        if ASSERT.match(line):
            added_asserts += line[0] == "+"
            removed_asserts += line[0] == "-"
    found.extend(f"{path}: deleted test {name}" for name in sorted(removed_defs - added_defs))
    if removed_asserts > added_asserts:
        found.append(f"{path}: fewer assertions ({removed_asserts} removed, {added_asserts} added)")
    return found


def main(argv: list[str]) -> int:
    rng = argv[1] if len(argv) > 1 else DEFAULT_RANGE
    reason = override(rng)
    if reason:
        print(f"test-diff: override recorded in a commit message: {reason}")
        return 0
    findings = [f for path in changed_test_files(rng) for f in findings_for(path, rng)]
    if not findings:
        print(f"test-diff: nothing weakened in tests/ over {rng}")
        return 0
    print(f"test-diff: the change weakens the tests ({rng}):")
    for finding in findings:
        print(f"  {finding}")
    print(
        "A test is read-only from red to green. If one of these is right, the user says so "
        "in their own words: put `test-override: <their reason>` in the commit message and "
        "in the ticket."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
