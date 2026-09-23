#!/usr/bin/env python3
"""Print the path of an installed skill's SKILL.md, by name, or the line a person types to start it.

No harness lets the model start a skill marked `disable-model-invocation: true`:
Claude Code's Skill tool refuses it, Copilot CLI's answers "Skill not found".
Only a person typing it starts one, so the persona gives the user the exact
line `--typed` prints: `/<plugin>:<skill>` when the skill ships in a plugin (the
form Copilot CLI, Claude Code and VS Code all accept; Copilot CLI answers
"Unknown command" to a bare plugin skill name), `/<skill>` when it was installed
on its own (`npx skills add`). When the person asks the agent to run it instead,
the persona locates the file with this script, reads it, and follows it; reading
is refused nowhere. The door check uses it too: a skill is installed when this
finds it.

Usage:
    python3 find_skill.py wayfinder
    python3 find_skill.py grilling tdd code-review      # one path per line
    python3 find_skill.py --typed wayfinder             # the line to type, e.g. /mattpocock-skills:wayfinder
    python3 find_skill.py --door-check [--no-cache]     # every skill in upstream.json; a clean
                                                        # result is cached for a day

Exit codes: 0 every name was found; 1 at least one was not (the missing names
and the directories searched go to stderr). `--typed` still prints its best line
for a missing skill, from the plugin `upstream.json` names, and exits 1.

Search order, first hit wins: Claude Code's installed plugin cache (the version
marked in use), then project and user skill directories for Claude Code and the
Agent Skills standard, then everything under ~/.copilot (Copilot CLI's installed
plugins and skills), then VS Code's agentPlugins folders, then Claude Code's
marketplace clones.
A match is a directory named <name>, or any SKILL.md whose frontmatter `name:`
is <name> (some skills live in a directory named differently).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

HOME = Path.home()
CWD = Path.cwd()
VSCODE_APPS = ("Code", "Code - Insiders")
VSCODE_USER_DIRS = [
    HOME / ".config",  # Linux
    HOME / "Library" / "Application Support",  # macOS
    Path(os.environ.get("APPDATA", str(HOME / "AppData" / "Roaming"))),  # Windows
]
ROOTS: list[Path] = [
    HOME / ".claude" / "plugins" / "cache",
    CWD / ".claude" / "skills",
    HOME / ".claude" / "skills",
    CWD / ".agents" / "skills",
    HOME / ".agents" / "skills",
    CWD / ".github" / "skills",
    HOME / ".copilot",  # Copilot CLI: installed-plugins/ and user skills live under here
    # VS Code's own plugin installs (chat.plugins.marketplaces), stable and Insiders
    *(base / app / "agentPlugins" for base in VSCODE_USER_DIRS for app in VSCODE_APPS),
    HOME / ".claude" / "plugins" / "marketplaces",
]
NAME_RE = re.compile(r"^name:\s*['\"]?([^'\"\n]+)", re.MULTILINE)
SKIP_DIRS = {"node_modules", ".git"}
# Where a plugin names itself; the harnesses prefix its skills' commands with that name.
PLUGIN_MANIFESTS = (
    Path(".claude-plugin") / "plugin.json",
    Path("plugin.json"),
    Path(".github") / "plugin" / "plugin.json",
)
MANIFEST = Path(__file__).resolve().parent.parent / "upstream.json"


def frontmatter_name(skill_md: Path) -> str:
    try:
        head = skill_md.read_text(encoding="utf-8", errors="replace")[:2000]
    except OSError:
        return ""
    if not head.startswith("---"):
        return ""
    m = NAME_RE.search(head.split("\n---", 1)[0])
    return m.group(1).strip() if m else ""


def in_use_rank(path: Path) -> int:
    """0 when the containing plugin version is the one Claude Code marks in use, else 1."""
    for parent in path.parents:
        if (parent / ".in_use").exists():
            return 0
        if parent.name == "cache":
            break
    return 1


def candidates(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        if "SKILL.md" in filenames:
            found.append(Path(dirpath) / "SKILL.md")
    return found


def find(name: str) -> Path | None:
    for root in ROOTS:
        hits = [p for p in candidates(root) if p.parent.name == name or frontmatter_name(p) == name]
        if hits:
            hits.sort(key=lambda p: (in_use_rank(p), str(p)))
            return hits[0]
    return None


def plugin_name(skill_md: Path) -> str:
    """The name of the plugin this SKILL.md ships in; empty for a skill installed on its own.

    Walks up from the skill's folder to the search root it was found under, so a
    project skill in `.agents/skills/` is never credited to a plugin manifest that
    happens to sit at the project's root.
    """
    stop = next((root for root in ROOTS if skill_md.is_relative_to(root)), None)
    for parent in skill_md.parents:
        if parent == stop:
            break
        for rel in PLUGIN_MANIFESTS:
            try:
                name = json.loads((parent / rel).read_text(encoding="utf-8")).get("name")
            except (OSError, ValueError, AttributeError):
                continue
            if isinstance(name, str) and name:
                return name
    return ""


def upstream_plugin(name: str) -> str:
    """The plugin upstream.json says ships `name`, for a skill that is not installed."""
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    for upstream in data.get("upstreams", []):
        if name in upstream.get("skills", {}):
            return str(upstream.get("plugin", ""))
    return ""


def typed(name: str) -> tuple[str, bool]:
    """The line a person types to start `name`, and whether the skill was found."""
    path = find(name)
    if path is None:
        plugin = upstream_plugin(name)
        return (f"/{plugin}:{name}" if plugin else f"/{name}"), False
    command = frontmatter_name(path) or path.parent.name
    plugin = plugin_name(path)
    return (f"/{plugin}:{command}" if plugin else f"/{command}"), True


def door_check(*, use_cache: bool = True) -> int:
    """Check the skills in upstream.json; print what is missing and how to install it.

    A clean result is cached for a day per repo and upstream.json version, so a
    session start costs one stat instead of a walk of every skill directory.
    """
    manifest = MANIFEST
    stamp_key = f"{CWD.resolve()}|{manifest.stat().st_mtime_ns}".encode()
    stamp = Path(tempfile.gettempdir()) / "python-dev-guard" / (
        "door-" + hashlib.sha256(stamp_key).hexdigest()[:16]
    )
    if use_cache and stamp.exists() and time.time() - stamp.stat().st_mtime < 86400:
        print("door check: every upstream skill is installed (cached; --no-cache to recheck)")
        return 0
    data = json.loads(manifest.read_text(encoding="utf-8"))
    missing = 0
    pyproject = CWD / "pyproject.toml"
    deps = pyproject.read_text(encoding="utf-8", errors="replace") if pyproject.exists() else ""
    for upstream in data["upstreams"]:
        if "skills" not in upstream:
            continue  # a reference the persona links to, not skills to find on disk
        needs = upstream.get("only_when_dependency")
        if needs and needs not in deps:
            continue
        absent = [name for name in upstream["skills"] if find(name) is None]
        if absent:
            missing += len(absent)
            print(f"missing from {upstream['repo']}: {', '.join(absent)}")
            print(f"  install: {upstream['install']}")
    if missing == 0:
        print("door check: every upstream skill is installed")
        stamp.parent.mkdir(parents=True, exist_ok=True)
        stamp.touch()
    return 1 if missing else 0


def main(names: list[str]) -> int:
    if not names:
        print(__doc__, file=sys.stderr)
        return 1
    if names and names[0] == "--door-check":
        return door_check(use_cache="--no-cache" not in names)
    if names[0] == "--typed":
        status = 0
        for name in names[1:]:
            line, found = typed(name)
            print(line)
            if not found:
                print(f"not installed: {name}; the door check prints its install line", file=sys.stderr)
                status = 1
        return status if names[1:] else 1
    missing: list[str] = []
    for name in names:
        path = find(name)
        if path is None:
            missing.append(name)
            continue
        print(path)
    if missing:
        print(f"not found: {', '.join(missing)}", file=sys.stderr)
        print("searched: " + ", ".join(str(r) for r in ROOTS), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
