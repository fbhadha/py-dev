# Pack template

A pack is a reference-only skill named `pack-<domain>` under `skills/`. It changes nothing about how the agent works; it changes what the agent knows when the repo is of a kind. `py-intake` selects packs from `pyproject.toml` dependencies; `py-design` stays the general craft reference. `pack-adk` is one: it routes into Google's own skills and adds six rules. `adk-migrate` is not a pack but a procedure, because a migration has steps.

Copy this file to `skills/pack-<domain>/SKILL.md`, fill every section, add the path to `skills` in `.claude-plugin/plugin.json`, and run `python scripts/check_plugin.py`.

```markdown
---
name: pack-<domain>
description: "Knowledge pack for <domain> repos in Python (<the libraries>). Reference only. Use when the repo's dependencies match, or when designing or reviewing <the things this domain builds>. Selected by py-intake from pyproject.toml."
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
