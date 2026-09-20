# Architecture

The rules only. The live map (modules, callers, entry points, hotspots) is Repowise: `get_overview()` from an agent, `uv run repowise serve` for the dashboard, or the managed section at the bottom of `AGENTS.md`. Nothing here repeats what the index can answer.

## Layers

Top to bottom. An arrow means "may import". The import-linter contract in `pyproject.toml` enforces this; when the two disagree, the contract is the truth and this file is out of date.

```
entrypoints   (CLI, HTTP, schedulers, ADK agents)   -> application, adapters, domain
application   (use cases, the transaction boundary) -> domain, ports
adapters      (one module per external system)      -> domain, ports
domain        (entities, value objects, rules)      -> nothing in this repo
```

## The shape most work takes

Source adapter -> normalised domain record -> sink adapter. Every source produces the same domain shape; every sink consumes it. A new source or sink is one new module, not a change to the others. The how-tos in `docs/howto/` are the recipes.

## Composition root

`src/{{PACKAGE}}/entrypoints/bootstrap.py` is the one place real adapters are wired to the application. Tests wire in-memory adapters there. Nothing else constructs an adapter.

## Decisions

`docs/adr/`. Each ADR names the paths it governs under `## Scope`; Repowise binds them and `repowise why <path>` shows which decisions apply to a file.
