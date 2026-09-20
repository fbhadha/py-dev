---
name: ask-dev
description: "Decide the next step and start it. Use at session start, or when the user asks what to do next or how to begin on a repo. Reads mode, glossary, tracker and Repowise state; runs the door check."
license: Apache-2.0
metadata:
  author: fbhadha
  version: 0.1.0
  tags: [python, router, workflow]
---

# Ask dev

You don't remember every skill, so ask. This is the router over four layers: Matt Pocock's process skills, Repowise's codebase-intelligence skills, Google's ADK skills, and this plugin's craft skills. It answers one question, "what happens next?", says so in one line, and starts it.

## 1. Read the state

- `docs/agents/mode.md`. Missing means the repo is not set up: the answer is `py-intake`, nothing else.
- `CONTEXT.md`, `docs/agents/issue-tracker.md`, the Repowise section of `AGENTS.md` (health line, last-indexed commit), the `docs/howto/` listing, and any open ticket the user names.
- The door check: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/find_skill.py" --door-check`. It prints every upstream skill that is not installed and the install command. Report it; do not improvise a missing skill's behaviour.

## 2. Place the user on a flow

| The situation | Next step | Then |
|---|---|---|
| Repo not set up (no `docs/agents/mode.md`) | `py-intake` | It explores, sets the mode and tracker, installs the baseline, indexes with Repowise, orients and grills on brownfield, writes the docs. |
| An idea or feature, in a repo | `grill-with-docs` (Matt's) | Small enough for one session: `py-implement` here. Bigger: `to-spec`, then `handoff` and a fresh session; `to-tickets`, then `handoff` and a fresh session; `py-implement` one ticket per session, each ending in `py-review` and a `handoff` for the next. |
| A message that is a handoff document path | read it, then `AGENTS.md` | Continue with the skill the document suggests; never re-ask what it answers. |
| A ticket already exists | `py-implement <ticket>` | It names the shape, checks scope, builds test-first, runs `py-review`, commits. |
| A branch to review | `py-review <fixed-point>` | Standards, Spec and Craft axes, report first, fixes on request. |
| Something is broken | describe the bug; the agent reaches for `diagnosing-bugs` | It builds a red-capable loop before any theory. |
| Tests you don't trust | `py-test-audit tests/` | Classifies every test; proposes deletions and rewrites at the right seam. |
| "Where is this repo ugly?" | `py-health` | Repowise health, dead code, doc drift and the mutation score in one report, then `improve-codebase-architecture` (Matt's) on the worst file. |
| "Why is this built this way?" | describe the file; the agent reaches for `architectural-decisions` (Repowise) | ADRs, `# WHY:` comments and commit archaeology for that path. |
| A decision was just made in conversation | write the ADR from `docs/adr/` template, then `scripts/adr_sync.py` | The only way a decision is recorded. |
| Working on an ADK agent | `adk-build` | Google's ADK skills with this plugin's baseline applied. |
| ADK 1.x patterns found at intake | `adk-migrate` | Detects all, forces what breaks on 2.x, tickets the rest as `later`. |
| Too big and foggy for one session | `wayfinder` (Matt's) | A map of decision tickets; merges back at `to-spec`. |
| Issues arriving from other people | `triage` (Matt's) | Only for work you did not create. |
| Mid merge conflict | `resolving-merge-conflicts` (Matt's, model-invoked) | Resolves by intent, never aborts. |
| A step only a human can do (credentials, dashboards) | `wizard` (Matt's, model-invoked) | Generates the walkthrough script. |
| The last message didn't land | `wait-what` (Matt's) | Re-pitched in plain English with the glossary's words. |
| Review the "not now" list | `py-intake later` | Shows the `later` tickets and asks what to kill. |

Skills marked "Matt's" come from `mattpocock-skills`; those marked "Repowise" from the `repowise` plugin. Model-invoked skills run through the Skill tool. Matt's user-invoked ones (`grill-with-docs`, `to-spec`, `to-tickets`, `implement`, `improve-codebase-architecture`, `setup-matt-pocock-skills`, `triage`, `wayfinder`, `wait-what`) the Skill tool refuses: run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/find_skill.py" <name>`, read the `SKILL.md` it prints, and follow it here as if invoked. The user never types a skill name.

## 3. Answer, then go

One line in this shape, then start the step in the same turn:

```
Next: <the step, in plain words, naming the skill in parentheses>
Why: <one sentence, plain English, using the repo's own words>
First I need: <the first thing it needs from you, or "nothing"; then the first question>
```

If the user's situation matches nothing above, say so and start `grill-with-docs`, because an unmatched situation is an unexamined one. The only step that waits for a word from the user is a one-way door (see the persona's ask-first list); everything else starts.
