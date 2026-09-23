# {{PROJECT}}

Pointers and the rules of work. Every harness reads this file; `CLAUDE.md` includes it. Keep it under 60 lines. The live map (architecture, entry points, health) is `docs/agents/repowise-map.md`, written only by Repowise; do not edit it.

## How work happens here

These hold for every agent and every person, whichever agent is selected.

1. **No ticket, no code.** Every change starts as a ticket in the tracker named in `docs/agents/issue-tracker.md`; a one-line fix gets a one-line ticket.
2. **Ideas are shaped before they are built**: a senior engineer's read of the idea (build it, change it, or drop it), a grilling on the open decisions, a spec, then tickets. A change to something already decided (a term, an ADR, a spec, a ticket) is re-shaped the same way before any code.
3. **Every ticket carries its plan**: the files, the functions and their signatures, the tests in the order they are written, the commands that prove it. The plan is shown and agreed before the first line of code.
4. **One ticket, one branch** (`ticket/<id>-<slug>`), tests first, the checks green; `main` changes only by a merge a person approved.

The `python-dev` agent runs this loop for you: pick it in the agent picker (`copilot --agent python-dev:python-dev` in Copilot CLI).

## Read first

- `CONTEXT.md`: the words this repo uses. Use them; do not invent synonyms.
- `docs/architecture.md`: the layering rules and the composition root. The import-linter contract in `pyproject.toml` enforces them. The live map of modules and callers is Repowise, below.
- `docs/howto/`: one file per kind of addition (a shape). Build by the matching how-to; if none matches, it is a new shape and needs the interview first.
- `docs/adr/`: decisions already taken. Repowise binds each to the paths it governs and warns you when you edit one. Do not reopen a decision without a new ADR.
- `docs/research/`: what was checked outside this repo and when, one dated, cited note per question. Facts, not decisions; a decision is an ADR.
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

The `python-dev` persona (plugin `python-dev`, repo `fbhadha/py-dev`) is the intended session agent. Its skills: `py-intake` (set up or re-orient), `py-shape` (an idea to its tickets), `py-build` (a ticket to its merge), `py-review`, `py-design` (craft), `py-baseline` (this layout), the packs listed above. Process skills come from Matt Pocock's plugin, called by name; codebase intelligence from the Repowise CLI. The words of AI coding itself (session, handoff, spec, ticket, grilling) are his AI Coding Dictionary, <https://github.com/mattpocock/dictionary-of-ai-coding>; `CONTEXT.md` holds this repo's words only.
