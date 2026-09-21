# Packs: what was verified, against what

Verified 2026-09-21. Every library claim in `skills/pack-adk`, `skills/adk-migrate`, `skills/pack-data-engineering` and `skills/py-design/references/canonical-examples.md` was checked against the source named below, by fetching the file. Re-verify when `upstream.json` moves the ADK pin or when a pack cites a new path.

## Google ADK (`google/adk-python` at `d57c84f13baf53cfd910c2155449f8c4254e01c5`, 2.9.0)

| Claim | Where it is checked |
|---|---|
| Node inputs, outputs, `output_schema` and state are Pydantic models, never `dict[str, Any]` | `.agents/skills/adk-agent-builder/references/best-practices.md`, first rule |
| State is written through `Event(state=...)`, never `ctx.state[key] = ...`; reading is `ctx.state[...]` | same file, "Write state through `Event(state=...)`" |
| At most one output event per node; a function yields or returns, never both | same file, the two headings |
| `{var}` in an instruction reads state; `{node_input}` is a `KeyError` | same file, last rule |
| `SequentialAgent`, `ParallelAgent`, `LoopAgent` deprecated in favour of `Workflow`; the one thing they still do is model-driven transfer under an `LlmAgent` | `references/multi-agent.md`, the "Deprecated" note; `src/google/adk/agents/sequential_agent.py` line 89 `@deprecated` |
| `BaseAgent.from_config` and `_parse_config` deprecated | `src/google/adk/agents/base_agent.py` lines 724 and 771 |
| `_run_async_impl` and `_run_live_impl` are the overridable run loops | `base_agent.py` lines 425 and 441 |
| `InMemoryRunner` exists; tests use `pytest-asyncio` with `asyncio_mode = "auto"` | `src/google/adk/runners.py` line 2219; `references/testing.md` lines 9 to 17 |
| Entrypoint layout: `__init__.py` does `from . import agent`, `agent.py` defines `root_agent`, `.env` beside it | `references/getting-started.md` lines 28 and 63 to 72 |
| The four skills we install exist; the install command selects them | `scripts/check_upstream_skills.py`, run at the pinned commit (CI) |

Not verified: how many other skills the directory holds (the GitHub tree listing is not reachable from the sandbox). The pack says "the other skills" and names none.

## dlt (`dlt-hub/dlt`, `devel` branch)

Every path the pack and `canonical-examples.md` cite exists: `dlt/extract/{source,resource,extract}.py`, `dlt/normalize/normalize.py`, `dlt/normalize/items_normalizers/`, `dlt/load/load.py`, `dlt/common/destination/{reference,client,capabilities}.py`, `dlt/destinations/impl/`, `dlt/sources/`.

## requests (`psf/requests`, `main`) and Architecture Patterns with Python (`cosmicpython/code`, `master`)

`src/requests/{api,sessions,adapters}.py` exist. All thirteen `src/allocation/` paths cited exist (`domain/`, `service_layer/`, `adapters/`, `entrypoints/`, `bootstrap.py`).

## ruff rules the packs turn on or cite

`PD` (pandas-vet), `NPY`, `S608`, `B901`, `BLE001`, `TID251`, `D401`, `TD002`, `FIX002`, `ERA001` all resolve with `ruff rule <code>` on ruff 0.16.
