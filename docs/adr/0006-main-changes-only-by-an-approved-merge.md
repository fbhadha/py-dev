# `main` changes only by a merge the user said yes to

## Status

Accepted (2026-09-21). Supersedes the per-file guard of 0.6.0 to 0.7.0 (design decisions 36 and 37).

## Context

The user's rule is that nothing in their repo changes without their yes. Versions 0.6.0 to 0.7.0 enforced it per file: a pre-tool `ask` on every edit to a protected file, a post-tool recorder, a snapshot to attribute what shell commands changed, a stop gate on unapproved changes, a commit-msg gate needing `approved: <files>`, and three modes to tune how often it asked. It blocked intake twice, needed a heuristic for every writing command, and still asked at the wrong moment: while building a ticket that the user had already grilled, specified and ticketed.

## Decision

Work happens on a branch. `main` changes only by a merge the user approves after seeing the diff summary, the commits and the check results. The plugin's command hook asks before anything that lands on `main` (a commit while it is checked out, a merge into it, a push to it, merging a pull request from the CLI) and denies destructive git; nothing watches individual files. Branch protection on the server, offered at the end of intake, holds the same rule for every tool and person. Merges keep the branch's commits, because Repowise reads that history.

## Consequences

One prompt per ticket instead of one per file, and the prompt comes with the whole change in front of the user. The hooks shrink to two small scripts and a status line. A change to packaging, CI or the docs can hide inside a ticket's diff, so the merge summary lists files outside `src/` and `tests/` first with a sentence each. A repo whose default branch is not `main`, `master` or `trunk` is not guarded by the hook until the list in `scripts/hooks/_common.py` is extended.

## Scope

- scripts/hooks/
- skills/py-intake/SKILL.md
- agents/python-dev.md
