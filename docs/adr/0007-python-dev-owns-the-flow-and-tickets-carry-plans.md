# 7. python-dev owns the flow from idea to tickets, and every ticket carries its plan

## Status

Accepted (2026-09-23). Supersedes ADR 0004 for the spec, the tickets, the build loop and the handoff; ADR 0004 still governs every other upstream skill.

## Context

The first live test on GitHub Copilot, on 0.10.0, felt like the default agent: no view, no pushback, no grill, no tickets, nothing explained. Part of that was packaging (the wrong agent id in the docs, hooks running in the plugin's folder); three parts were the design in this repo:

1. The flow ran through Matt Pocock's user-invoked skills (`grill-with-docs`, `to-spec`, `to-tickets`, `implement`, `handoff`). Only a person typing their names can start them, Copilot hides them from the model, and the persona reached them through a script path that is empty in the model's shell on Copilot.
2. His `to-spec` and `to-tickets` leave out file paths and code by design ("they go stale fast"); his tickets describe behaviour, "not a layer-by-layer implementation list"; the order of work comes only from blocking edges. The user asked for exactly that: what to build, where, how, and in what order, the way a senior engineer hands work over.
3. The persona forced a new session after the spec and again after the tickets, against his own advice to keep grilling, spec and tickets in one context, and its voice rules allowed one sentence of explanation per step.

## Decision

python-dev runs the flow itself.

- `py-shape`: read the code, then the agent's view (the premise, what to build and what not, rejected alternatives, risks, size), the grill in rounds with a recommended answer per question, the spec from `references/spec.md`, the breakdown approved as a table, the tickets from `references/ticket.md`, all in one session; plus a revision route and a quick-ticket route.
- Every ticket carries a plan: the files, the signatures, the tests in the order they get written with their seams and where each expected value comes from, the commands.
- `py-build` checks the plan against the code, shows it, waits for a go, and builds one slice at a time.
- The spec stays at the level of modules, types and interfaces, where the rule against file paths is right; exact paths live in the tickets, which are checked again when picked up.
- His model-invoked skills (`domain-modeling`, `tdd`, `code-review`, `diagnosing-bugs`, `research`, `prototype`, `wizard`) stay the disciplines inside the flow, called by name.
- The persona's loop (say what kind of message it is; no ticket, no code) is backed by a hook that asks before an edit to product code off a ticket branch, in repos intake set up.

## Consequences

We maintain the flow's steps and two templates, and we no longer receive his changes to spec and ticket writing; the door check stops requiring those five skills. The persona grows to about 12,000 characters, with the ceiling at 14,000. A plan can go stale when an earlier ticket moves a file; `py-build`'s check catches it before any code. The edit guard asks on every product edit off a ticket branch, which the default agent never does; a user who wants an unticketed edit states the override, or sets `PYTHON_DEV_GUARD=off` in their own shell.

## Scope

- agents/python-dev.md
- skills/py-shape/
- skills/py-build/
- scripts/hooks/guard_edit.py
- upstream.json
