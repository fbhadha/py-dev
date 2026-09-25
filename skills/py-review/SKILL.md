---
name: py-review
description: "Review a diff since a fixed point on four axes: Matt Pocock's code-review (Standards, Spec), Repowise's gate, risk and impacted tests (Change), the py-reviewer agent with the fault catalogue plus the test-diff check (Craft). Report first, fix on request. Use for a branch, a pull request or a diff to review."
---

# Review

Four axes, reported separately. Report first; fix on request. The fixed point is the commit or branch the user names, else `origin/main`.

1. Skill `code-review` (Matt Pocock's) with the fixed point. Keep its `## Standards` and `## Spec` as it wrote them.
2. `## Change`: `uv run python scripts/repowise_gate.py <fixed-point>..HEAD`, `uv run repowise risk <fixed-point>..HEAD`, `uv run repowise impacted-tests <fixed-point>..HEAD`. A gate finding is 🔴.
3. `## Craft`: dispatch the `py-reviewer` agent with the fixed point. Where the harness cannot dispatch an agent, open the plugin's `py-reviewer` agent file and follow it yourself after the other axes, so its judgement is not coloured by them.
4. Add to Craft: `uv run python scripts/check_test_diff.py <fixed-point>...HEAD` (deleted test, added skip, fewer assertions), then read the `tests/` diff yourself for an assertion loosened in place. Each is 🔴 unless the ticket and a commit message carry `test-override:` in the user's words. `uv run python scripts/check_literals.py <fixed-point>...HEAD` (a path that names nothing in the tree, a key missing from `.env.example`): 🔴 unless a commit message carries `literal-override:` in the user's words; then read the diff's other literals (paths, keys, field names, signatures) against the sources the ticket's plan names: one with no source is 🟠, one that contradicts its source 🔴. Read the ticket's `## Edge cases` table against the `tests/` diff: a `test` row with no test, or an edge-case test whose expected value has no source, is 🔴 (the way out is a revision of the row in the user's words, not an override); a transform or serialiser with a stated rule and no property test is 🟠; a mutation survivor with no triage is 🟠. A ticket that changed an agent (`src/<package>/entrypoints/agents/`): read `tests/evals/<name>/reports/<ticket>.md` against the ticket's `eval` rows: a row with no case, a case whose rubric is not the row's decided outcome, a report whose `commit:` is older than the agent's last change, or a targets file that quotes a user's sentence, each 🔴; a rerun for a simulated user that broke role is 🟠.

End with one line per axis: count and worst finding. No overall verdict. Then ask: "Fix the 🔴 now?"

Noisy output goes through `uv run repowise distill <command>`. A pack listed under `## Packs` in `AGENTS.md` is open while reviewing.
