# 8. The persona is written once and rendered per harness

## Status

Accepted

## Context

Two harnesses load this plugin and each reads an agent file in its own shape: Claude Code from `agents/<name>.md`, Copilot CLI from `com.github.copilot/agents/<name>.agent.md` with different frontmatter keys. The persona changes often (11 commits to the hooks and 8 to the plugin check in 90 days track it), and a hand-maintained second copy drifted in 0.10.x: the smoke test found the wrong agent id in one harness's copy.

## Decision

`agents/*.md` is the only hand-written copy of each agent. `scripts/render_agents.py` generates the Copilot files from it, and `scripts/check_plugin.py` fails CI when a rendered copy is stale. Nobody edits `com.github.copilot/agents/` by hand.

## Scope

- agents/
- com.github.copilot/agents/
- scripts/render_agents.py

## Consequences

One place to change the persona; a harness's quirks live in the renderer, not in the prose. A third harness costs a renderer branch, not a third copy. Revisit if a harness needs content the source cannot carry, which would force per-harness prose.

<!-- Date: 2026-09-25. Recorded at intake, from the orientation grill. -->
