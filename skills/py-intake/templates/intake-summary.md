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
| hypothesis | generates the inputs for property tests, so a rule is checked on many values, not one |
| mutmut | changes the code on purpose to prove the tests notice; run on what a ticket changed, before review |
| pre-commit | runs the rows above on every commit, on the files you changed |
| repowise | the map of the code: what calls what, what is worst, what nothing uses |
{{PACK_TOOLS}}

## The checks, and where each one stops you

| When | What runs | What it refuses |
|---|---|---|
| While I work (Copilot CLI and Claude Code) | the plugin's guard | an edit to `src/` or `tests/` off a ticket branch, a commit or push that lands on `main`, until you say yes |
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
| `docs/research/` | you want to know what was checked outside this repo, and when; one dated, cited note per question |
| `docs/agents/mode.md`, `issue-tracker.md`, `domain.md`, `adr-template.md` | rarely: guide-mode settings, where tickets live, where the glossary and the decisions live, the blank ADR |
| `pyproject.toml` `[tool.*]`, `.pre-commit-config.yaml`, `{{CI_FILE}}` | the settings of the checks above; changed by a ticket, never to get green |
| `scripts/repowise_gate.py`, `adr_sync.py`, `run_readme_blocks.py`, `check_test_diff.py` | never edited here: the change gate, ADR binding, README execution and test-diff check CI runs |
| `.env.example`, `.secrets.baseline` | the keys the code reads, with no values; the secrets scanner's baseline |

## How work goes from here

1. You say what you want. I say which kind of request it is (a new idea, a change to something already decided, a ticket, a bug, a question), then what I think we should build, what I would leave out, and why, before I ask anything. If I think it should not be built, I say so.
2. I grill you in rounds of a few numbered questions, each with my recommended answer, the reason and what the other answer costs. A fact I need from outside this repo is read by a background researcher into `docs/research/`; a question talking cannot settle gets a throwaway prototype you react to; an idea bigger than one session becomes a map of decision tickets in {{TRACKER}}, worked one per session.
3. In the same session: the spec (the design, the order of work), then the tickets in {{TRACKER}}. Every ticket carries its plan: the files, the functions and their signatures, the tests in the order they get written, the commands that prove it. You approve the breakdown before anything is published.
4. No ticket, no code: a one-line fix gets a one-line ticket. Each ticket is one session on its own branch, `ticket/<id>`, never `main`.
5. Before the first line of code I check the plan against the code and show it to you: "Go?". Then tests first, one slice at a time, the checks after every green, and a line after each slice saying what changed.
6. Done: I show you the diff, the commits and the checks and ask "Merge to main?". That yes is the one approval; the hook asks before anything that lands on `main`. Merge commits, never squash: Repowise reads the history.

Change your mind about something already decided and I re-grill that part, update the spec and the tickets, then carry on; nothing gets quietly built around it. Lost: say so, or type `/mattpocock-skills:wait-what` and I say it again in plain words. A few of Matt Pocock's skills only you can start (a map for an idea too big for one session, triage of issues from other people, an architecture survey, learning a topic): when one is due I say why, give you the exact line to type, and wait. Parked ideas are `later` tickets; "what is parked?" lists them. How much I explain is `explain:` in `docs/agents/mode.md` (`decisions`, `teach` or `brief`). A word about AI coding itself (session, handoff, spec, ticket, grilling): Matt Pocock's AI Coding Dictionary, <https://github.com/mattpocock/dictionary-of-ai-coding>. A step only you can take (an install, a sign-in, a key) comes as a script that walks you through it; nothing secret goes through this chat.

## What Repowise found

{{ORIENTATION}}

## Next

- First ticket: {{FIRST_TICKET}}
- `uv run repowise health`, any time, for the whole-repo picture, worst files first.
- Packs: {{PACKS}}. A pack is selected when `pyproject.toml` gains a dependency one knows (google-adk 2.x; dlt, pandas, polars, pyarrow, sqlalchemy, duckdb, dbt-core, pandera, pyspark, prefect, dagster, airflow): say so and I run intake's pack step again.
