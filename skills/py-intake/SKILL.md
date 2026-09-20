---
name: py-intake
description: "Set up a Python repo for python-dev or re-orient in one: explore, mode, tracker, baseline, Repowise index, brownfield read-back and grilling, the human docs, harness shells. Resumable. `py-intake later` reviews parked tickets."
---

# Python intake

Run once per repo, and again whenever you come back after a long gap. Every step has a "done when" test, so re-running skips what is already there and never overwrites what a person wrote. Guide voice throughout: before each step, one plain paragraph on what you are about to do and why; after it, one on what changed.

`py-intake later`: skip to step 10.

## Door check, before anything

| Need | Test | If missing |
|---|---|---|
| `uv`, `git` | on PATH | stop; say how to install |
| `repowise` | `uv run repowise --version` or on PATH | `uv add --group dev repowise` (Python 3.11 or newer) |
| Upstream skills | `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/find_skill.py" --door-check` prints nothing missing | it prints the install command per upstream; continue, but steps 3 and 6 wait for Matt Pocock's skills |

Never improvise a missing skill's behaviour.

## 1. Explore (write nothing)

Establish facts from the repo, never by guessing. Present them as one table and ask "anything wrong here?" before going on.

| Fact | How |
|---|---|
| Greenfield or brownfield | brownfield when there is a `src/` or any `.py` outside scripts, and more than five commits |
| Remote | `git remote -v`: GitHub, GitLab (including self-hosted hosts), or none. Public repo? (`gh repo view --json isPrivate`, `glab repo view`) |
| Python | `.python-version`, `pyproject.toml` `requires-python`, else `python3 --version` |
| Package name | the directory under `src/` with an `__init__.py`, else `[project] name` |
| Tooling present | `pyproject.toml` `[tool.*]` tables, `.pre-commit-config.yaml`, CI files, `uv.lock`, `requirements*.txt` |
| ADK | `google-adk` in dependencies and its version: `1.x` means `adk-migrate` is the first ticket after intake; `2.x` means the `pack-adk` pack is selected. Either way install Google's skills from their repo: `npx skills@latest add google/adk-python -s adk-agent-builder,adk-architecture,adk-debug,adk-style -a '*' -y` |
| Packs | dependencies that select a knowledge pack (`pack-adk`: google-adk 2.x; `pack-data-engineering`: dlt, pandas, polars, pyarrow, sqlalchemy, duckdb, dbt-core, pandera, pyspark, prefect, dagster, airflow). A selected pack's "extra checks" section is applied in step 4 and its name is written under `## Packs` in `AGENTS.md` |
| Docs already there | `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`, `docs/adr/`, `docs/agents/`, `docs/howto/`, `README.md` |
| Repowise state | `.repowise/` present? `AGENTS.md` has a `REPOWISE:START` marker? |

## 2. Mode

Done when `docs/agents/mode.md` exists. Write it from `../py-baseline/templates/mode.md`. Say in one sentence what guide mode means: you explain before and after every step, and nothing runs unattended until a ticket earns it.

## 3. Tracker

Done when `docs/agents/issue-tracker.md` exists.

The remote decides. GitHub remote: GitHub Issues. GitLab remote: GitLab Issues. No remote: Backlog.md. A public repo gets a warning that its planning will be public and the offer of Backlog.md instead.

Matt Pocock's `setup-matt-pocock-skills` writes the tracker file, `docs/agents/domain.md` and the `## Agent skills` block. It is user-invoked, so the Skill tool refuses it: run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/find_skill.py" setup-matt-pocock-skills`, read the `SKILL.md` it prints, and follow it here. You already know its answers from step 1: tracker from the remote (GitHub, GitLab, or **Other: "Backlog.md, see docs/agents/issue-tracker.md"**), default triage labels, single-context, edit `AGENTS.md`. Ask the user only what step 1 did not settle, and show the draft files before writing, as it says.

Then, for the Backlog.md case: run `npx backlog.md init --defaults --no-git` if `backlog/config.yml` is missing, and replace `docs/agents/issue-tracker.md` with `templates/issue-tracker-backlog-md.md` (the "Other" file is freeform prose; ours carries the commands the skills need). Say the file was replaced and why.

## 4. Baseline

Done when every row of the files table in `py-baseline` exists and `uv run pre-commit run --all-files` runs (red is fine on brownfield; "cannot run" is not).

Call the Skill tool with "py-baseline" and follow its application rules: merge, never overwrite; fill placeholders from step 1; report every proposed change and let the user accept or decline each. In order:

1. `uv init --package` if there is no `pyproject.toml`; `uv python pin <version>`.
2. `[tool.*]` tables from `templates/pyproject-tools.toml`; `[dependency-groups] dev` from the same file; `uv sync`.
3. `.pre-commit-config.yaml`, `uv run pre-commit install`, `uv run detect-secrets scan > .secrets.baseline`.
4. `scripts/repowise_gate.py`, `scripts/adr_sync.py`, `scripts/run_readme_blocks.py`.
5. CI: `.github/workflows/ci.yml` on a GitHub remote, `.gitlab-ci.yml` on GitLab, both when there is no remote.
6. `.env.example`; `.gitignore` gets `.env`, `.repowise/`, `coverage.lcov`, `.mutmut-cache/`, `.secrets.baseline` stays tracked.
7. `CLAUDE.md` = `@AGENTS.md`; `AGENTS.md` pointers from the template above any existing content; `CONTEXT.md`; `docs/adr/` with the template as `docs/adr/README.md`.

Brownfield: do not apply everything in one commit. Propose the baseline as tickets on the tracker, one file group each (tool tables and pre-commit; CI; scripts and docs), and apply the first one now. Turning strict checks on over ten thousand lines at once is the horizontal slice that never lands.

Prove each gate bites before moving on: make one violation on a scratch file (a `print`, a 401-line module), watch the hook fail, revert, watch it pass. Show the output.

## 5. Repowise

Done when `.repowise/` exists and `AGENTS.md` has the managed section.

```bash
DO_NOT_TRACK=1 uv run repowise init --no-prose --no-editor-setup --no-save-key -y
uv run repowise generate-claude-md --output AGENTS.md
uv run python scripts/adr_sync.py --no-index
```

Read the "Does the score find the bugs?" line `init` prints and repeat it to the user: it is the evidence that the health score means something on this repo, or that the repo is too young to say.

Do not wire Repowise into the editor (`.mcp.json`, `~/.claude/settings.json`). The agent uses the CLI for everything it needs; its MCP tool definitions are a fixed cost on every turn, how large depends on the harness, and the CLI is pay-per-use. Say so in one sentence. If the user asks for it anyway, the command is `uv run repowise init -y`, and it is theirs to run.

## 6. Orientation (brownfield only)

Done when `CONTEXT.md` has at least three terms from this repo and every decision candidate Repowise found is accepted as an ADR, dismissed, or parked.

Read, in this order, and say nothing until you have all of it:

1. The map: the `AGENTS.md` managed section (architecture, key modules, entry points), then `uv run repowise context <file>` on each entry point. `context` takes files and symbols (`path.py::Name`), not directories.
2. Health: `uv run repowise health --refactoring-targets`.
3. Dead code: `uv run repowise dead-code --safe-only`.
4. Decisions: `uv run repowise decision candidates` and `uv run repowise decision health` (ungoverned hotspots).
5. Doc drift: `uv run repowise doc-drift`.

Then tell the user what the repo is, in six short paragraphs, using its own names: what it does and where a run starts; how it is layered, or that it is not; the three worst files and the one marker that makes each bad, in plain words ("this file talks to the database inside a loop, once per row"); what nothing uses; which files keep getting bug-fixed and have no decision governing them; which docs point at things that no longer exist. No scores without the sentence that explains them.

Now the grill. Call the Skill tool with "grilling". The questions come from what Repowise surfaced, one at a time, each with your recommended answer and its cost:

- Every decision candidate: "Repowise found this in `<evidence>`: <quote>. Is this a rule of the repo?" Yes: write the ADR from `templates/adr-template.md` with the paths under `## Scope`, then `uv run python scripts/adr_sync.py`. No: `uv run repowise decision dismiss <id>`. Not now: a `later` ticket.
- Every ungoverned hotspot: "This file is fixed often and no decision covers it. Why is it shaped this way?" The answer is an ADR, a `CONTEXT.md` term, or a `later` ticket titled with the question.
- Every repeated shape without a how-to: "You have four adapters that look alike. Is adding another one a thing people do here?" Yes: the first how-to in step 7 is that shape.
- Anything in the map you cannot name from the code: a `CONTEXT.md` term, in Matt Pocock's format.

Stop grilling when the frontier is empty or the user says stop; park the rest as `later` tickets so nothing is lost.

## 7. The three human docs

Done when `README.md` has at least one ```bash ci``` block that runs, `docs/architecture.md` exists, and `docs/howto/` has one how-to whose example compiles.

- `README.md`: merge `templates/README-skeleton.md` into what exists; never delete a section a person wrote. Run `uv run python scripts/run_readme_blocks.py README.md` and show it passing.
- `docs/architecture.md` from the template: rules only, the map is Repowise.
- The first how-to: brownfield, the shape from step 6 (or the most repeated module family in the map), mirrored on the best existing example of it; greenfield, wait for the first `grill-with-docs` and write it then. A how-to with no compiling example is not done.

## 8. Harness shells

Both harnesses install this plugin whole (Claude Code from `.claude-plugin/`, Copilot CLI from `plugin.json` and `com.github.copilot/`), so the persona, the reviewer agent and the hooks arrive with it. The repo needs only the pointer that selects the persona.

| Harness | File | From |
|---|---|---|
| Claude Code | `.claude/settings.json` with `"agent": "python-dev"` merged in | `templates/claude-settings.json` |
| GitHub Copilot | nothing in the repo; the user selects the agent with `copilot --agent python-dev` or the agent picker. Each machine installs the plugin once: `copilot plugin marketplace add fbhadha/py-dev`, `copilot plugin install python-dev@py-dev` | say so once |

Copilot's cloud agent on github.com cannot run intake or grilling and installs no plugins; say so once. Nothing has been exercised on Copilot yet; the first session there is the test.

## 9. Finish

1. `uv run pre-commit run --all-files` and `uv run pytest -m "not eval"`; show the output; on brownfield, red is recorded as the first tickets, not fixed now.
2. Commit in groups with messages that name the decision (`intake: baseline tool tables`, `intake: ADR 1, adapters never normalise`, ...). Never one commit called "setup".
3. ADK 1.x found in step 1: say that `adk-migrate` is the first ticket and create it.
4. Say in one line what comes next (the persona's table) and start it: greenfield, `grill-with-docs` on the user's idea; brownfield, `improve-codebase-architecture` on the worst file, or the first `later` ticket the user wants back.

## 10. `later`

List the open tickets labelled `later` from the tracker in `docs/agents/issue-tracker.md`, oldest first, one line each. Ask, one at a time: keep, kill, or do now. Kill closes it with a comment saying why. Do now: build it by the persona's build steps. Nothing else.
