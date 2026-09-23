# Spec template

A spec says what we are building and why, and the design at the level of modules, types and interfaces: stable enough to survive the first ticket landing. Exact files and line-level steps belong in the tickets, which are re-checked against the code when each is picked up. Fill every section; a section with nothing to say gets one line saying so. Written in the repo's words from `CONTEXT.md`.

```markdown
# Spec: <name>

Shape: <the how-to it follows, or "new shape: see ADR NNNN"> · Tickets: <filled in once cut>

## Problem

What hurts today, for whom, in the user's words. Why now.

## Decision

What we will build, in two to five sentences, and what we will not. The view the grill settled on.

## Behaviours

Numbered; each one testable and visible to a user or a test.

1. When <situation>, <who> gets <outcome>.

## Design

- **Where it fits**: the shape and its how-to; the layers it touches (domain, application, ports, adapters, entrypoints); the modules it adds or changes, by module name (`<package>.adapters.jira`).
- **Data**: every new or changed type: its name from `CONTEXT.md`, its fields with types, its invariants, and the adapter where outside data is parsed into it.
- **Interfaces**: every new or changed public function, Protocol, CLI command or API route, with its signature and the errors it raises.
- **Flow**: one run, step by step, from the entrypoint to the output.
- **Failure**: what can go wrong at each boundary and what happens then: retry (how often, with what backoff), reject, quarantine, or fail loudly.
- **Config and secrets**: new settings and keys, their defaults, and the `.env.example` lines.
- **Operations**: what is logged, what is counted, how a person can tell a run worked.

## Tests

For each behaviour: the seam it is tested at, the tier (unit, integration, eval), the in-memory adapter it uses, and where its expected value comes from (this spec, a worked example, a fixture). Nothing is tested through a mock of our own code.

## Order of work

The tickets in order, one line each, and the rule from `py-design`'s `references/planning.md` that set the order (walking skeleton, riskiest next, prefactor first, expand then migrate then contract).

## Alternatives rejected

One line each: the option, and why not.

## Risks and one-way doors

Each risk with its mitigation. Each one-way door with the ADR that records the decision.

## Out of scope

What this spec will not do, and where each item went (a `later` ticket, or never).

## Revisions

Dated lines, newest last: what changed and why. Empty until the first revision.
```
