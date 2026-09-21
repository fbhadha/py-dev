# Intake report: {{PROJECT}}

What intake set up, where each thing lives, and how work goes from here.

## What is installed

Everything runs through `uv run`; nothing needs an activated environment.

| Tool | Its job, in plain words |
|---|---|
| uv | installs the packages and runs every command below |
| ruff | reads the code for faults and formats it |
| mypy | checks that the types line up, on `src/` only |
| import-linter | keeps the layers from importing the wrong way |
| pylint, one rule | refuses a module over 400 lines, a test file over 150 |
| detect-secrets | refuses a key or a password in the code |
| pytest, coverage, diff-cover | runs the tests; new lines need a test |
| pre-commit | runs the rows above on every commit, on the files you changed |
| repowise | the map of the code: what calls what, what is worst, what nothing uses |
{{PACK_TOOLS}}

## The checks, and where each one stops you

| When | What runs | What it refuses |
|---|---|---|
| Every commit | ruff, mypy, import-linter, module length, detect-secrets, on the files in the commit | a print, a swallowed exception, a TODO with no owner, a 401-line file, a wrong-way import, a secret |
| Every pull request | the same on the lines the branch changed; the test-diff check; the whole test suite; coverage on the new lines; the change gate; the README's command blocks | a deleted or skipped test, fewer assertions, new lines under 90% covered, a change that made a touched file worse, a README command that no longer runs |
| Before a merge | branch protection on the server, offered after this merge | a merge with a red check; a push straight to `main` |
| When you ask | `uv run repowise health` | nothing; it reports the worst files, dead code and docs that drift |

Old code is tolerated: the commit and pull-request checks look at changed lines only. {{RED_NOW}}

## Files, and when to read each

| File | Read it when |
|---|---|
| `AGENTS.md` | first, every session: pointers to everything else |
| `docs/agents/repowise-map.md` | you want the map: layers, key modules, where a run starts; Repowise writes it, nobody edits it |
| `CLAUDE.md` | never; one line that includes `AGENTS.md` |
| `CONTEXT.md` | you need the word for something; the repo's glossary |
| `docs/architecture.md` | you need the layering rules |
| `docs/adr/` | you want to know why something is shaped this way; one file per decision |
| `docs/howto/` | before adding anything; one recipe per kind of addition. {{HOWTO}} |
| `docs/agents/mode.md`, `issue-tracker.md`, `domain.md`, `adr-template.md` | rarely: guide-mode settings, where tickets live, where the glossary and the decisions live, the blank ADR |
| `pyproject.toml` `[tool.*]`, `.pre-commit-config.yaml`, `{{CI_FILE}}` | the settings of the checks above; changed by a ticket, never to get green |
| `scripts/repowise_gate.py`, `adr_sync.py`, `run_readme_blocks.py`, `check_test_diff.py` | never edited here: the change gate, ADR binding, README execution and test-diff check CI runs |
| `.env.example`, `.secrets.baseline` | the keys the code reads, with no values; the secrets scanner's baseline |

## How work goes from here

1. You say what you want. I grill you until it is clear, then write the spec and the tickets in {{TRACKER}}.
2. Each ticket is one session on its own branch, `ticket/<id>`. Never a commit on `main`.
3. I name the shape (which how-to it fits), ask Repowise what the files depend on, search before naming anything new, and agree with you where the tests go.
4. Tests first, then code; the checks run after every green.
5. Done: I show you the diff, the commits and the checks and ask "Merge to main?" That yes is the one approval. The hook asks you before anything that lands on `main`, so nothing gets there by accident.
6. Merge commits, never squash: Repowise reads the history.

Lost: say so. Parked ideas are `later` tickets; "what is parked?" lists them.

## What Repowise found

{{ORIENTATION}}

## Next

- First ticket: {{FIRST_TICKET}}
- `uv run repowise health`, any time, for the whole-repo picture, worst files first.
- Packs: {{PACKS}}. A pack is selected when `pyproject.toml` gains a dependency one knows (google-adk 2.x; dlt, pandas, polars, pyarrow, sqlalchemy, duckdb, dbt-core, pandera, pyspark, prefect, dagster, airflow): say so and I run intake's pack step again.
