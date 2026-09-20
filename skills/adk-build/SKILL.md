---
name: adk-build
description: "Build or change a Google ADK 2.x agent, workflow, tool or node. Routes into Google's adk-agent-builder, adk-architecture, adk-debug and adk-style and adds this baseline's layout, test tiers and craft rules. Not for 1.x."
license: Apache-2.0
metadata:
  author: fbhadha
  version: 0.1.0
  tags: [python, adk, agents, google]
---

# ADK build

Google maintains the ADK skills in `google/adk-python` under `.agents/skills/`. They are the framework knowledge; nothing here repeats them. This skill says which of them to open for which job, and what this baseline adds on top. Guide voice: before each step, one plain paragraph on what an ADK term means here the first time it appears (node, workflow, event, session, tool).

## Door check

| Need | Test | If missing |
|---|---|---|
| `google-adk` 2.x in the dependencies | `uv pip show google-adk` | 1.x: stop and run `adk-migrate` first. Absent: `uv add "google-adk>=2.0"`. |
| Google's skills | `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/find_skill.py" adk-agent-builder adk-architecture adk-debug adk-style` prints four paths | `npx skills@latest add google/adk-python -s adk-agent-builder,adk-architecture,adk-debug,adk-style -a '*' -y` in the repo (installs to `.agents/skills/`, symlinked for Claude Code, Codex and Copilot). The other seven ADK skills are for people contributing to adk-python itself; do not install them here. |

Never improvise what one of Google's skills would say; open it. Their references were checked against a stated `google-adk` version (the skill's head says which); when the installed version is newer, read `src/google/adk/` in the installed package before relying on a signature, exactly as their skill tells you to.

## Which of Google's skills, for which job

| You are | Open |
|---|---|
| Creating an agent, a workflow, a tool, a node; routing, fan-out, loops; pausing for a human; testing an agent | `adk-agent-builder`: read only the reference its table names for the task, and always `references/best-practices.md` before the first line, because every rule in it is a silent failure |
| Explaining or deciding how the runtime fits together, where a capability belongs, why a node re-ran | `adk-architecture` |
| An agent that runs but misbehaves | `adk-debug`, after `diagnosing-bugs` has a red-capable loop |
| Naming, typing, Pydantic, async and file-layout conventions inside agent code | `adk-style`; where it conflicts with this baseline's tool tables (formatter, line length), the baseline wins and you say so |

## What this baseline adds

1. **Layout.** ADK's CLI discovers an agent by convention: a package with `__init__.py` doing `from . import agent`, an `agent.py` defining `root_agent`, and `.env` beside it. Keep that convention for the entrypoint only, under `src/{{PACKAGE}}/entrypoints/agents/<name>/`. Everything the agent calls lives in the layers below it: tools in `src/{{PACKAGE}}/application/tools/` as typed functions, prompts in `prompts.py` or loaded files, domain models in `domain/`, external systems behind `adapters/`. An agent package that imports a database driver has skipped a layer; import-linter says so.
2. **Types at every node edge.** Node inputs, outputs, `output_schema` and state values are Pydantic models from `CONTEXT.md` terms, never `dict[str, Any]` (Google's first rule, and this baseline's rule 2).
3. **Exceptions in tools are interface.** A tool catches the specific error it can turn into a useful result and lets everything else propagate; a broad `except` inside a tool hides the failure from the runtime's retry and human-in-the-loop handling and from the user. ruff `BLE001` flags it; the reviewer flags the narrower version.
4. **State goes through events.** `Event(state=...)`, never `ctx.state[key] = ...`; one output event per node; a node yields or returns, never both; `{var}` in an instruction reads state, not `node_input`. All from Google's `best-practices.md`; the reviewer checks them because no linter does.
5. **Three test tiers.** `tests/unit/`: `InMemoryRunner` with a faked model, following Google's `references/testing.md`, no network. `tests/integration/`: adapters against a local substitute. `tests/evals/`: live model runs, marked `eval`, excluded from the commit gate and CI (`pytest -m "not eval"`), run on demand. `asyncio_mode = "auto"` in the pytest table.
6. **Secrets.** `.env` beside `agent.py` is gitignored; `.env.example` at the repo root lists every key it needs, and `pydantic-settings` reads them once at the entrypoint.

## Process

1. Name the shape (persona rule): "adding another agent / tool / node?" The how-to in `docs/howto/add-an-agent.md` (written at intake or on the first agent) is the template; a new shape gets the interview and a new how-to first.
2. Skill tool with "pre-modification-check" on the files to touch; "architectural-decisions" when one governs them.
3. Open the Google reference for the task. Say in two sentences what pattern it recommends and why it fits here.
4. Build through `py-implement`: test first at the seam (`InMemoryRunner` with the faked model), one slice per acceptance criterion, checks after each green, the change gate before review.
5. `py-review`. Its Craft axis carries the four ADK rules above.

## An eval is not a unit test

A unit test fakes the model and pins a behaviour. An eval calls the model and measures a score over a set. An agent with no evals has no way to tell a refactor from a regression; the first `adk-build` ticket in a repo with none is "write the evals for what exists", and `adk-migrate` insists on it.
