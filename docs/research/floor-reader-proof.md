2026-09-28

# Research: does a floor reader build a ticket from the plan alone?

Run on 2026-09-28 for ticket #31, spec #29, behaviour 2. One run per plan: a smoke test, not a benchmark.

## The question

A floor reader is given a ticket's plan and three fixed lines. Does it build the ticket with zero questions, a green Verify block and no weakened test? And does a plan written by the six rules do better than one written by the template before them?

## The set-up

- The ticket built: #24, property tests for `path_literals` and `env_keys` in `scripts/check_literals.py`.
- Two plans, both written before either run, with the same files, tests and expected values:
  - "before": from `skills/py-shape/references/ticket.md` at commit `7293a88`, the last commit before #30 changed it. <https://github.com/fbhadha/py-dev/issues/24#issuecomment-5875103478>
  - "after": from the same file on `main` at `015fa42`. <https://github.com/fbhadha/py-dev/issues/24#issuecomment-5875103752>
- The reader: one sub-agent per plan, dispatched by Claude Code's Agent tool with `model: haiku`, each in its own worktree cut from `origin/main`. The harness reported the alias `haiku` and no exact model id.
- The whole prompt was these three lines, then the plan's text:

```
Build the ticket below in this repository.
Write each test before the code it tests.
When the ticket's Verify commands pass, stop and report what you changed.
```

## The result

| Plan | Questions | Verify | Test-diff | Result | Tokens |
|---|---|---|---|---|---|
| before | 0 | green: 187 passed | clean | pass | 58,357 |
| after | 0 | green: 187 passed | clean | pass | 62,541 |

Verify and test-diff were run again by the dispatching session in each worktree, not taken from the sub-agent's report: `uv run pytest -m "not eval"` and `uv run python scripts/check_test_diff.py origin/main...HEAD`.

Both runs pass. By spec #29, behaviour 2: the rules ship, and there is no measured gain for the ticket template.

## What the pass or fail does not show

Read from the two test files. These are observations from one run each, so they may be chance.

| Observation | before | after |
|---|---|---|
| The named edge cases appear as `@example` with their exact values | No. The URL is `https://src/example.json`, not `https://example.com/a.json`. The glob and the format string are built from `src/example`, not the named `src/*.py` and `src/{name}.py` | Yes, all eight |
| The key is built, never filtered | Yes | No. It uses `.filter(...)` on the text strategy, where the plan says to build the key from one first character and a tail |
| Code the plan did not ask for | Two test classes, and an `else: raise ValueError` branch that no input reaches | None |
| Changed only the one file the plan names | Yes | Yes |
| `uv run ruff format --check` on the new file | would reformat | would reformat |
| The work was committed | No | No |

Neither plan named `ruff format` or a commit, and neither run did them. A plan for the floor reader must name both.

## Limits

- One run per plan. A second run of either plan could differ.
- The dispatching session wrote both plans, and knew which was which.
- The ticket changes no product code, so "write each test before the code" had nothing to order.
- The run tested a plan alone, not the persona or `py-build`. That is ticket #34.
