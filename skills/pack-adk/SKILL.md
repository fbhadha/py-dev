---
name: pack-adk
description: "Knowledge pack for Google ADK 2.x repos: which of Google's adk-* skills to open for which job, and the six rules this baseline adds (layout, typed node edges, exceptions in tools, state through events, three test tiers, secrets). Reference only. Use when building or reviewing an ADK agent, workflow, tool or node. Not for 1.x: that is adk-migrate."
---

# ADK pack

Google maintains the ADK skills in `google/adk-python` under `.agents/skills/`. They are the framework knowledge; nothing here repeats them. This pack says which of them to open for which job, and what this baseline adds on top. Guide voice: the first time an ADK term appears (node, workflow, event, session, tool), one plain sentence on what it means here.

## Selected when

`google-adk` 2.x is a dependency (`uv pip show google-adk`). 1.x: stop and run `adk-migrate` first. Absent: `uv add "google-adk>=2.0"` after asking.

## Door check

`python3 <scripts>/find_skill.py adk-agent-builder adk-architecture adk-debug adk-style` must print four paths (`<scripts>` as the persona's section 5 says). If not: `npx skills@latest add google/adk-python -s adk-agent-builder,adk-architecture,adk-debug,adk-style -a '*' -y` in the repo (installs to `.agents/skills/`, symlinked for Claude Code and Copilot). The other skills in that directory are for people contributing to adk-python itself; do not install them.

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
5. **Three test tiers.** `tests/unit/`: `InMemoryRunner` with a faked model, following `adk-agent-builder`'s `references/testing.md`, no network. `tests/integration/`: adapters against a local substitute. `tests/evals/`: live model runs, marked `eval`, excluded from the commit gate and CI (`pytest -m "not eval"`), run on demand; scenarios played by ADK's simulated user, never inputs the author wrote (the outside user, below). `asyncio_mode = "auto"` in the pytest table.
6. **Secrets.** `.env` beside `agent.py` is gitignored; `.env.example` at the repo root lists every key; `pydantic-settings` reads them once at the entrypoint.

## Canonical repo

`google/adk-python` itself, at the commit pinned in `upstream.json`. Cite `.agents/skills/adk-agent-builder/references/getting-started.md` for the entrypoint layout (`__init__.py` re-exporting `agent`, `agent.py` defining `root_agent`, `.env` beside it), `references/testing.md` for the `InMemoryRunner` test with a faked model, and `references/best-practices.md` for the four runtime rules above. `src/google/adk/agents/base_agent.py` for what is deprecated (`from_config`, `_parse_config`) and `sequential_agent.py` for the deprecated shells.

## Extra checks this pack turns on

Added by `py-intake` step 5 when the pack is selected:

- `uv add --group dev pytest-asyncio` and `asyncio_mode = "auto"` in `[tool.pytest.ini_options]` (Google's `testing.md` setup; the baseline does not carry it).
- import-linter: `{{PACKAGE}}.entrypoints.agents` may import `{{PACKAGE}}.application` and `{{PACKAGE}}.domain` only; a database driver or HTTP client imported by an agent package fails the contract.
- ruff `BLE001` already on from the baseline; `B901` (return inside a generator) already on via `B`. Nothing custom: the runtime rules a linter cannot see are the reviewer's.
- `uv add --group dev "google-adk[eval]"` (the simulated user and the judges) and `.adk/` in `.gitignore` (`adk eval` writes its history there, inside the agent package).

## Shapes

| Shape | The how-to it gets | The seam |
|---|---|---|
| Agent | `add-an-agent.md`: one entrypoint package by ADK's convention, everything it calls in the layers below | `InMemoryRunner` with a faked model |
| Tool | `add-a-tool.md`: one typed function under `application/tools/`, its external system behind an adapter | the function, with an in-memory adapter |
| Node or workflow | `add-a-node.md`: typed input and output models, state through events | `InMemoryRunner`, asserting on the events |

Building any of them goes through Skill `py-build` (name the shape, ask the index, the plan shown first, `tdd` slice by slice). Open the Google reference for the task first and say in two sentences what pattern it recommends and why it fits here. The review's Craft axis carries the four rules above that no linter enforces.

## Faults this pack looks for (beyond the catalogue)

The four runtime rules no linter sees, each a silent failure in `adk-agent-builder`'s `references/best-practices.md`:

| Fault | Tell | Fix |
|---|---|---|
| Untyped edge | `dict[str, Any]` as a node input, output or `output_schema` | A Pydantic model named from `CONTEXT.md` |
| Direct state write | `ctx.state[key] = ...` | `Event(state={key: ...})`; reads stay `ctx.state[...]` |
| Two outputs, or yield and return | Two `Event(output=...)` in one node; a generator with `return Event(...)` | One output event; the rest carry state only; a function yields or returns |
| Input as placeholder | `{node_input}` in an instruction | `{var}` reads state; the input arrives as the user message |
| Blind except in a tool | `except Exception` inside `application/tools/` | Catch the one error the tool can turn into a result; let the rest reach the runtime |

## Tests

Unit: `InMemoryRunner` with a faked model (`testing.md` shows the fake), asserting on the events and the final state; no network, no `GOOGLE_API_KEY`. Integration: a tool's adapter against a local substitute. Never in the unit tier: a live model, a real MCP server, a real API. Evals: `tests/evals/<name>/`, scenarios played by ADK's simulated user (the outside user, below), never inputs the author wrote.

## The outside user

A unit test fakes the model and pins a behaviour; it cannot test phrasing, because the fake answers whatever the test author wrote. An eval calls the model and measures a score over a set. An agent with no evals has no way to tell a refactor from a regression; the first ticket in an ADK repo with none is "write the evals for what exists", and `adk-migrate` insists on it.

The author of an agent knows the happy path and the words that make it work; a user does not, and a model playing the user is cooperative by default (the sources are in `docs/research/outside-user.md` of `fbhadha/py-dev`). So an agent's inputs are never written in the session that built it. ADK plays the user: an eval case carries a `conversation_scenario` (`starting_prompt`, the fixed first message; `conversation_plan`, what the user wants and what they only say when asked; `user_persona`) instead of a static `conversation`, and its simulated user writes every later turn from the plan and the persona, seeing nothing of the agent but its replies. In `google/adk-python` since 1.18.0, personas since 1.26.0: the docs page Evaluate, User simulation, and the sample under `contributing/samples/evaluation/user_simulation/`. Google's four skills carry no eval reference, so this section names the docs itself.

- **Targets**, written by `py-build` with the ticket in view: `tests/evals/<name>/targets-<ticket>.md`, `<name>` being the agent's folder under `entrypoints/agents/`. The agent's `description` verbatim under a `Public description` heading, its `app_name`, the path of this pack's `references/personas.json`, then one row per `eval` row of the ticket: what the user wants in plain words, what they do not know or get wrong, the decided outcome as one rubric sentence, a persona id. No quoted user sentence anywhere in it.
- **Scenarios**, written by the `py-eval` agent, which sees the targets file and nothing else: `<ticket>.test.json`, an `EvalSet` whose cases each carry a scenario, the `session_input` and one rubric (`type` `FINAL_RESPONSE_QUALITY`, the row's outcome); `test_config.json` beside it.
- **Personas**: `references/personas.json`, six `UserPersona` objects that change how the user talks and never what they want: `PLAIN` (everyday words, never the product's terms), `VAGUE` (a loose goal, one detail at a time when asked), `HURRIED` (terse, impatient), `SCEPTICAL` (a confirmation before anything changes; challenges what does not fit), `WANDERER` (one unrelated question mid-way), `CHANGER` (one detail changed after a confirmation). ADK's own `EXPERT` is the control; its `NOVICE` and `EVALUATOR` are cooperative by construction. Never a persona written for one ticket: free text is where the author's wording comes back.
- **Judges that need only `GOOGLE_API_KEY`**: `hallucinations_v1`; `per_turn_user_simulator_quality_v1`, whether the simulated user kept to the plan and the persona (a simulated user errs in a third to a half of turns in published benchmarks, so a low score there is a rerun, never a verdict on the agent); `rubric_based_final_response_quality_v1` with each case's rubric. `safety_v1` and the `multi_turn_*` judges need a Vertex project.
- **The wrapper**, `tests/evals/<name>/test_outside_user.py`, marked `eval`: `await AgentEvaluator.evaluate(agent_module="src/<package>/entrypoints/agents/<name>", eval_dataset_file_path_or_dir="tests/evals/<name>", num_runs=1)` (`from google.adk.evaluation.agent_evaluator import AgentEvaluator`). It reads every `*.test.json` and the `test_config.json` beside them and fails on any case under its threshold. `uv run pytest -m eval tests/evals/<name>` runs it.
- **The report**, `tests/evals/<name>/reports/<ticket>.md`, committed: `agent:` (the package path), `commit:` (the HEAD the eval ran on), `command:`, then one line per case: pass or fail, the rubric that failed, the simulator-quality score, what was fixed. `py-review` reads it against the ticket's `eval` rows, and `scripts/check_eval_report.py` (from the baseline) fails a pull request that changes an agent package without a report whose `commit:` is an ancestor of HEAD with no later change to that package; the run itself never enters CI.
