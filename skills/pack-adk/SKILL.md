---
name: pack-adk
description: "Knowledge pack for Google ADK 2.x repos: which of Google's adk-* skills to open for which job, and the six rules this baseline adds (layout, typed node edges, exceptions in tools, state through events, three test tiers, secrets). Reference only. Use when building or reviewing an ADK agent, workflow, tool or node. Not for 1.x: that is adk-migrate."
---

# ADK pack

Google maintains the ADK skills in `google/adk-python` under `.agents/skills/`. They are the framework knowledge; nothing here repeats them. This pack says which of them to open for which job, and what this baseline adds on top. Guide voice: the first time an ADK term appears (node, workflow, event, session, tool), one plain sentence on what it means here.

## Selected when

`google-adk` 2.x is a dependency (`uv pip show google-adk`). 1.x: stop and run `adk-migrate` first. Absent: `uv add "google-adk>=2.0"` after asking.

## Door check

`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/find_skill.py" adk-agent-builder adk-architecture adk-debug adk-style` must print four paths. If not: `npx skills@latest add google/adk-python -s adk-agent-builder,adk-architecture,adk-debug,adk-style -a '*' -y` in the repo (installs to `.agents/skills/`, symlinked for Claude Code and Copilot). The other skills in that directory are for people contributing to adk-python itself; do not install them.

Never improvise what one of Google's skills would say; open it. Their references were checked against a stated `google-adk` version (the skill's head says which); when the installed version is newer, read `src/google/adk/` in the installed package before relying on a signature, as their skill tells you to.

## Which of Google's skills, for which job

| You are | Open |
|---|---|
| Creating an agent, a workflow, a tool, a node; routing, fan-out, loops; pausing for a human; testing an agent | `adk-agent-builder`: only the reference its table names for the task, and always `references/best-practices.md` before the first line, because every rule in it is a silent failure |
| Explaining or deciding how the runtime fits together, where a capability belongs, why a node re-ran | `adk-architecture` |
| An agent that runs but misbehaves | `adk-debug`, after `diagnosing-bugs` has a red-capable loop |
| Naming, typing, Pydantic, async and file-layout conventions inside agent code | `adk-style`; where it conflicts with this baseline's tool tables (formatter, line length), the baseline wins and you say so |

## What this baseline adds

1. **Layout.** ADK's CLI discovers an agent by convention: a package with `__init__.py` doing `from . import agent`, an `agent.py` defining `root_agent`, and `.env` beside it. Keep that convention for the entrypoint only, under `src/{{PACKAGE}}/entrypoints/agents/<name>/`. Everything the agent calls lives in the layers below: tools in `src/{{PACKAGE}}/application/tools/` as typed functions, prompts in `prompts.py` or loaded files, domain models in `domain/`, external systems behind `adapters/`. An agent package that imports a database driver has skipped a layer; import-linter says so.
2. **Types at every node edge.** Node inputs, outputs, `output_schema` and state values are Pydantic models named from `CONTEXT.md`, never `dict[str, Any]` (Google's first rule, and `py-design` rule 2).
3. **Exceptions in tools are interface.** A tool catches the specific error it can turn into a useful result and lets everything else propagate. A broad `except` inside a tool hides the failure from the runtime's retry and human-in-the-loop handling and from the user. ruff `BLE001` flags it; the reviewer flags the narrower version.
4. **State goes through events.** `Event(state=...)`, never `ctx.state[key] = ...`; one output event per node; a node yields or returns, never both; `{var}` in an instruction reads state, not `node_input`. All from Google's `best-practices.md`; the reviewer checks them because no linter does.
5. **Three test tiers.** `tests/unit/`: `InMemoryRunner` with a faked model, following Google's `references/testing.md`, no network. `tests/integration/`: adapters against a local substitute. `tests/evals/`: live model runs, marked `eval`, excluded from the commit gate and CI (`pytest -m "not eval"`), run on demand. `asyncio_mode = "auto"` in the pytest table.
6. **Secrets.** `.env` beside `agent.py` is gitignored; `.env.example` at the repo root lists every key; `pydantic-settings` reads them once at the entrypoint.

## Canonical repo

`google/adk-python` itself, at the commit pinned in `upstream.json`. Cite `.agents/skills/adk-agent-builder/references/getting-started.md` for the entrypoint layout (`__init__.py` re-exporting `agent`, `agent.py` defining `root_agent`, `.env` beside it), `references/testing.md` for the `InMemoryRunner` test with a faked model, and `references/best-practices.md` for the four runtime rules above. `src/google/adk/agents/base_agent.py` for what is deprecated (`from_config`, `_parse_config`) and `sequential_agent.py` for the deprecated shells.

## Extra checks this pack turns on

Added by `py-intake` step 5 when the pack is selected:

- `uv add --group dev pytest-asyncio` and `asyncio_mode = "auto"` in `[tool.pytest.ini_options]` (Google's `testing.md` setup; the baseline does not carry it).
- import-linter: `{{PACKAGE}}.entrypoints.agents` may import `{{PACKAGE}}.application` and `{{PACKAGE}}.domain` only; a database driver or HTTP client imported by an agent package fails the contract.
- ruff `BLE001` already on from the baseline; `B901` (return inside a generator) already on via `B`. Nothing custom: the runtime rules a linter cannot see are the reviewer's.

## Shapes

| Shape | The how-to it gets | The seam |
|---|---|---|
| Agent | `add-an-agent.md`: one entrypoint package by ADK's convention, everything it calls in the layers below | `InMemoryRunner` with a faked model |
| Tool | `add-a-tool.md`: one typed function under `application/tools/`, its external system behind an adapter | the function, with an in-memory adapter |
| Node or workflow | `add-a-node.md`: typed input and output models, state through events | `InMemoryRunner`, asserting on the events |

Building any of them goes through the persona's build steps (name the shape, ask the index, Matt Pocock's `implement` with `tdd`). Open the Google reference for the task first and say in two sentences what pattern it recommends and why it fits here. The review's Craft axis carries the four rules above that no linter enforces.

## Tests

Unit: `InMemoryRunner` with a faked model (`testing.md` shows the fake), asserting on the events and the final state; no network, no `GOOGLE_API_KEY`. Integration: a tool's adapter against a local substitute. Never in the unit tier: a live model, a real MCP server, a real API.

## An eval is not a unit test

A unit test fakes the model and pins a behaviour. An eval calls the model and measures a score over a set. An agent with no evals has no way to tell a refactor from a regression; the first ticket in an ADK repo with none is "write the evals for what exists", and `adk-migrate` insists on it.
