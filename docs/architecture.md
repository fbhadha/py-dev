# Architecture

The rules only. The live map (modules, callers, entry points, hotspots) is Repowise: `docs/agents/repowise-map.md`, `uv run repowise context <file>`, or `uv run repowise serve` for the dashboard. Nothing here repeats what the index can answer.

## What this repo is

A plugin, not a library: Markdown that a harness loads (the persona, the skills, the packs) and a small amount of Python that the harness or CI runs (`scripts/`). There is no `src/`, no package and no layering contract; the product code is twelve scripts.

## The three kinds of Python, and who checks each

| Where | What it is | Checked by |
|---|---|---|
| `scripts/hooks/` | the five hooks a harness starts through `hooks/*.json`; they share `_common.py` and nothing else | `scripts/test_hooks.py` in `validate.yml`; ruff, mypy strict and the size gate at commit |
| `scripts/check_*.py`, `find_skill.py`, `render_agents.py` | plugin checks and the two helpers; each stands alone with its own `main()` | `validate.yml`, one step per check; the commit gate |
| `skills/**/templates/`, `skills/**/references/example/` | shipped artifacts copied into a target repo by intake | `check_pack_examples.py` and `check_template_deps.py`, in a scratch copy; this repo's ruff and mypy skip them |

## The rules

- **One persona source.** `agents/python-dev.md` (and `py-eval.md`) is the source; `com.github.copilot/agents/*.agent.md` is rendered from it by `scripts/render_agents.py` and never edited by hand.
- **A hook fails open.** When a hook cannot decide (no repo, no payload, the plugin root not expanded), it allows and says nothing; the guard is CI and branch protection, not the hook (ADR 0002, 0006).
- **A check is a script with a `main()` returning 0 or 1**, printed reasons first, run by one step in `validate.yml`. Adding one is the shape `docs/howto/add-a-plugin-check.md` describes.
- **Nothing is copied from upstream.** Matt Pocock's and Google's skills are called by name; `upstream.json` pins them and `check_upstream_skills.py` proves they still exist (ADR 0004).

## Decisions

`docs/adr/`. Each ADR names the paths it governs under `## Scope`; Repowise binds them and `repowise why <path>` shows which decisions apply to a file.
