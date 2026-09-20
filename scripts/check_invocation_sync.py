#!/usr/bin/env python3
"""Keep the two invocation switches in step across harnesses.

For every SKILL.md under skills/:

  frontmatter `disable-model-invocation: true`
      <=>  agents/openai.yaml `policy.allow_implicit_invocation: false`

Every skill must have an agents/openai.yaml (Codex reads it for the display
name and the policy). Exit code is non-zero on any mismatch.

Usage: python scripts/check_invocation_sync.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def frontmatter(path: Path) -> dict:
    match = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        print(f"{path}: frontmatter is not valid YAML: {exc}")
        return {}


def main() -> int:
    failures: list[str] = []
    skill_files = sorted(ROOT.glob("skills/*/SKILL.md"))
    for skill_md in skill_files:
        rel = skill_md.relative_to(ROOT)
        user_only = bool(frontmatter(skill_md).get("disable-model-invocation", False))
        openai_yaml = skill_md.parent / "agents" / "openai.yaml"
        if not openai_yaml.exists():
            failures.append(f"{rel}: missing agents/openai.yaml")
            continue
        data = yaml.safe_load(openai_yaml.read_text(encoding="utf-8")) or {}
        implicit = (data.get("policy") or {}).get("allow_implicit_invocation", True)
        if user_only and implicit:
            failures.append(f"{rel}: user-invoked but openai.yaml allows implicit invocation")
        if not user_only and implicit is False:
            failures.append(f"{rel}: model-invoked but openai.yaml forbids implicit invocation")
        else:
            print(f"ok  {rel}")
    if failures:
        print("\nINVOCATION SYNC FAILED:")
        for failure in failures:
            print(f"  {failure}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
