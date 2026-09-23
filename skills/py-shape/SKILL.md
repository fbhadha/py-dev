---
name: py-shape
description: "Turn an idea into tickets before any code: read the code, give your view and push back, grill in rounds, write the spec, cut tickets that each carry an exact plan, all in one session. Also the revision route (a change to something already decided) and the quick-ticket route (a small, clear change). Use for any new idea, feature, project, revision or small change."
---

# Shaping an idea

Everything that changes the repo starts here and leaves as tickets on the tracker, each with a plan exact enough to build from. Shaping decides; it never builds. What it leaves behind: your view, terms in `CONTEXT.md`, ADRs, research notes in `docs/research/`, prototype branches, the how-to for a new shape, the spec and the tickets. Product code is a ticket's work (Skill `py-build`).

Voice is the persona's section 2, pushback its section 3. The user types a skill name only for `wayfinder` (section 4), which only a person can start.

## 0. Pick the route

Say which route and why, in one sentence.

- **Quick ticket** (section 6) when all four hold: it fits one session; it stays inside an existing how-to; no one-way door; nothing to decide that the user has not already said. A typo, a bumped pin, a missing test, a bug fix after `diagnosing-bugs` found the cause.
- **Revision** (section 7) when it changes a `CONTEXT.md` term, an ADR, a spec, an open ticket or behaviour already merged.
- **New idea** (sections 1 to 5): everything else.

## 1. Branch and read

`git fetch origin && git switch -c shaping/<two-word-slug> origin/main` (no remote: `main`). Commit what settles as it settles, one decision per commit, the decision in the message. A map names its branch in its Notes: `git switch` to it and `git merge origin/main`. The hook asks before product code on a shaping branch; the answer is a prototype branch or a ticket.

Read before you say anything: `CONTEXT.md`; the how-to the idea looks closest to; the code it would touch (grep, open the files); `uv run repowise risk -t <f1> -t <f2> ...` on those files and `uv run repowise why <file>` on any it marks governed; the ADRs that names. Anything you can find out, you find out; the user is asked only for decisions.

## 2. Your view

One message, before any question:

1. **The problem**, as you understand it, in the user's words and the repo's.
2. **The premise**: should this be built at all, now, this way? The cheaper thing, the thing that already exists, or the reason to wait. Said plainly, once.
3. **What you would build**: the shape (which how-to, or a new one), the layers it touches, the main pieces and how they fit, in plain words; what you would leave out and why.
4. **What you rejected**: each alternative in one line with the reason.
5. **Risks and one-way doors**: what could go wrong and what is hard to undo.
6. **How big**: one ticket, a few tickets, or more than one session of deciding.

Then the first round of questions.

## 3. Grill

Walk the decision tree one branch at a time, in rounds: at most five numbered questions per round, each with your recommended answer, the reason, and what the other answer costs. Wait for the answers. Settle a branch before opening the next; a question that depends on an unsettled one waits.

Everything the grill settles lands where it belongs as it settles: a term in `CONTEXT.md` (Skill `domain-modeling` for the wording, and for whether a decision is worth an ADR); a hard-to-reverse choice as an ADR from `docs/agents/adr-template.md`; a rejected idea in the spec's Out of scope. Challenge vague words. When the user contradicts the code, an ADR or an earlier answer, say so and quote it.

Two detours; each ends back at the question that sent you out.

**A fact from outside the repo blocks a decision** (a library, an API, a spec, a version): Skill `research`, as one background subagent told to do the reading itself and spawn nothing. It writes `docs/research/<slug>.md`, dated on its first line, one citation per claim; you keep grilling. A note is a fact on a date; the decision it feeds becomes an ADR or a term.

**Talking cannot settle it** (how a state model feels, how a library or a data shape behaves when run): Skill `prototype`.

- `git switch -c prototype/<slug>`; the code goes under `prototypes/`, which the code checks skip (detect-secrets still reads it).
- A state model the user must feel: his single HTML file. They click; no Python needed.
- A library, an API or a data shape you must run: a throwaway script. `uv run` it and show the state after every step.
- The user picks; never pick for them. Commit the prototype there, never merge it, switch back, and record the answer as the decision (an ADR or a term) with a pointer to the branch.

Stop when every branch is settled. Say what you understood in at most five lines and ask: "Is that what we are building?" Nothing is written up until the answer is yes.

## 4. Fog

When the grill turns up more open questions than one session can settle (a new project, a feature across many sessions): stop grilling. Matt's `wayfinder` charts the map, and only the user can start it (persona section 5): User types `wayfinder` with the idea in one line. It charts the map on the tracker in `docs/agents/issue-tracker.md` (its "Wayfinding operations" section has the commands); while it runs, answer its questions from what this session settled, and leave the destination and every open decision to the user. Write the shaping branch into the map's Notes. Charting is that session's whole work; hand off, and give the next session's first message: the `wayfinder` line with the map and the handoff's path.

Every map session starts with that line; one that did not: give them the line first. It works one ticket from the map's frontier, by its type: grilling (section 3 on that one question), a prototype or research as above, a task. Research tickets run in parallel as subagents. A ticket that reads "build the X" is mis-typed: retype it as the question behind it, or rule it out of scope. Resolve it, close it, append the decision to the map, hand off the same way. When the map clears, section 5 runs on the map.

## 5. Spec and tickets, in this session

The spec and the tickets are written in the session that grilled, because they are made from that conversation.

1. **One ticket** (the whole change fits one session): no spec; the ticket's Why and Plan carry it. Go to 3.
2. **The spec**: write it from `references/spec.md`. Show it whole, change what the user changes, then publish it to the tracker by the workflow in `docs/agents/issue-tracker.md`, titled `Spec: <name>`.
3. **The breakdown**: cut the work by `py-design`'s `references/planning.md` (walking skeleton first, riskiest next, prefactor before the feature, vertical slices, one session each). Show it as a table (order, title, what it proves, blocked by, size) and change it until the user approves.
4. **The tickets**: write each from `references/ticket.md`. Every file named is checked to exist or marked new; every new or changed signature is written out; the tests are listed in the order they get written, each with its seam and where its expected value comes from. Publish them blockers first, each linking the spec, labelled `ready-for-agent`, with the blocking edges the tracker file describes.
5. **Land the decisions.** One ticket: `git branch -m ticket/<id>-<two-word-slug>`, then Skill `py-build` in this session. More than one: push the shaping branch and land it by `py-build`'s landing steps (the merge summary, "Merge to main?"), so every ticket session reads the decisions from `main`; then write the handoff naming the first ticket on the frontier (persona section 6).

## 6. Quick ticket

1. Your view in two to four sentences: what you would change, why, why it is this small, and the one thing that could go wrong.
2. Write the ticket from `references/ticket.md` (a short plan, never an absent one), show it, and publish it.
3. `git switch -c ticket/<id>-<two-word-slug> origin/main` (or rename the shaping branch), then Skill `py-build` in this session.

Anything that fails one of the four tests in section 0 is a new idea: section 1.

## 7. Revision

The user changes something already decided. Mid-build: stop at the next green, commit it on the ticket branch, run this, then resume or re-plan.

1. **Name what it changes**, quoting it: "This changes ADR 0004 (`adapters never normalise`), spec line 3, and tickets #12 and #14."
2. **Your view on the change**: better or worse than what was decided, and why; what changing it costs now (tickets done, code merged, data written); what you recommend.
3. **Grill only the branch it touches**, in rounds as in section 3.
4. **Write it down before any code**: the term in `CONTEXT.md`; a new ADR that supersedes the old one (the old one's Status becomes `Superseded by NNNN`); the spec edited, with a dated line under its Revisions saying what changed and why; open tickets rewritten, obsolete ones closed with the reason, new ones created from `references/ticket.md`. Merged behaviour that must change becomes a new ticket, never an edit on `main`.
5. **Say what changed in the plan** (tickets added, closed, reordered) and what comes next.
