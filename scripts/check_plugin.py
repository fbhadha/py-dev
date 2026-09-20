#!/usr/bin/env python3
"""Check that this plugin is well-formed. CI runs it; run it before a release.

  - every skills/<name>/SKILL.md starts with YAML frontmatter whose `name` equals
    the folder, whose `description` is non-empty and at most 1024 characters,
    and whose name contains neither 'anthropic' nor 'claude'
  - every skill has agents/openai.yaml (Codex reads it), and its
    `policy.allow_implicit_invocation` agrees with `disable-model-invocation`
  - .claude-plugin/plugin.json lists exactly the skill folders that exist
  - plugin.json and marketplace.json carry the same version
  - every agents/<name>.md has frontmatter with `name` and `description`
  - plugin.json, marketplace.json, hooks/hooks.json and upstream.json parse

Exit code is non-zero on any failure.

Usage: python scripts/check_plugin.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
RESERVED = ("anthropic", "claude")
JSON_FILES = (
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    "hooks/hooks.json",
    "upstream.json",
)


def frontmatter(path: Path) -> dict | str:
    """The parsed frontmatter, or a string saying what is wrong with it."""
    match = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    if not match:
        return "must begin with YAML frontmatter delimited by ---"
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        return f"frontmatter is not valid YAML (quote values that contain ': '): {exc}"
    return data if isinstance(data, dict) else "frontmatter must be a mapping"


def check_skill(skill_md: Path) -> list[str]:
    rel = skill_md.relative_to(ROOT)
    fm = frontmatter(skill_md)
    if isinstance(fm, str):
        return [f"{rel}: {fm}"]
    problems: list[str] = []
    name = str(fm.get("name", ""))
    folder = skill_md.parent.name
    if name != folder:
        problems.append(f"{rel}: name '{name}' must equal folder name '{folder}'")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name or ""):
        problems.append(f"{rel}: name must be lowercase letters, digits and hyphens")
    if any(word in name.lower() for word in RESERVED):
        problems.append(f"{rel}: name must not contain 'anthropic' or 'claude'")
    description = str(fm.get("description", "")).strip()
    if not description:
        problems.append(f"{rel}: description is required")
    elif len(description) > 1024:
        problems.append(f"{rel}: description is {len(description)} characters; the limit is 1024")

    openai_yaml = skill_md.parent / "agents" / "openai.yaml"
    if not openai_yaml.exists():
        problems.append(f"{rel}: missing agents/openai.yaml")
    else:
        data = yaml.safe_load(openai_yaml.read_text(encoding="utf-8")) or {}
        implicit = (data.get("policy") or {}).get("allow_implicit_invocation", True)
        user_only = bool(fm.get("disable-model-invocation", False))
        if user_only and implicit:
            problems.append(f"{rel}: user-invoked but openai.yaml allows implicit invocation")
        if not user_only and implicit is False:
            problems.append(f"{rel}: model-invoked but openai.yaml forbids implicit invocation")
    return problems


def check_agent(agent_md: Path) -> list[str]:
    rel = agent_md.relative_to(ROOT)
    fm = frontmatter(agent_md)
    if isinstance(fm, str):
        return [f"{rel}: {fm}"]
    return [f"{rel}: frontmatter needs '{key}'" for key in ("name", "description") if not fm.get(key)]


def main() -> int:
    problems: list[str] = []

    parsed: dict[str, dict] = {}
    for rel in JSON_FILES:
        path = ROOT / rel
        try:
            parsed[rel] = json.loads(path.read_text(encoding="utf-8"))
            print(f"ok  {rel}")
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"{rel}: {exc}")

    skill_files = sorted(ROOT.glob("skills/*/SKILL.md"))
    for skill_md in skill_files:
        found = check_skill(skill_md)
        problems += found
        if not found:
            print(f"ok  {skill_md.relative_to(ROOT)}")

    for agent_md in sorted(ROOT.glob("agents/*.md")):
        found = check_agent(agent_md)
        problems += found
        if not found:
            print(f"ok  {agent_md.relative_to(ROOT)}")

    plugin = parsed.get(".claude-plugin/plugin.json")
    marketplace = parsed.get(".claude-plugin/marketplace.json")
    if plugin is not None:
        listed = sorted(Path(p).name for p in plugin.get("skills", []))
        present = sorted(p.parent.name for p in skill_files)
        if listed != present:
            problems.append(
                f"plugin.json skills {listed} do not match the folders under skills/ {present}"
            )
    if plugin is not None and marketplace is not None:
        pv = plugin.get("version")
        mv = (marketplace.get("metadata") or {}).get("version")
        if pv != mv:
            problems.append(f"plugin.json version {pv!r} and marketplace.json version {mv!r} differ")

    if problems:
        print("\nPLUGIN CHECK FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"\nplugin ok: {len(skill_files)} skills, {len(list(ROOT.glob('agents/*.md')))} agents")
    return 0


if __name__ == "__main__":
    sys.exit(main())
