#!/usr/bin/env python3
"""Check that every upstream skill this plugin calls by name still exists upstream.

Reads upstream.json at the plugin root: for each upstream repository, the pinned commit,
the directory its skills live under, and the skill names we depend on with the
invocation we assume (`model` = we call it through the Skill tool, `user` = only
a person can start it, so the persona gives the user `/<plugin>:<skill>`). Clones
each repository at the pinned commit into a temp dir, finds each SKILL.md by
directory name or frontmatter name, and fails when a skill is missing or its
`disable-model-invocation` flag no longer matches the assumption, or when the
repository's `.claude-plugin/plugin.json` name is not the entry's `plugin` (the
prefix of every line the persona gives the user). A `reference` entry (kind "reference",
with `dir` and `terms`) is a repository of files the persona links to instead
of skills it calls; each `<dir>/<term>.md` must exist at the pin.

With --latest it checks the default branch instead of the pin and reports
drift as warnings, so a scheduled run can say "upstream moved" without failing.

Usage: python scripts/check_upstream_skills.py [--latest]
Exit codes: 0 all present and matching; 1 a skill is missing or its
invocation changed; 2 a clone failed.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def frontmatter(path: Path) -> dict[str, str]:
    m = FRONTMATTER_RE.match(path.read_text(encoding="utf-8", errors="replace"))
    if not m:
        return {}
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip().strip("'\"")
    return out


def clone(repo: str, ref: str, dest: Path) -> bool:
    url = f"https://github.com/{repo}.git"
    init = subprocess.run(["git", "init", "-q", str(dest)], capture_output=True, check=False)
    if init.returncode != 0:
        return False
    fetch = subprocess.run(
        ["git", "-C", str(dest), "fetch", "-q", "--depth", "1", url, ref],
        capture_output=True, text=True, check=False,
    )
    if fetch.returncode != 0:
        print(f"  fetch failed for {repo}@{ref}: {fetch.stderr.strip()[-300:]}", file=sys.stderr)
        return False
    checkout = subprocess.run(
        ["git", "-C", str(dest), "checkout", "-q", "FETCH_HEAD"], capture_output=True, check=False
    )
    return checkout.returncode == 0


def index_skills(skills_dir: Path) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for skill_md in skills_dir.rglob("SKILL.md"):
        if "node_modules" in skill_md.parts:
            continue
        found.setdefault(skill_md.parent.name, skill_md)
        name = frontmatter(skill_md).get("name")
        if name:
            found.setdefault(name, skill_md)
    return found


def check_reference(upstream: dict, dest: Path) -> list[str]:
    """Every term the plugin links to is a file `<dir>/<term>.md` in the reference repo."""
    problems: list[str] = []
    for term in upstream["terms"]:
        path = dest / upstream["dir"] / f"{term}.md"
        if path.exists():
            print(f"  ok  {term} (reference)")
        else:
            problems.append(f"{upstream['repo']}: term {term!r} not found under {upstream['dir']}")
    return problems


def check_upstream(upstream: dict, latest: bool, workdir: Path) -> list[str]:
    repo = upstream["repo"]
    ref = upstream["default_branch"] if latest else upstream["commit"]
    dest = workdir / repo.replace("/", "__")
    print(f"{repo} @ {ref}")
    if not clone(repo, ref, dest):
        return [f"{repo}: could not fetch {ref}"]
    if upstream.get("kind") == "reference":
        return check_reference(upstream, dest)
    skills = index_skills(dest / upstream["skills_dir"])
    problems: list[str] = []
    if upstream.get("plugin"):
        # The persona gives the user `/<plugin>:<skill>` for a user-invoked skill; a renamed plugin breaks every line.
        try:
            actual_plugin = json.loads((dest / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")).get("name")
        except (OSError, ValueError):
            actual_plugin = None
        if actual_plugin != upstream["plugin"]:
            problems.append(f"{repo}: its plugin is named {actual_plugin!r}; the persona gives users /{upstream['plugin']}:<skill>")
        else:
            print(f"  ok  plugin name {actual_plugin}")
    for name, expected in upstream["skills"].items():
        skill_md = skills.get(name)
        if skill_md is None:
            problems.append(f"{repo}: skill {name!r} not found under {upstream['skills_dir']}")
            continue
        flag = frontmatter(skill_md).get("disable-model-invocation", "false").lower() == "true"
        actual = "user" if flag else "model"
        if actual != expected:
            problems.append(f"{repo}: {name} is {actual}-invoked upstream; we assume {expected}")
        else:
            print(f"  ok  {name} ({actual})")
    return problems


def main(argv: list[str]) -> int:
    latest = "--latest" in argv
    manifests = [ROOT / "upstream.json"]
    if not manifests[0].exists():
        print("no upstream.json found at the plugin root")
        return 0
    problems: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for manifest in manifests:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            for upstream in data["upstreams"]:
                problems += check_upstream(upstream, latest, Path(tmp))
    if problems:
        print("\nUPSTREAM CHECK " + ("DRIFT (latest)" if latest else "FAILED") + ":")
        for p in problems:
            print(f"  {p}")
        return 0 if latest else 1
    print("\nall upstream skills present with the expected invocation")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
