# Context

The words this codebase uses, in the form Matt Pocock's `grilling` skill maintains. One entry per term the code, the tickets and the docs all rely on. Created lazily: the first grilling session that settles a term adds it.

## Glossary

<!-- Format, one term per entry:

### Term

One or two sentences saying what it is in this repo, and what it is not when
that is the common confusion. Name the module that owns it.

-->

### Shape

A kind of addition this repo already knows how to make: it has a how-to in `docs/howto/` and an example package the how-to mirrors. Adding another of a shape is template work. Anything else is a new shape and needs the interview.

### Junior reader

The person every file and doc is written for: reads Python, has never seen this repo, cannot ask the author. If they could not continue the work from the docs alone, the docs are not done.

### Decision

A constraint the user accepted, written as an ADR in `docs/adr/` with the paths it governs. Repowise reads the ADRs and warns whoever edits a governed path. Nothing else counts as a decision: not a comment, not a chat message, not a candidate Repowise mined from history.

## Decisions with a page of their own

See `docs/adr/`. Only decisions that were hard to reverse, contested, or surprising get one.
