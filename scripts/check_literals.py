#!/usr/bin/env python3
"""Fail when a change types a literal from memory.

A path that names nothing in the tree, or an environment key that is not in `.env.example`:
both are the tells of a literal remembered from an earlier read or from the conversation
instead of copied from the file (python-dev's rule: every literal comes from a file open in
this slice). Signatures are mypy's; expected values have their source in the ticket's plan;
the rest is the reviewer's. Runs in CI on the pull request range and locally before review,
over the added lines of `.py` files under `src/` and `tests/`.

  path literal   a string with a `/`, a file extension, and a first folder that exists in the
                 tree (so the literal claims to be inside the repo); a finding when the file
                 does not exist and the range does not add it. A runtime path whose first
                 folder is not in the tree is never a finding.
  env key        `os.environ["KEY"]`, `os.environ.get("KEY")`, `os.getenv("KEY")`,
                 `alias="KEY"`, `validation_alias="KEY"`; a finding when `.env.example` exists
                 and does not carry the key. With no `.env.example` keys are not checked, and
                 the output says so.

Skipped: URLs, globs (`*`, `?`), format strings (`{`), and lines carrying `# literal-ok: <reason>`.
An override is a line `literal-override: <reason>` in a commit message inside the range, written
in the user's words and recorded in the ticket. It prints the reason and passes.

Usage: python scripts/check_literals.py [<range>]   (default: origin/main...HEAD)
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

DEFAULT_RANGE = "origin/main...HEAD"
STRING = re.compile(r"""'([^'\n]{2,200})'|"([^"\n]{2,200})\"""")
PATH_SHAPE = re.compile(r"^\.?[\w.-]+(?:/[\w.-]+)+\.[A-Za-z0-9]{1,8}$")
ENV_KEY = re.compile(
    r"""(?:os\.environ(?:\.get)?\s*[\[(]\s*|os\.getenv\s*\(\s*|\b(?:validation_)?alias\s*=\s*)"""
    r"""['"]([A-Z][A-Z0-9_]{2,})['"]"""
)
ENV_LINE = re.compile(r"^\s*#?\s*([A-Z][A-Z0-9_]+)\s*=", re.MULTILINE)
OVERRIDE = re.compile(r"^literal-override:\s*(.+)$", re.MULTILINE)
LITERAL_OK = "# literal-ok:"
ADDED_HEADER = re.compile(r"^\+\+\+ b/(.+)$")
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False).stdout


def override(rng: str) -> str | None:
    match = OVERRIDE.search(git("log", "--format=%B", rng))
    return match.group(1).strip() if match else None


def added_lines(rng: str) -> list[tuple[str, int, str]]:
    """(path, line number, text) for every added line of a .py file under src/ or tests/."""
    found: list[tuple[str, int, str]] = []
    path, number = "", 0
    for line in git("diff", rng, "--", "src/", "tests/").splitlines():
        header = ADDED_HEADER.match(line)
        if header:
            path = header.group(1)
            continue
        hunk = HUNK.match(line)
        if hunk:
            number = int(hunk.group(1))
            continue
        if not path.endswith(".py") or line.startswith("---"):
            continue
        if line.startswith("+"):
            found.append((path, number, line[1:]))
            number += 1
        elif not line.startswith("-"):
            number += 1
    return found


def path_literals(text: str) -> list[str]:
    """String literals shaped like a repo path: a slash, an extension, no URL, glob or format."""
    literals = [a or b for a, b in STRING.findall(text)]
    return [
        lit
        for lit in literals
        if PATH_SHAPE.match(lit) and "://" not in lit and not any(c in lit for c in "*?{")
    ]


def env_keys(text: str) -> list[str]:
    return ENV_KEY.findall(text)


def example_keys() -> set[str] | None:
    example = Path(".env.example")
    if not example.exists():
        return None
    return set(ENV_LINE.findall(example.read_text(encoding="utf-8", errors="replace")))


def path_finding(literal: str, added: set[str]) -> str | None:
    """Why this path literal is a finding, or None: the first folder is real, the file is not."""
    if literal in added or Path(literal).exists():
        return None
    first = literal.split("/", 1)[0]
    if first != "." and not Path(first).is_dir():
        return None  # a runtime path outside the tree: not ours to know
    return f"names no file in the tree (the folder `{first}/` exists)"


def line_findings(
    path: str, number: int, text: str, added: set[str], keys: set[str] | None
) -> list[str]:
    """Every finding on one added line; none when it carries `# literal-ok:`."""
    if LITERAL_OK in text:
        return []
    found: list[str] = []
    for literal in path_literals(text):
        why = path_finding(literal, added)
        if why:
            found.append(f"{path}:{number}: `{literal}` {why}")
    if keys is not None:
        for key in env_keys(text):
            if key not in keys:
                found.append(f"{path}:{number}: `{key}` is not in .env.example")
    return found


def main(argv: list[str]) -> int:
    rng = argv[1] if len(argv) > 1 else DEFAULT_RANGE
    reason = override(rng)
    if reason:
        print(f"literals: override recorded in a commit message: {reason}")
        return 0
    added = set(git("diff", "--name-only", "--diff-filter=A", rng).split())
    keys = example_keys()
    findings = [
        f
        for path, number, text in added_lines(rng)
        for f in line_findings(path, number, text, added, keys)
    ]
    note = "" if keys is not None else " (no .env.example, so keys were not checked)"
    if not findings:
        print(f"literals: nothing typed from memory over {rng}{note}")
        return 0
    print(f"literals: the change types literals that match nothing ({rng}){note}:")
    for finding in findings:
        print(f"  {finding}")
    print(
        "Open the file the literal names and copy it from there. A path that exists only at "
        "runtime takes `# literal-ok: <reason>` on its line; a key goes into .env.example in the "
        "same commit. If the user accepts a literal as it is, put `literal-override: <their "
        "reason>` in the commit message and in the ticket."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
