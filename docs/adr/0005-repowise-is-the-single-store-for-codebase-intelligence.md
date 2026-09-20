# 5. Repowise is the single store for codebase intelligence

## Status

Accepted

## Context

The agent needs to know a repo's structure, history, risk, health, dead code and decisions, and it needs one place to read each of those from and one place to write each of them to. Before this decision the design had two of several: a hand-written orientation page beside Repowise's structural wiki, a `docs/health/` folder beside Repowise's health history, ADRs beside Repowise's decision store, and an architecture document that repeated the import graph.

Verified on Repowise 0.52.0 (`docs/research/repowise.md`): the index builds in seconds with no model, it reads committed ADRs in Nygard format as accepted decisions, it re-extracts ADRs on `init` but not on `update`, and an ADR binds to files only through `repowise decision confirm --scope`.

## Decision

For every kind of codebase intelligence there is one read path and one write path, and the agent uses no other.

| Kind | Written by | Read by the agent |
|---|---|---|
| Structure, entry points, callers, ownership, hotspots | Repowise index (`repowise init`, `update`) | `get_overview`, `get_context`, `get_symbol`, `search_codebase` through the `codebase-exploration` skill; `repowise context` / `search` on a harness without MCP |
| Blast radius before an edit | Repowise index | `get_risk` through the `pre-modification-check` skill |
| Why the code is shaped this way | ADR files in `docs/adr/` (Nygard headings, `## Status` Accepted, `## Scope` listing the paths it governs); `# WHY:` comments in code | `get_why` through the `architectural-decisions` skill; `repowise why` |
| Health score, worst files, refactoring targets, trend | Repowise index; coverage from `coverage.lcov` via `repowise coverage add` | `get_health` through the `code-health` skill; `repowise health` |
| Duplication, dead code | Repowise index | `get_dead_code` through the `dead-code-cleanup` skill |
| What a change put at risk, which tests it touches | Repowise index | `get_change_risk`, `impacted-tests` through the `change-review` skill; the CI gate `scripts/repowise_gate.py` |
| Whether the docs still match the tree | Repowise index | `repowise doc-drift` in `py-health` |
| Vocabulary | `CONTEXT.md`, by grilling | Read at session start |
| Rules the checks enforce | `pyproject.toml` tool tables | Linters; `docs/architecture.md` explains them |
| Tickets and scope | The tracker named in `docs/agents/issue-tracker.md` | Matt Pocock's ticket skills |

Consequences of the table:

- `docs/health/`, the orientation page, and the `py-orient` skill are gone. Brownfield orientation is `repowise init` followed by reading the overview, the health report, the dead-code report and the decision candidates, then grilling the user on what those surfaced.
- `docs/architecture.md` states the layering rules and the composition root only. The live map is Repowise.
- The agent never calls `repowise decision add`. A decision is an ADR file. `scripts/adr_sync.py` re-indexes and binds each accepted ADR to its `## Scope` paths so Repowise can push it back at the agent when it edits a governed file. `.repowise/` stays gitignored; the ADR files are the shared truth.
- `AGENTS.md` carries the plugin's pointers above the Repowise managed section, which `repowise generate-claude-md --output AGENTS.md` maintains between its markers. `CLAUDE.md` is `@AGENTS.md`.
- The Repowise plugin is a prerequisite beside Matt Pocock's, checked at the door with its six skill names. The plugin's own skills are not re-described here; ours call them.

## Consequences

One place to look, one place to write, for every kind of knowledge. A junior reader learns one map. The cost: Repowise (AGPL-3.0, Python 3.11 or newer) becomes a hard dependency of the agent's orientation and review flows, and when it is missing those flows degrade to reading files by hand and say so.
