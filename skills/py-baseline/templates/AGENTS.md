# {{PROJECT}}

Pointers only. Every harness reads this file; `CLAUDE.md` includes it. Keep this section under 40 lines. Below the `REPOWISE:START` marker is the section Repowise maintains (architecture map, entry points, health, its tools); do not edit inside the markers.

## Read first

- `CONTEXT.md`: the words this repo uses. Use them; do not invent synonyms.
- `docs/architecture.md`: the layering rules and the composition root. The import-linter contract in `pyproject.toml` enforces them. The live map of modules and callers is Repowise, below.
- `docs/howto/`: one file per kind of addition (a shape). Build by the matching how-to; if none matches, it is a new shape and needs the interview first.
- `docs/adr/`: decisions already taken. Repowise binds each to the paths it governs and warns you when you edit one. Do not reopen a decision without a new ADR.
- `docs/agents/mode.md`: guide mode settings. `docs/agents/issue-tracker.md`: where tickets live.

## Commands

```bash
uv sync                                   # install
uv run pytest -m "not eval"               # tests without live models
uv run pre-commit run --all-files         # the commit gate on everything
uv run repowise health                    # whole-repo health, worst files first
uv run python scripts/adr_sync.py         # re-index and bind ADRs after writing one
```

## Rules the checks enforce (so nobody argues about them)

Modules under 400 lines, tests under 150. No `utils`/`helpers`/`common`/`misc` modules. Domain imports no I/O. No blind `except`, no `print`, no TODO without an owner and an issue. Tests before code, at an agreed seam; existing tests are read-only from red to green. `pytest` treats warnings as errors. A diff that makes a touched file worse fails CI (`scripts/repowise_gate.py`).

## Packs

<!-- py-intake lists the knowledge packs it selected from pyproject.toml, one per line, e.g. pack-data-engineering -->

## Agent

The `python-dev` persona (plugin `python-dev`, repo `fbhadha/py-dev`) is the intended session agent. Its skills: `py-design` (craft), `py-baseline` (this layout), `py-intake` (set up or re-orient), `ask-dev` (what to run next). Process skills come from Matt Pocock's plugin; codebase intelligence from the Repowise plugin. Both are called by name.
