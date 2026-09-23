---
name: py-design
description: "Python craft reference: the design rules, the order to build things in, the edges (timeouts, retries, parsing, errors, config, logs, contract tests), the fault catalogue, three canonical repos to cite. Use when designing a module, class, function or layout, placing a seam or Protocol, ordering tickets or a ticket's plan, or reviewing Python."
---

# Python design

A reference, not a process. Consult it while designing or reviewing; do not run it as a session.

For the vocabulary (**module**, **interface**, **depth**, **seam**, **adapter**, **leverage**, **locality**) call the Skill tool with "codebase-design" and use those words exactly. This file is their Python translation, plus the rules that decide what shape a piece of Python takes.

## The shape of a repo

The live map of any real repo is Repowise (`uv run repowise context <file>`); this is the target layout a new repo gets and an old one moves toward.

```
src/<package>/
  __init__.py          # explicit __all__: the public surface, nothing else
  domain.py            # entities, value objects, rules; imports nothing below this line
  application.py       # use cases and orchestration; imports domain and ports
  ports.py             # Protocols the application needs: Source, Sink, Clock, Repository
  adapters/            # one module per external system, each satisfying one port
  entrypoints/         # CLI, agent, API; the one place things are constructed
tests/
  unit/                # domain and application through their public surface, no I/O
  integration/         # adapters against a real or local-substitutable backend
  evals/               # agent evals, run on demand, never in the commit gate
```

Names come from `CONTEXT.md`. The layering is enforced by import-linter, not requested: `entrypoints` may import anything, `adapters` may import `domain` and `ports`, `application` may import `domain` and `ports`, `domain` imports nothing of ours.

## Rules

1. **A class earns its place** when it owns state across calls, satisfies a Protocol at a seam, or is a value object. Otherwise write a function. Data is a frozen `dataclass` or a Pydantic model; behaviour at a seam is a Protocol; transformation is a function.
2. **Parse at the edge, trust inside.** External data becomes a typed model in the adapter that received it. Domain code never sees a raw `dict`, a DataFrame, or a JSON string.
3. **Accept dependencies, return results.** Constructors take their ports as keyword arguments. Functions return values instead of mutating what they were given.
4. **Ports are Protocols. Two adapters justify a seam.** A `Source` Protocol exists because there is a `JiraSource` and an `InMemorySource`, and both pass one contract suite (`references/boundaries.md`). One adapter means the seam is hypothetical: inline it.
5. **Composition over inheritance.** Subclass only for a real is-a where every method of the parent still makes sense on the child. Reuse by passing collaborators in, the way `logging.Logger` takes handlers and filters.
6. **Exceptions are interface.** Each package defines a small hierarchy; each public function says what it raises; callers catch the specific type or let it propagate. Never `except Exception: pass`, never `except: return None`. In an ADK tool, a broad except also disables the framework's retry and human-in-the-loop machinery.
7. **Signatures that cannot be misread.** Keyword-only (`*`) after the first parameter whenever two parameters share a type. No boolean flag parameters; two functions or an enum instead. No mutable defaults. `X | None` only when absence means something; say what.
8. **Modules are inert on import.** No client is constructed, no file is read, no logging is configured at import time. Configuration is one `pydantic-settings` class read once at the entrypoint, so a missing variable fails before any work starts and names itself. Log with `logging.getLogger(__name__)`; never `print`.
9. **Small public surface.** `__all__` in every package `__init__`; a leading underscore on everything else; no barrel that re-exports a subtree. Several small entry points beat one giant one.
10. **Search before you write.** Before adding a function or a type, search `CONTEXT.md` for the term and the index for the name (`uv run repowise search <name>`). A second `normalize_date` because the first was not in context is the most common duplication.
11. **No grab bags.** No directory or module named `utils`, `helpers`, `common`, `misc`. A function belongs to the domain concept it serves; if it serves none, it does not belong.
12. **Comments say why.** A comment states something the code cannot: the constraint, the reason, the gotcha. A docstring states the contract when it is subtle (invariants, ordering, errors); it never restates the signature. A comment that reads like an instruction to a model is a defect.
13. **The deletion test.** Before adding a layer, imagine deleting it. If the callers would simply call the next thing down with the same arguments, it was a pass-through.

## Planning the work

What to build first and in what order, between tickets and inside one; what every step of a plan names; one-way and two-way doors; sizing: [references/planning.md](references/planning.md). `py-shape` cuts tickets by it and `py-build` checks each plan against it.

## The edges

Timeouts, retries and idempotency on calls out; parsing at the edge into named types; money, time and identifiers; error hierarchies; configuration; logs and the run summary; async; one contract suite per port that every adapter runs: [references/boundaries.md](references/boundaries.md). Open it whenever a plan touches an adapter, an entrypoint or a port.

## The worked shape: adapter, model, writer

Most data projects are this shape: several external systems in, one common record in the middle, one writer out. The full code (Source and Sink Protocols, a frozen `Record`, two adapters, `sync()`, the composition root) is in `references/worked-example.md`; open it when writing or reviewing that shape, not otherwise.

## Tests

Call the Skill tool with "tdd" for the loop. On top of it: expected values are literals from a spec or a worked example, never computed the way the code computes them; a test with no assertion is a defect; mock only at the system boundary (the API client, the clock), never your own modules; a test of a trivial mapping mirrors the code and is deleted; agent tests fake the model, and live-model runs are evals in `tests/evals/`.

## When reviewing or explaining

- The faults to look for, each with its tell and its fix: [references/fault-catalogue.md](references/fault-catalogue.md).
- Classifying tests the user does not trust, with evidence and one action per test: [references/test-audit.md](references/test-audit.md).
- The three repos to cite by path when explaining a recommendation: [references/canonical-examples.md](references/canonical-examples.md). `requests` for depth, the *Architecture Patterns with Python* code for layering, `dlt` for the adapter-model-writer shape at scale.

In guide mode, every recommendation carries one sentence on why, in the repo's own words.
