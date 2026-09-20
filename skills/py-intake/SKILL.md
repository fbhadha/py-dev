---
name: py-intake
description: "Set up a Python repo for python-dev or re-orient in one: explore, mode, agent files, tracker, baseline, Repowise index, brownfield read-back and grilling, the human docs, harness shells. Resumable; changes no existing file without showing the change and getting a yes. `py-intake later` reviews parked tickets."
---

# Python intake

Run once per repo, and again whenever you come back after a long gap. Every step has a "done when" test, so re-running skips what is already there. Guide voice throughout: before each step, one plain paragraph on what you are about to do and why; after it, one on what changed.

`py-intake later`: skip to step 11.

## The rule for existing files

This holds for every step below and overrides anything a template or an upstream skill says.

**You do not change, move, rename or delete a file that already exists without showing the change and getting a yes for that file.** Creating a file that does not exist is allowed where a step says so. Everything else goes through this, one file at a time:

1. Name the file and say in one sentence what you will do to it and why (merge these keys, append this section, move this content to that file, replace the body with a one-line include).
2. Show the change: the diff, or for a merge the resulting file with the new parts marked.
3. Wait for a yes. The harness will ask as well when you make the edit: that prompt is the mechanical yes, this one is where you explain. No yes, no change; record the file under `later` and move on. The user may say "yes to all of <group>" in their own words; that covers the group they named and nothing else.
4. After the change, say what changed, in one line.

A repo is "existing" when it has any commit before this session. In a repo with none, create freely and still show what you wrote. Never batch changes to several existing files behind one question, and never let a step "just fix" a file because a later step needs it that way: stop, explain, ask.

## Door check, before anything

| Need | Test | If missing |
|---|---|---|
| `uv`, `git` | on PATH | stop; say how to install |
| `repowise` | `uv run repowise --version` or on PATH | `uv add --group dev repowise` (Python 3.11 or newer) |
| Upstream skills | `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/find_skill.py" --door-check` prints nothing missing | it prints the install command per upstream; continue, but steps 4 and 7 wait for Matt Pocock's skills |

Never improvise a missing skill's behaviour.

## 1. Explore (write nothing)

Establish facts from the repo, never by guessing. Present them as one table and ask "anything wrong here?" before going on.

| Fact | How |
|---|---|
| Greenfield or brownfield | brownfield when there is a `src/` or any `.py` outside scripts, and more than five commits |
| Remote | `git remote -v`: GitHub, GitLab (including self-hosted hosts), or none. Public repo? (`gh repo view --json isPrivate`, `glab repo view`) |
| Python | `.python-version`, `pyproject.toml` `requires-python`, else `python3 --version` |
| Package name | the directory under `src/` with an `__init__.py`, else `[project] name` |
| Packaging | `uv.lock` (on uv already); `pyproject.toml` without a lock; `setup.py`, `setup.cfg`, `requirements*.txt`, `Pipfile`, `poetry.lock` (not on uv: see step 5) |
| Tooling present | `pyproject.toml` `[tool.*]` tables, `.pre-commit-config.yaml`, CI files under `.github/workflows/` or `.gitlab-ci.yml` |
| Agent files | `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `.cursorrules`, `.cursor/rules/`, `GEMINI.md`: which exist, and whether each is a one-line include or has real content |
| ADK | `google-adk` in dependencies and its version: `1.x` means `adk-migrate` is the first ticket after intake; `2.x` means the `pack-adk` pack is selected. Either way install Google's skills from their repo: `npx skills@latest add google/adk-python -s adk-agent-builder,adk-architecture,adk-debug,adk-style -a '*' -y` |
| Packs | dependencies that select a knowledge pack (`pack-adk`: google-adk 2.x; `pack-data-engineering`: dlt, pandas, polars, pyarrow, sqlalchemy, duckdb, dbt-core, pandera, pyspark, prefect, dagster, airflow). A selected pack's "extra checks" section is applied in step 5 and its name is written under `## Packs` in `AGENTS.md` |
| Docs already there | `CONTEXT.md`, `docs/adr/`, `docs/agents/`, `docs/howto/`, `README.md` |
| Repowise state | `.repowise/` present? `AGENTS.md` has a `REPOWISE:START` marker? |

## 2. Mode

Done when `docs/agents/mode.md` exists. Write it from `../py-baseline/templates/mode.md`. Say in one sentence what guide mode means: you explain before and after every step, and nothing runs unattended until a ticket earns it.

## 3. Agent files

Done when `AGENTS.md` exists with the pointer block from `../py-baseline/templates/AGENTS.md` at the top, and `CLAUDE.md` is the one line `@AGENTS.md`.

`AGENTS.md` is canonical because every harness reads it; `CLAUDE.md` is an include because Claude Code reads that (ADR 0003). This step runs before the tracker so Matt Pocock's setup skill has an `AGENTS.md` to write into.

| Found in step 1 | Propose |
|---|---|
| Neither file | Create `AGENTS.md` from the template and `CLAUDE.md` as `@AGENTS.md`. |
| `AGENTS.md` with content, no `CLAUDE.md` | Change `AGENTS.md`: the pointer block above the existing content, nothing else touched. Create `CLAUDE.md`. |
| `CLAUDE.md` with content, no `AGENTS.md` | Create `AGENTS.md`: the pointer block, then a heading `## Carried over from CLAUDE.md` with the content unchanged. Change `CLAUDE.md` to the one line. Two files, two approvals. |
| Both with content | Create nothing. Change `AGENTS.md`: pointer block on top, then `## Carried over from CLAUDE.md` with that content below the existing content. Change `CLAUDE.md` to the one line. |
| `.github/copilot-instructions.md` with content | Change `AGENTS.md`: `## Carried over from copilot-instructions.md` with the content. Change the original to one line, `See AGENTS.md.`; Copilot reads `AGENTS.md` natively. |
| `.cursorrules`, `.cursor/rules/`, `GEMINI.md` | Leave them. Say once that they exist and that `AGENTS.md` now holds the shared rules; folding them in is the user's call, as a `later` ticket. |

If the user declines the `CLAUDE.md` change, the fallback is: leave it as it is and prepend the one line `@AGENTS.md` (still a change, still shown), and say plainly that anything only in `CLAUDE.md` is invisible to every other harness.

Every prose rule that was carried over is a question for step 7: is a check enforcing it? Yes: propose deleting the sentence. No: should one? A rule the machine can check lives in `pyproject.toml`, not in prose.

## 4. Tracker

Done when `docs/agents/issue-tracker.md` exists.

The remote decides. GitHub remote: GitHub Issues. GitLab remote: GitLab Issues. No remote: Backlog.md. A public repo gets a warning that its planning will be public and the offer of Backlog.md instead.

Matt Pocock's `setup-matt-pocock-skills` writes the tracker file, `docs/agents/domain.md` and the `## Agent skills` block. It is user-invoked, so the Skill tool refuses it: run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/find_skill.py" setup-matt-pocock-skills`, read the `SKILL.md` it prints, and follow it here. You already know its answers from step 1: tracker from the remote (GitHub, GitLab, or **Other: "Backlog.md, see docs/agents/issue-tracker.md"**), default triage labels, single-context, and the file for the `## Agent skills` block is `AGENTS.md`. His skill prefers `CLAUDE.md` when one exists; here `AGENTS.md` is canonical (step 3), so put the block in `AGENTS.md` and say why. Writing the block into `AGENTS.md` is a change to an existing file: show it, get the yes. Ask the user only what step 1 did not settle, and show the draft files before writing, as it says. If `docs/agents/issue-tracker.md` already exists from an earlier run of his skill, this step is done; do not run it again.

Then, for the Backlog.md case: run `npx backlog.md init --defaults --no-git` if `backlog/config.yml` is missing, and propose replacing `docs/agents/issue-tracker.md` with `templates/issue-tracker-backlog-md.md` (the "Other" file is freeform prose; ours carries the commands the skills need). Show both, get the yes.

## 5. Baseline

Done when every row of the files table in `py-baseline` exists and `uv run pre-commit run --all-files` runs (red is fine on brownfield; "cannot run" is not).

Call the Skill tool with "py-baseline" and follow its application rules: merge, never overwrite; fill placeholders from step 1; every change to an existing file goes through the rule above. In order:

1. **Packaging.** No `pyproject.toml` and no other packaging: `uv init --package`, `uv python pin <version>`. Already on uv: nothing. On something else (`setup.py`, `requirements*.txt`, `Pipfile`, `poetry.lock`): do not touch it. Adopting uv is a decision, so it becomes the first baseline ticket, with the migration steps in the body (`uv init` beside the existing config, `uv add` from the requirements, `uv lock`, run the suite, then remove the old files), and the rest of this step waits until that ticket is done. Say so.
2. `[tool.*]` tables from `templates/pyproject-tools.toml`; `[dependency-groups] dev` from the same file; `uv sync`. Existing tables: merge missing keys only, show the result.
3. `.pre-commit-config.yaml`, `uv run pre-commit install` (the template installs the pre-commit and commit-msg stages), `uv run detect-secrets scan > .secrets.baseline`. An existing pre-commit config gets our hooks appended, shown first.
4. `scripts/repowise_gate.py`, `scripts/adr_sync.py`, `scripts/run_readme_blocks.py`, `scripts/check_protected_commit.py`.
5. **CI.** No workflow yet: `.github/workflows/ci.yml` on a GitHub remote, `.gitlab-ci.yml` on GitLab, both when there is no remote. A workflow already exists: never edit it. Add ours beside it as `.github/workflows/python-dev-checks.yml`, or on GitLab a `python-dev-checks.yml` that the user includes from `.gitlab-ci.yml` (that one-line include is a change to their file: show it, ask). Their pipeline keeps running; ours adds pre-commit on changed lines and the change gate.
6. `.env.example`; `.gitignore` gets `.env`, `.repowise/`, `coverage.lcov`, `.mutmut-cache/`; `.secrets.baseline` stays tracked. An existing `.gitignore` is a change: show the lines you will add.
7. `CONTEXT.md` from the template if absent; `docs/adr/` with the template as `docs/adr/README.md`.

Brownfield: do not apply everything in one commit. Propose the baseline as tickets on the tracker, one file group each (tool tables and pre-commit; CI; scripts and docs), and apply the first one now. Turning strict checks on over ten thousand lines at once is the horizontal slice that never lands. Strictness applies to changed lines only (pre-commit on staged files, CI from `origin/main`), so old code is tolerated and new mess is blocked.

Prove each gate bites before moving on: make one violation on a scratch file (a `print`, a 401-line module), watch the hook fail, revert, watch it pass. Show the output.

## 6. Repowise

Done when `.repowise/` exists and `AGENTS.md` has the managed section.

```bash
DO_NOT_TRACK=1 uv run repowise init --no-prose --no-editor-setup --no-save-key -y
uv run repowise generate-claude-md --output AGENTS.md
uv run python scripts/adr_sync.py --no-index
```

`generate-claude-md` appends a managed section between `REPOWISE:START` and `REPOWISE:END` markers to `AGENTS.md` and touches nothing above them. It is still a change to an existing file: say what it will add, get the yes, run it.

Read the "Does the score find the bugs?" line `init` prints and repeat it to the user: it is the evidence that the health score means something on this repo, or that the repo is too young to say.

Do not wire Repowise into the editor (`.mcp.json`, `~/.claude/settings.json`). The agent uses the CLI for everything it needs; its MCP tool definitions are a fixed cost on every turn, how large depends on the harness, and the CLI is pay-per-use. Say so in one sentence. If the user asks for it anyway, the command is `uv run repowise init -y`, and it is theirs to run.

## 7. Orientation (brownfield only)

Done when `CONTEXT.md` has at least three terms from this repo and every decision candidate Repowise found is accepted as an ADR, dismissed, or parked.

Read, in this order, and say nothing until you have all of it:

1. The map: the `AGENTS.md` managed section (architecture, key modules, entry points), then `uv run repowise context <file>` on each entry point. `context` takes files and symbols (`path.py::Name`), not directories.
2. Health: `uv run repowise health --refactoring-targets`.
3. Dead code: `uv run repowise dead-code --safe-only`.
4. Decisions: `uv run repowise decision candidates` and `uv run repowise decision health` (ungoverned hotspots).
5. Doc drift: `uv run repowise doc-drift`.

Then tell the user what the repo is, in six short paragraphs, using its own names: what it does and where a run starts; how it is layered, or that it is not; the three worst files and the one marker that makes each bad, in plain words ("this file talks to the database inside a loop, once per row"); what nothing uses; which files keep getting bug-fixed and have no decision governing them; which docs point at things that no longer exist. No scores without the sentence that explains them.

Now the grill. Call the Skill tool with "grilling". The questions come from what Repowise surfaced and from step 3, one at a time, each with your recommended answer and its cost:

- Every decision candidate: "Repowise found this in `<evidence>`: <quote>. Is this a rule of the repo?" Yes: write the ADR from `templates/adr-template.md` with the paths under `## Scope`, then `uv run python scripts/adr_sync.py`. No: `uv run repowise decision dismiss <id>`. Not now: a `later` ticket.
- Every ungoverned hotspot: "This file is fixed often and no decision covers it. Why is it shaped this way?" The answer is an ADR, a `CONTEXT.md` term, or a `later` ticket titled with the question.
- Every prose rule carried over into `AGENTS.md` in step 3: "A check enforces this now (`<rule>`): delete the sentence?" or "Nothing enforces this. Should a check, an ADR, or neither?" Deleting the sentence is a change to `AGENTS.md`: show it, get the yes.
- Every repeated shape without a how-to: "You have four adapters that look alike. Is adding another one a thing people do here?" Yes: the first how-to in step 8 is that shape.
- Anything in the map you cannot name from the code: a `CONTEXT.md` term, in Matt Pocock's format.

Stop grilling when the frontier is empty or the user says stop; park the rest as `later` tickets so nothing is lost.

## 8. The three human docs

Done when `README.md` has at least one ```bash ci``` block that runs, `docs/architecture.md` exists, and `docs/howto/` has one how-to whose example compiles.

- `README.md`: propose merging `templates/README-skeleton.md` into what exists, section by section; never delete a section a person wrote; show the result, get the yes. Run `uv run python scripts/run_readme_blocks.py README.md` and show it passing.
- `docs/architecture.md` from the template: rules only, the map is Repowise.
- The first how-to: brownfield, the shape from step 7 (or the most repeated module family in the map), mirrored on the best existing example of it; greenfield, wait for the first `grill-with-docs` and write it then. A how-to with no compiling example is not done.

## 9. Harness shells

Both harnesses install this plugin whole (Claude Code from `.claude-plugin/`, Copilot CLI from `plugin.json` and `com.github.copilot/`), so the persona, the reviewer agent and the hooks arrive with it. The repo needs only the pointer that selects the persona.

| Harness | File | From |
|---|---|---|
| Claude Code | `.claude/settings.json` with `"agent": "python-dev"` merged in; an existing file is a change, shown first | `templates/claude-settings.json` |
| GitHub Copilot | nothing in the repo; the user selects the agent with `copilot --agent python-dev` or the agent picker. Each machine installs the plugin once: `copilot plugin marketplace add fbhadha/py-dev`, `copilot plugin install python-dev@py-dev` | say so once |

Copilot's cloud agent on github.com cannot run intake or grilling and installs no plugins; say so once. Nothing has been exercised on Copilot yet; the first session there is the test.

## 10. Finish

1. `uv run pre-commit run --all-files` and `uv run pytest -m "not eval"`; show the output; on brownfield, red is recorded as the first tickets, not fixed now.
2. Commit in groups with messages that name the decision (`intake: baseline tool tables`, `intake: ADR 1, adapters never normalise`, ...). Never one commit called "setup". Every existing file the commit touches was approved by name; the message says so (`approved: pyproject.toml, .gitignore`).
3. ADK 1.x found in step 1: say that `adk-migrate` is the first ticket and create it.
4. Say this once, in these words or close to them: "The protected-file guard stays on. From now on the harness asks you before I change an agent file, packaging, a check, CI or a doc, once per file per session, and a commit touching one must name it as approved. To turn it off, tell me and I will change `protect-existing-files` to `off` in `docs/agents/mode.md`; the harness will ask you to confirm that edit. `PYTHON_DEV_GUARD=off` turns it off for one session without changing the repo."
5. Say in one line what comes next (the persona's table) and start it: greenfield, `grill-with-docs` on the user's idea; brownfield, `improve-codebase-architecture` on the worst file, or the first `later` ticket the user wants back.

## 11. `later`

List the open tickets labelled `later` from the tracker in `docs/agents/issue-tracker.md`, oldest first, one line each. Ask, one at a time: keep, kill, or do now. Kill closes it with a comment saying why. Do now: build it by the persona's build steps. Nothing else.
