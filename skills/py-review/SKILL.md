---
name: py-review
description: "Review a diff since a fixed point on four axes and report before fixing: Standards and Spec (Matt Pocock's code-review), Change (Repowise), Craft (py-reviewer). Use for a branch, PR, MR or work in progress."
license: Apache-2.0
metadata:
  author: fbhadha
  version: 0.1.0
  tags: [python, review, code-review, repowise]
---

# Python review

Four axes, reported separately, never re-ranked against each other. Report first; fix only on request. In guide mode every finding carries one sentence on why it matters to this repo, in the repo's own words.

## 1. Pin the fixed point

The commit, branch, tag or merge-base the user names; `origin/main` when they name nothing and the branch has one; ask otherwise. `git rev-parse <fixed-point>` must resolve and `git diff <fixed-point>...HEAD --stat` must be non-empty before anything else runs.

## 2. Standards and Spec

Call the Skill tool with "code-review" and pass it the fixed point. It runs its two sub-agents and reports `## Standards` and `## Spec`. Keep its output as it is. Its Standards axis already skips what tooling enforces; so does everything below.

## 3. Change (Repowise)

Call the Skill tool with "change-review" for the range (`get_change_risk(revspec="<fixed-point>..HEAD")`, then `get_risk` in PR mode on the changed files). Without MCP:

```bash
uv run repowise update
uv run python scripts/repowise_gate.py <fixed-point>..HEAD    # findings the diff introduced
uv run repowise risk <fixed-point>..HEAD                       # fix history, review priority
uv run repowise impacted-tests <fixed-point>..HEAD             # tests that guard the change
```

Report under `## Change`: every finding the change introduced or worsened (file, marker, plain-words meaning), the files with prior fix history, co-change partners the diff did not touch, and tests that guard the change but did not run. A gate finding is 🔴.

## 4. Craft

Dispatch the `py-reviewer` agent with the diff command and the fixed point. It reads the changed files in full, applies `py-design` and its fault catalogue, and reports 🔴 🟠 🟡 with file, line, fault name, why, and fix. It never edits and never spawns. On a harness without subagents, follow `agents/py-reviewer.md` yourself in a new section after finishing the three axes above, so its judgement is not coloured by them.

Add to Craft, from the diff of `tests/` alone: any assertion loosened, test deleted, `skip` or `xfail` added, or expected value now computed the way the code computes it. Each is 🔴 unless the ticket records an explicit override in the user's words.

## 5. Report

```
## Standards      (Matt Pocock's code-review)
## Spec           (Matt Pocock's code-review)
## Change         (Repowise)
## Craft          (py-reviewer, fault catalogue)
```

End with one line per axis: count and worst finding. No overall verdict, no cross-axis ranking; the axes are separate so that one cannot mask another.

Then ask: "Fix the 🔴 now?" Fixes go through `py-implement`'s slice rules (tests read-only, checks after each change) and end with this review run again against the same fixed point.
