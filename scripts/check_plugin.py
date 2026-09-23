#!/usr/bin/env python3
"""Check that this plugin is well-formed. CI runs it; run it before a release.

  - every skills/<name>/SKILL.md starts with YAML frontmatter whose `name` equals
    the folder, whose `description` is non-empty and at most 1024 characters,
    and whose name contains neither 'anthropic' nor 'claude'
  - .claude-plugin/plugin.json lists exactly the skill folders that exist
  - the three manifests (plugin.json for Copilot, .claude-plugin/plugin.json for
    Claude Code, .claude-plugin/marketplace.json) carry the same name and version
  - .github/plugin/marketplace.json (Copilot's path) is identical to
    .claude-plugin/marketplace.json (Claude Code's path)
  - every agents/<name>.md has frontmatter with `name` and `description`
  - the rendered Copilot agents under com.github.copilot/agents/ match what
    scripts/render_agents.py would write
  - every JSON file (manifests, both hooks files, upstream.json) parses
  - agents/python-dev.md stays under PERSONA_MAX_CHARS: it holds the loop, the voice,
    the pushback and the routing table, loaded every turn; every step list belongs
    in a skill it names
  - the persona names the plugin version the manifests carry, because its status
    line is how the user tells it from the default agent where no hook runs
  - every folder under skills/ is named by a routing row in agents/python-dev.md,
    so nothing moved out of the persona can become unreachable

Exit code is non-zero on any failure.

Usage: python scripts/check_plugin.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
RESERVED = ("anthropic", "claude")
JSON_FILES = (
    "plugin.json",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    ".github/plugin/marketplace.json",
    "hooks/hooks.json",
    "com.github.copilot/hooks/hooks.json",
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
    return problems


def check_agent(agent_md: Path) -> list[str]:
    rel = agent_md.relative_to(ROOT)
    fm = frontmatter(agent_md)
    if isinstance(fm, str):
        return [f"{rel}: {fm}"]
    return [f"{rel}: frontmatter needs '{key}'" for key in ("name", "description") if not fm.get(key)]


def check_rendered_agents() -> list[str]:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "render_agents.py"), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        print("ok  com.github.copilot/agents/*.agent.md (rendered from agents/)")
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]

PERSONA = ROOT / "agents" / "python-dev.md"
PERSONA_MAX_CHARS = 14_000  # about 3,900 tokens at 3.6 characters per token, loaded every turn


def check_persona_budget() -> list[str]:
    """The persona is the router; the steps live in skills. CI holds that line."""
    text = PERSONA.read_text(encoding="utf-8")
    problems: list[str] = []
    if len(text) > PERSONA_MAX_CHARS:
        problems.append(
            f"agents/python-dev.md is {len(text):,} characters; the ceiling is "
            f"{PERSONA_MAX_CHARS:,} (about {round(PERSONA_MAX_CHARS / 3.6):,} tokens, loaded "
            "every turn). Grow a skill, not the persona."
        )
    named = set(re.findall(r"Skill `([a-z0-9-]+)`", text))
    for folder in sorted(d.name for d in (ROOT / "skills").iterdir() if d.is_dir()):
        if folder not in named:
            problems.append(
                f"skills/{folder} is not named by any routing row in agents/python-dev.md, "
                "so nothing runs it"
            )
    if not problems:
        print(
            f"ok  agents/python-dev.md: {len(text):,} of {PERSONA_MAX_CHARS:,} characters; "
            "every skill reachable"
        )
    return problems


REF_RE = re.compile(r"`?((?:templates|references|scripts)/[A-Za-z0-9_.-]+\.[a-z]+)`?")
CALL_RE = re.compile(r"(?:Skill|File) `([a-z][a-z0-9-]+)`|Skill tool with \"([a-z][a-z0-9-]+)\"")
STEP_RE = re.compile(r"\b[Ss]tep (\d+)\b")
SECTION_RE = re.compile(r"\bsection (\d+)\b")
PACK_SECTIONS = (
    "## Selected when",
    "## Shapes",
    "## Canonical repo",
    "## Extra checks this pack turns on",
    "## Faults this pack looks for",
    "## Tests",
)


def upstream_names() -> set[str]:
    data = json.loads((ROOT / "upstream.json").read_text(encoding="utf-8"))
    return {name for up in data["upstreams"] for name in up.get("skills", {})}


def resolve_ref(ref: str, here: Path, line: str, upstream: set[str]) -> bool:
    """A templates/, references/ or scripts/ path must exist here, in py-baseline, or upstream."""
    candidates = [here / ref, ROOT / "skills" / "py-baseline" / ref, ROOT / ref]
    if ref.startswith("scripts/"):
        candidates.append(ROOT / "skills" / "py-baseline" / "templates" / Path(ref).name)
    if ref.startswith("templates/"):
        candidates += [d / ref for d in (ROOT / "skills").iterdir()]
    if ref.startswith("references/"):
        candidates += [d / ref for d in (ROOT / "skills").iterdir()]
    if any(c.exists() for c in candidates):
        return True
    return ref.startswith("references/") and any(name in line for name in upstream)


def check_references(doc: Path) -> list[str]:
    """Every file, skill, step and section a document names must exist."""
    problems: list[str] = []
    rel = doc.relative_to(ROOT)
    text = doc.read_text(encoding="utf-8")
    upstream = upstream_names()
    local = {d.name for d in (ROOT / "skills").iterdir() if d.is_dir()}
    headings = len(re.findall(r"^## \d+\.", text, re.M))
    for line in text.splitlines():
        for ref in REF_RE.findall(line):
            if not resolve_ref(ref, doc.parent, line, upstream):
                problems.append(f"{rel}: names `{ref}`, which does not exist")
        for a, b in CALL_RE.findall(line):
            name = a or b
            if name not in local | upstream:
                problems.append(f"{rel}: calls skill `{name}`, not in skills/ or upstream.json")
        pattern = STEP_RE if "py-intake" in str(rel) else SECTION_RE
        for num in pattern.findall(line):
            if headings and int(num) > headings:
                problems.append(f"{rel}: refers to {pattern.pattern[3:-3]} {num}; only {headings} exist")
    if doc.parent.name.startswith("pack-"):
        for section in PACK_SECTIONS:
            if section not in text:
                problems.append(f"{rel}: pack is missing the template section `{section}`")
    return problems


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

    agent_files = sorted(ROOT.glob("agents/*.md"))
    for agent_md in agent_files:
        found = check_agent(agent_md)
        problems += found
        if not found:
            print(f"ok  {agent_md.relative_to(ROOT)}")

    problems += check_rendered_agents()
    problems += check_persona_budget()
    for doc in [*skill_files, *agent_files]:
        problems += check_references(doc)

    plugin = parsed.get(".claude-plugin/plugin.json")
    marketplace = parsed.get(".claude-plugin/marketplace.json")
    if plugin is not None:
        listed = sorted(Path(p).name for p in plugin.get("skills", []))
        present = sorted(p.parent.name for p in skill_files)
        if listed != present:
            problems.append(
                f"plugin.json skills {listed} do not match the folders under skills/ {present}"
            )
    copilot = parsed.get("plugin.json")
    if plugin is not None:
        version = plugin.get("version")
        persona = PERSONA.read_text(encoding="utf-8")
        if f"python-dev {version}" not in persona:
            problems.append(
                f"agents/python-dev.md must name `python-dev {version}` (its status line); "
                "bump it with the manifests"
            )
    if plugin is not None and marketplace is not None and copilot is not None:
        versions = {
            ".claude-plugin/plugin.json": plugin.get("version"),
            "plugin.json": copilot.get("version"),
            ".claude-plugin/marketplace.json": (marketplace.get("metadata") or {}).get("version"),
        }
        if len(set(versions.values())) != 1:
            problems.append(f"manifest versions differ: {versions}")
        if plugin.get("name") != copilot.get("name"):
            problems.append("plugin.json and .claude-plugin/plugin.json name differ")
    copilot_market = parsed.get(".github/plugin/marketplace.json")
    if marketplace is not None and copilot_market is not None and marketplace != copilot_market:
        problems.append(".github/plugin/marketplace.json must be identical to .claude-plugin/marketplace.json")

    if problems:
        print("\nPLUGIN CHECK FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"\nplugin ok: {len(skill_files)} skills, {len(agent_files)} agents")
    return 0


if __name__ == "__main__":
    sys.exit(main())
