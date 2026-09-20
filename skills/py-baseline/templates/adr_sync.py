#!/usr/bin/env python3
"""Bind every accepted ADR in docs/adr/ to the paths it governs, in Repowise.

An ADR file is the only way a decision is written in this repo. Repowise reads
the file when the repo is indexed, but it binds a decision to files only through
an acceptance with a scope. This script closes that gap: it re-indexes (unless
--no-index), then for each ADR whose Status is Accepted and whose "## Scope"
section lists paths, it accepts the matching Repowise decision with those paths.

Usage:
    uv run python scripts/adr_sync.py            # re-index, then bind
    uv run python scripts/adr_sync.py --no-index # bind against the current index (CI)

Exit codes: 0 all accepted ADRs are bound; 1 an ADR could not be bound (no Scope
section, no matching decision, or Repowise refused); 2 repowise is not installed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ADR_DIR = Path("docs/adr")
HEADING = re.compile(r"^##\s+(.+?)\s*$")


def sections(text: str) -> dict[str, str]:
    """Split a Markdown body into {lower-cased '## heading': body}."""
    out: dict[str, list[str]] = {}
    current = ""
    for line in text.splitlines():
        m = HEADING.match(line)
        if m:
            current = m.group(1).strip().lower()
            out[current] = []
        elif current:
            out[current].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def title_of(text: str) -> str:
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def scope_paths(body: str) -> list[str]:
    return [
        line.lstrip("-* ").strip().strip("`")
        for line in body.splitlines()
        if line.strip().startswith(("-", "*"))
    ]


def repowise(*args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "DO_NOT_TRACK": "1", "REPOWISE_SKIP_EDITOR_SETUP": "1"}
    return subprocess.run(["repowise", *args], capture_output=True, text=True, check=False, env=env)


def bind(adr: Path, by_title: dict[str, dict[str, str]]) -> str | None:
    """Bind one ADR. Returns an error message, or None when bound or not accepted."""
    text = adr.read_text(encoding="utf-8")
    parts = sections(text)
    status = parts.get("status", "").split()
    if not status or status[0].lower() not in ("accepted", "approved"):
        return None
    paths = scope_paths(parts.get("scope", ""))
    if not paths:
        return f"{adr}: accepted but has no '## Scope' paths; add the paths it governs"
    title = title_of(text)
    decision = by_title.get(title.lower())
    if decision is None:
        return f"{adr}: no Repowise decision titled {title!r}; run without --no-index"
    cmd = ["decision", "confirm", decision["id"], "--reason", f"Accepted in {adr}"]
    cmd += ["--evidence", str(adr)]
    for path in paths:
        cmd += ["--scope", path]
    confirmed = repowise(*cmd)
    if confirmed.returncode != 0:
        return f"{adr}: repowise refused: {confirmed.stdout.strip()} {confirmed.stderr.strip()}"
    print(f"{adr}: bound to {', '.join(paths)}")
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--no-index", action="store_true", help="skip `repowise init`; use the current index"
    )
    args = parser.parse_args()

    if shutil.which("repowise") is None:
        print("repowise is not installed: uv add --group dev repowise", file=sys.stderr)
        return 2
    if not ADR_DIR.is_dir():
        print(f"{ADR_DIR}: no ADRs; nothing to bind")
        return 0

    if not args.no_index:
        result = repowise("init", "--no-prose", "--no-editor-setup", "--no-save-key", "-y", ".")
        if result.returncode != 0:
            print(result.stderr[-2000:], file=sys.stderr)
            return 1

    listed = repowise("decision", "list", "--format", "json")
    if listed.returncode != 0:
        print(listed.stderr[-2000:], file=sys.stderr)
        return 1
    decisions = json.loads(listed.stdout).get("decisions", [])
    by_title = {d["title"].strip().lower(): d for d in decisions}

    errors = [bind(adr, by_title) for adr in sorted(ADR_DIR.glob("*.md"))]
    for error in filter(None, errors):
        print(error)
    return 1 if any(errors) else 0


if __name__ == "__main__":
    sys.exit(main())
