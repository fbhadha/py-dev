---
name: py-shape
description: "Shape an idea before any ticket exists: the grill, a research note for a fact from outside the repo, a prototype for a question talking cannot settle, a wayfinder map when it is more than one session. Ends as one ticket or a spec. Use for an idea, a feature, a new project, or a map with open tickets."
---

# Shaping an idea

Everything new starts here and leaves as a ticket. Shaping decides; it never builds. Its products are terms in `CONTEXT.md`, ADRs, research notes in `docs/research/`, prototype branches and, when the shape is new, the how-to in `docs/howto/`. Product code is a ticket's work (Skill `py-build`). Session count decides the route, not project size.

Voice as the persona says: one sentence before a step on what and why, one after on what changed; questions one at a time, each with your recommended answer and its cost.

## 1. Branch

`git fetch origin && git switch -c shaping/<two-word-slug> origin/main` (no remote: `main`). Commit what settles as it settles, one decision per commit, the decision in the message. A map names its branch in its Notes: `git switch` to it and `git merge origin/main`. The hook asks before a commit on a shaping branch that carries `src/` or `tests/`; the answer is a prototype branch or a ticket, unless the user asked for the code in their own words.

## 2. Grill

File `grill-with-docs`. Open `CONTEXT.md` first and use its words. Two detours while it runs; each ends back at the question that sent you out.

**A fact outside the repo blocks a decision** (a library, an API, a spec, a version): Skill `research`, as one background subagent told to do the reading itself and spawn nothing (a second agent is his skill's known bug). It writes `docs/research/<slug>.md`, dated on its first line, one citation per claim; you keep grilling. A note is a fact on a date; the decision it feeds becomes an ADR or a term, which is what later sessions read.

**Talking cannot settle it** (how a state model feels, how a library or a data shape behaves when run): Skill `prototype`.

- `git switch -c prototype/<slug>`; the code goes under `prototypes/`, which the code checks skip (detect-secrets still reads it).
- A state model the user must feel: his single HTML file. They click; no Python needed.
- A library, an API or a data shape you must run: a throwaway script. `uv run` it and show the state after every step.
- The user picks; never pick for them. Commit the prototype there, never merge it, switch back, and record the answer as the decision (an ADR or a term) with a pointer to the branch. `main` keeps the decision only.
- A long grill first hands off (the persona's session boundaries) and prototypes in a fresh session, so the prototype's context stays out of the grill's.

## 3. Fog

When the grill turns up questions you cannot yet phrase sharply, more than one session's worth (a new project, a feature across many sessions): stop grilling and File `wayfinder` to chart the map on the tracker in `docs/agents/issue-tracker.md` (its "Wayfinding operations" section has the commands). Write the shaping branch into the map's Notes. Charting is that session's whole work; hand off.

Every session after works one ticket from the frontier, by its type: grilling (Skill `grilling`, then Skill `domain-modeling`); a prototype or research as in the grill above; a task. Research tickets run in parallel as subagents. A ticket that reads "build the X" is mis-typed: retype it as the question behind it, or rule it out of scope. Resolve it, close it, append the decision to the map, hand off.

When the map clears, File `to-spec` on the map itself, never `implement`.

## 4. Size the exit

- **No fog, and it fits one session**: File `to-tickets` for the one ticket, so the fence (acceptance criteria, out of scope) exists. `git branch -m ticket/<id>-<two-word-slug>`, then Skill `py-build` in this session.
- **Bigger**: land the shaping branch by `py-build`'s landing steps (push, the merge summary, "merge to main?"), so the spec and every ticket session read the decisions from `main`. Then File `to-spec` and hand off. The next session runs `to-tickets` and hands off; each ticket is then one session of `py-build`.
