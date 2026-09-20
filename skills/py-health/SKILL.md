---
name: py-health
description: "One report on where the repo is ugly and what to fix first: Repowise health, dead code, doc drift, test-quality markers, linter counts, optional mutation testing. Writes nothing. Use for cleanup planning."
license: Apache-2.0
metadata:
  author: fbhadha
  version: 0.1.0
  tags: [python, health, refactoring, repowise, mutation-testing]
---

# Python health

The numeric half of orientation and the thing the mentor points at when it says "this file is the problem". Everything derived from the code comes from Repowise; the line-level counts come from the linters the baseline installs; nothing is stored anywhere but Repowise's own history (ADR 0005 in the plugin's repo). Guide voice: the first time a marker appears, one plain sentence on what it means and why it predicts bugs.

## 1. Refresh

```bash
DO_NOT_TRACK=1 uv run repowise update
uv run pytest -m "not eval" --cov --cov-report=lcov:coverage.lcov -q
uv run repowise coverage add coverage.lcov
uv run python scripts/adr_sync.py --no-index
```

Coverage is what lights up the untested-hotspot markers and makes `impacted-tests` measured instead of inferred. If the suite cannot run, say so and continue without it; the report must say "no coverage" rather than pretend.

## 2. Gather

| Source | Command | Read for |
|---|---|---|
| Whole-repo health | `uv run repowise health --refactoring-targets` (or the Skill tool with "code-health", `include=["refactoring","trend"]`) | the three KPIs, the 20 lowest files, the ranked refactoring targets, the trend against the last snapshot |
| Evidence the score means something here | the "Does the score find the bugs?" line from the last `init`, or `get_health(include=["accuracy"])` | whether to trust the ranking on this repo |
| Test quality | `uv run repowise health --format json`, findings with `biomarker_type` in `assertion_free_test`, `mock_saturated_test`, `large_assertion_block`, `duplicated_assertion_block` | tests that check nothing or prove only that mocks were called |
| Dead code | `uv run repowise dead-code --safe-only` | files nothing imports; unused exports are listed as review input only |
| Docs that drifted | `uv run repowise doc-drift` | how-tos, README and architecture doc naming paths or commands that no longer exist |
| Decisions | `uv run repowise decision health` | stale ADRs, ungoverned hotspots, unscoped decisions (an ADR without `## Scope`) |
| Line-level counts | `uv run ruff check --statistics src tests`, `uv run mypy` (count), `uv run lint-imports`, `uv run pylint --disable=all --enable=too-many-lines src` | how much the commit gate would reject if it ran on everything; the baseline is strict on changed lines only |
| Security | `uv run bandit -q -r src` | high-severity findings only in the summary |
| Mutation (on request, or on a schedule) | `uv run mutmut run` then `uv run mutmut results` | the survivor rate: tests that pass whatever the code does |

## 3. Report

One report, this order, no scores without their sentence:

1. **Headline.** Code health, hotspot health, worst file, trend since last time, and the accuracy line. Three sentences.
2. **Fix first.** The top five refactoring targets from Repowise, each as: file, the one marker that makes it bad in plain words, the leverage (what gets easier), the estimated effort Repowise gives. This is the list `improve-codebase-architecture` starts from.
3. **Tests that lie.** The advisory findings, grouped by file, and the mutation survivor rate if measured. Point at `py-test-audit` for the directory with the most.
4. **Dead and drifting.** Safe-to-delete files; docs that name things that no longer exist.
5. **Decisions.** Ungoverned hotspots (a bug-magnet file with no ADR), stale or unscoped ADRs. Each ungoverned hotspot is a grilling question for the next intake round.
6. **The gate's arithmetic.** Ruff, mypy, import-linter, module-length and bandit counts as a table. One line on what the commit gate blocks today and what `py-intake`'s baseline tickets still have open.

End with one next step in the `ask-dev` shape, and start it if the user says go: usually `improve-codebase-architecture` (Matt Pocock's, via `find_skill.py`) on the first target, or `py-test-audit` on the worst test directory.

## Rules

- Never edit code from here. This skill measures.
- Never write a report file. Repowise's `health --trend` is the history; a report in `docs/` would be a second copy that drifts.
- Mutation testing runs on the module the user names or the worst target, not the whole repo, unless the user asks and has the minutes.
