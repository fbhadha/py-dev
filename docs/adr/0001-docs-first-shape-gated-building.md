# Docs first: a shape gates whether the agent may build without an interview

## Decision

Every repo the agent works in carries how-to docs, one per **shape** (a kind of addition the repo already knows how to make), each naming the layers and folders that shape touches and mirroring a compiling example. A ticket that stays inside a how-to's named layers is built by template after one confirmation ("this looks like adding another X, correct?"). A ticket that touches anything outside them is a new shape: the interview is mandatory, the how-to is written or extended before any code, and the build follows the edited how-to. We chose the mechanical trigger over the agent's own judgement because agents drift toward "yes, this matches" so they can start building (arXiv 2605.29442), and we chose docs-before-code over docs-after because a doc written after the build lags the code it describes from day one. The cost is an occasional interview about something small that spilled over one folder.

## Status

Accepted

## Scope

- skills/py-shape/
- skills/py-build/
- skills/py-baseline/templates/howto-template.md
