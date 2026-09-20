---
name: adk-migrate
description: "Move a Google ADK 1.x codebase to 2.x: detect every 1.x pattern mechanically, force only what silently breaks, evals first, tickets as expand, migrate, contract. Use when py-intake or pack-adk finds 1.x."
---

# ADK migrate

ADK 2.x replaced the 1.x orchestration classes with a graph runtime: `Workflow` schedules nodes along declared edges, `BaseAgent` is a node, state travels in events. The old shells still import and run in 2.x, so a repo can upgrade the dependency and look fine while its state writes vanish on replay. This skill separates what must change from what merely should. Guide voice: each pattern gets one plain sentence on what it did in 1.x and what replaces it.

The facts here come from Google's `adk-agent-builder` references (`multi-agent.md`, `best-practices.md`, `state-and-events.md`, `advanced-patterns.md`) and the installed package's source. Open them (`find_skill.py adk-agent-builder`) before rewriting anything; the references name the exact replacement.

## 1. Detect (mechanical, whole repo)

Run every search and present one table: pattern, count, files. Nothing is guessed.

| Pattern | Search | Class |
|---|---|---|
| Deprecated orchestration shells | `rg -n "SequentialAgent|ParallelAgent|LoopAgent" src` | later, unless nested inside something forced |
| Custom agent subclass overriding the run loop | `rg -n "_run_async_impl|_run_live_impl" src` | forced when it mutates state or appends events; later otherwise |
| Config-driven agents | `rg -n "AgentConfig|BaseAgentConfig|from_config|_parse_config" src` | later (deprecated with warnings in 2.x source) |
| Direct event appends | `rg -n "session\.events\.append|\.events\.append\(" src` | forced |
| Direct state writes | `rg -n "ctx\.state\[[^]]+\]\s*=|\.state\[[^]]+\]\s*=" src` | forced |
| Broad except inside a tool | ruff `BLE001` on `src/**/tools/`; `rg -n "except Exception|except:" src/**/tools` | forced |
| Untyped node edges | `rg -n "dict\[str, Any\]" src/**/agents src/**/tools` | later |
| Instruction reading the input as a placeholder | `rg -n "\{node_input\}" src` | forced |
| yield and return in one node function | ruff `B901`; `rg -n "return Event" src` in generator functions | forced |
| Custom session or state tables | `rg -n "BaseSessionService|create_table|CREATE TABLE" src` | forced when the schema is rigid; the 2.x session service owns the schema |

Also record the installed version (`uv pip show google-adk`) and the target (`>=2.0`, the newest 2.x on PyPI unless the user pins).

## 2. Force only what silently breaks

Push hard, in the persona's second tier, on the rows marked forced: each is a behaviour that runs without error on 2.x and produces the wrong result (state lost on replay, output swallowed, a failure hidden from the runtime and the user). The user may not override these into `later` without saying, in their own words, that they accept silent data loss on those paths; write that into the ticket if they do.

Everything marked later becomes a `later` ticket, one per pattern family, with the file list in the body. The deprecated shells keep working; Google's `multi-agent.md` says the one thing they still do that `Workflow` cannot (a `Workflow` as a sub-agent of an `LlmAgent` for model-driven transfer), so a shell used that way is not even a later.

## 3. Evals first

A migration without a way to tell a regression from a refactor is a rewrite. Before any code changes:

1. `tests/evals/` exists with at least one eval per agent that exercises today's behaviour on 1.x, marked `eval`, runnable on demand. If none exist, "write the evals" is the first ticket and nothing else starts until it is green.
2. Record the eval scores at 1.x in the ticket.

## 4. Tickets as expand, migrate, contract

Open Matt Pocock's `to-tickets` (via `find_skill.py`, read and follow) with this structure already decided, so it only quizzes the user on granularity:

1. **Expand.** Add `google-adk>=2.0` beside the current pin only if both can coexist; otherwise the upgrade is the first migrate ticket and the evals are its gate. Add the 2.x shapes beside the old: the `Workflow` next to the `SequentialAgent`, the `Event(state=...)` writes next to the `ctx.state` writes, feature-flagged at the composition root.
2. **Migrate.** One ticket per forced row, one agent per ticket, each green on the evals before the next. Rewrite by the Google reference for that pattern, through the persona's build steps (Matt Pocock's `implement`, test first at the `InMemoryRunner` seam).
3. **Contract.** Delete the 1.x forms once no caller remains; one ticket blocked by every migrate ticket. The `later` families stay open with their file lists.

Each ticket names the eval it must keep green and the Google reference it follows.

## 5. Finish

Evals at 2.x equal or better than the recorded 1.x scores; `uv run pytest -m "not eval"` green; the change gate green; an ADR "ADK 2.x: state through events" from the template with `## Scope` on the agent packages, then `scripts/adr_sync.py`. Hand off between tickets as the persona does.
