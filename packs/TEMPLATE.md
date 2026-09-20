# Pack template

A pack is a reference-only skill named `pack-<domain>` under `skills/`. It changes nothing about how the agent works; it changes what the agent knows when the repo is of a kind. `py-intake` selects packs from `pyproject.toml` dependencies; `py-design` stays the general craft reference. The ADK pack is the pair `adk-build` and `adk-migrate` plus Google's own skills, because framework work needs procedures as well as reference; every other pack is one file in this shape.

Copy this file to `skills/pack-<domain>/SKILL.md`, add `agents/openai.yaml`, fill every section, run `python scripts/validate_skills.py`, and add the name to `.claude-plugin/plugin.json`.

```markdown
---
name: pack-<domain>
description: Knowledge pack for <domain> repos in Python (<the libraries>). Reference only. Use when the repo's dependencies match, or when designing or reviewing <the things this domain builds>. Selected automatically by py-intake from pyproject.toml.
license: Apache-2.0
metadata:
  author: <you>
  version: 0.1.0
  tags: [python, <domain>, pack]
---

# <Domain> pack

## Selected when
The dependency names that select this pack.

## Shapes
A table: shape, the how-to it gets (`docs/howto/add-a-<shape>.md`), the seam tests drive.

## Canonical repo
One well-known repo and the paths to cite, with the sentence to say for each.

## Extra checks this pack turns on
ruff rule groups, import-linter contracts, pre-commit hooks, dev dependencies that py-intake adds when the pack is selected. Established tools only; no custom gates.

## Faults this pack looks for (beyond the catalogue)
A table: fault, tell, fix. Only faults specific to this domain; the general ones are in py-design's fault catalogue.

## Tests
What a unit test looks like here, what is integration, what is never allowed in the unit tier.
```

Rules: no procedures (those belong in a skill with a verb in its name), no copies of another skill's content (cite it), nothing a linter enforces (turn the linter on instead), and every claim about a library checked against its current docs with the version noted.
