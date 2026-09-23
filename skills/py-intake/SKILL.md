---
name: py-intake
description: "Set up a Python repo for python-dev or re-orient in one: explore, mode, agent files, tracker, baseline, Repowise index, brownfield read-back and grilling, the human docs, harness shells, the intake report. Resumable; changes no existing file without showing the change and getting a yes. `py-intake later` reviews parked tickets."
---

# Python intake

Run once per repo, and again whenever you come back after a long gap. Every step has a "done when" test, so re-running skips what is already there. Voice throughout (persona section 2): before each step, what you are about to do, why, and what the user gets; after it, what changed and what comes next.

`py-intake later`: skip to step 11.

## The branch rule

Intake runs on a branch, `intake/baseline`, and lands on `main` by one merge the user says yes to at the end (step 10), after the intake report has said what was set up. Create it first: `git switch -c intake/baseline` (a repo with no commits yet: make the first commit, `init`, on `main`; the hook asks once; then branch). On the branch you change files freely, and for every existing file you still say, before the change, which file and what you will do to it in one sentence, then show the result with the new parts marked. Nobody waits per file; the diff at the merge is where the user says yes. Never let a step "just fix" a file because a later step needs it that way without saying so.

## Door check, before anything

| Need | Test | If missing |
|---|---|---|
| `uv`, `git` | on PATH | a wizard stage (below) |
| `gh` signed in (GitHub remote), `glab` signed in (GitLab), `node` (no remote: Backlog.md runs on it) | `gh auth status`, `glab auth status`, `node --version`; `git remote -v` says which one applies | a wizard stage |
| `repowise` | not needed until step 6; step 5's `uv sync` installs it from the dev group | a repo whose `requires-python` is below 3.11 cannot install it in its own environment: `uv tool install repowise` and call `repowise` on PATH instead of `uv run repowise`, skip the CI change-gate job, and create the ticket "move to Python 3.11" (say why: the change gate imports Repowise, which needs 3.11) |
| Upstream skills | `python3 <scripts>/find_skill.py --door-check` prints nothing missing (`<scripts>`: the folder the session-start line names, or the persona's section 5 command) | it prints the install command per upstream. Matt Pocock's plugin itself: its lines go in the chat, because `wizard` is in it. Google's: you run it in step 1. Continue, but steps 4 and 7 wait for Matt Pocock's skills |

Everything missing goes into one script: Skill `wizard`, one stage per item (the install line, the page to open, the command that proves it), saved to the OS temp dir. Say how to run it in another terminal and stop; the next session starts here again, and a stage already done is skipped. Never improvise a missing skill's behaviour.

## 1. Explore (write nothing)

Establish facts from the repo, never by guessing. Present them as one table and ask "anything wrong here?" before going on.

| Fact | How |
|---|---|
| Greenfield or brownfield | brownfield when there is a `src/` or any `.py` outside scripts, and more than five commits |
| Remote | `git remote -v`: GitHub, GitLab (including self-hosted hosts), or none. Public repo? (`gh repo view --json isPrivate`, `glab repo view`) |
| Python | `.python-version`, `pyproject.toml` `requires-python`, else `python3 --version`. Below 3.11: see the door check's Repowise row |
| Package name | the directory under `src/` with an `__init__.py`, else `[project] name` |
| Packaging | `uv.lock` (on uv already); `pyproject.toml` without a lock; `setup.py`, `setup.cfg`, `requirements*.txt`, `Pipfile`, `poetry.lock` (not on uv: see step 5) |
| Tooling present | `pyproject.toml` `[tool.*]` tables, `.pre-commit-config.yaml`, CI files under `.github/workflows/` or `.gitlab-ci.yml` |
| Agent files | `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `.cursorrules`, `.cursor/rules/`, `GEMINI.md`: which exist, and whether each is a one-line include or has real content |
| ADK | `google-adk` in dependencies and its version: `1.x` means `adk-migrate` is the first ticket after intake; `2.x` means the `pack-adk` pack is selected. Either way install Google's skills from their repo: `npx skills@latest add google/adk-python -s adk-agent-builder,adk-architecture,adk-debug,adk-style -a '*' -y` |
| Packs | dependencies that select a knowledge pack (`pack-adk`: google-adk 2.x; `pack-data-engineering`: dlt, pandas, polars, pyarrow, sqlalchemy, duckdb, dbt-core, pandera, pyspark, prefect, dagster, airflow). A selected pack's "extra checks" section is applied in step 5 and its name is written under `## Packs` in `AGENTS.md` |
| Docs already there | `CONTEXT.md`, `docs/adr/`, `docs/agents/`, `docs/howto/`, `docs/research/`, `README.md` |
| Matt Pocock's skills already set up | `docs/agents/issue-tracker.md`, `docs/agents/domain.md`, `docs/agents/triage-labels.md`, an `## Agent skills` block in `AGENTS.md` or `CLAUDE.md`, a `backlog/` directory: which exist. Any of them means his setup ran before; steps 4 and 7 keep what it wrote and ask only about what is missing |
| Repowise already in use | `.repowise/` present; `docs/agents/repowise-map.md` or a `REPOWISE:START` marker in `AGENTS.md` or `.claude/CLAUDE.md` (an older layout, or `repowise update` run by hand: the map moves to its own file, the marker section is removed from the agent file, shown first); `.mcp.json` or `.claude/settings.json` names repowise (the user wired the editor themselves); `uv run repowise decision list` shows decisions that have no ADR file behind them; `uv run repowise status` for when the index was last synced. Anything found means the user has used Repowise here; step 6 keeps the index and the wiring and step 7 turns stored decisions into ADRs |

## 2. Mode

Done when `docs/agents/mode.md` exists. Write it from `../py-baseline/templates/mode.md`. Say in two sentences what guide mode means: before and after each step the agent says what it is doing, why, and what changed; it gives its view on every idea, pushes back, and writes no code without a ticket; nothing runs unattended until a ticket earns it. `explain:` in that file sets how much it explains (`decisions`, `teach`, `brief`).

## 3. Agent files

Done when `AGENTS.md` exists with the pointer block from `../py-baseline/templates/AGENTS.md` at the top, and `CLAUDE.md` is the one line `@AGENTS.md`.

`AGENTS.md` is canonical because every harness reads it; `CLAUDE.md` is an include because Claude Code reads that (ADR 0003). This step runs before the tracker so Matt Pocock's setup skill has an `AGENTS.md` to write into.

| Found in step 1 | Propose |
|---|---|
| Neither file | Create `AGENTS.md` from the template and `CLAUDE.md` as `@AGENTS.md`. |
| `AGENTS.md` with content, no `CLAUDE.md` | Change `AGENTS.md`: the pointer block above the existing content, nothing else touched. Create `CLAUDE.md`. |
| `CLAUDE.md` with content, no `AGENTS.md` | Create `AGENTS.md`: the pointer block, then a heading `## Carried over from CLAUDE.md` with the content unchanged. Change `CLAUDE.md` to the one line. |
| Both with content | Create nothing. Change `AGENTS.md`: pointer block on top, then `## Carried over from CLAUDE.md` with that content below the existing content. Change `CLAUDE.md` to the one line. |
| `.github/copilot-instructions.md` with content | Change `AGENTS.md`: `## Carried over from copilot-instructions.md` with the content. Change the original to one line, `See AGENTS.md.`; Copilot reads `AGENTS.md` natively. |
| `.cursorrules`, `.cursor/rules/`, `GEMINI.md` | Leave them. Say once that they exist and that `AGENTS.md` now holds the shared rules; folding them in is the user's call, as a `later` ticket. |

An `AGENTS.md` written by an earlier python-dev with no `## How work happens here` section: propose adding it from the template, above `## Read first` (a change: show it, get the yes). It is what makes any agent in the repo, the default one included, work ticket-first.

If the user declines the `CLAUDE.md` change, the fallback is: leave it as it is and prepend the one line `@AGENTS.md` (still a change, still shown), and say plainly that anything only in `CLAUDE.md` is invisible to every other harness.

Every prose rule that was carried over is a question for step 7: is a check enforcing it? Yes: propose deleting the sentence. No: should one? A rule the machine can check lives in `pyproject.toml`, not in prose.

## 4. Tracker

Done when `docs/agents/issue-tracker.md` exists.

The remote decides. GitHub remote: GitHub Issues. GitLab remote: GitLab Issues. No remote: Backlog.md. A public repo gets a warning that its planning will be public and the offer of Backlog.md instead.

Matt Pocock's `setup-matt-pocock-skills` writes the tracker file, `docs/agents/domain.md` and the `## Agent skills` block. Only a person can start it (persona section 5): User types `setup-matt-pocock-skills`, and say you will answer its questions from step 1 and show every file before it is written. This is the first time the user types a line for you: say that a few of Matt's skills work this way and you will always say when. When it runs, follow it here. You already know its answers from step 1: tracker from the remote (GitHub, GitLab, or **Other: "Backlog.md, see docs/agents/issue-tracker.md"**), default triage labels, single-context, and the file for the `## Agent skills` block is `AGENTS.md`. His skill prefers `CLAUDE.md` when one exists; here `AGENTS.md` is canonical (step 3), so put the block in `AGENTS.md` and say why. Writing the block into `AGENTS.md` is a change to an existing file: show it, get the yes. Ask the user nothing his skill's questions cover: the tracker, the labels (defaults), the context count and the file are settled above. Show the draft files before writing, as it says. If `docs/agents/issue-tracker.md` already exists from an earlier run of his skill, this step is done; do not run it again. `domain.md` or the `## Agent skills` block present with the tracker file missing: say what is there, run his skill only for the missing piece, and keep his files as they are.

Then, for the Backlog.md case: run `npx backlog.md init --defaults --no-git` if `backlog/config.yml` is missing, and propose replacing `docs/agents/issue-tracker.md` with `templates/issue-tracker-backlog-md.md` (the "Other" file is freeform prose; ours carries the commands the skills need). Show both, get the yes.

## 5. Baseline

Done when every row of the files table in `py-baseline` exists and `uv run pre-commit run --all-files` runs (red is fine on brownfield; "cannot run" is not).

Call the Skill tool with "py-baseline" and follow its application rules: merge, never overwrite; fill placeholders from step 1; every change to an existing file is announced and shown as the branch rule says. In order:

1. **Packaging.** No `pyproject.toml` and no other packaging: `uv init --package`, `uv python pin <version>`. Already on uv: nothing. On something else (`setup.py`, `requirements*.txt`, `Pipfile`, `poetry.lock`): do not touch it. Adopting uv is a decision, so it becomes the first baseline ticket, with the migration steps in the body (`uv init` beside the existing config, `uv add` from the requirements, `uv lock`, run the suite, then remove the old files), and the rest of this step waits until that ticket is done. Say so.
2. `[tool.*]` tables from `templates/pyproject-tools.toml`; `[dependency-groups] dev` from the same file; `uv sync`. Existing tables: merge missing keys only, show the result. If `uv sync` reports a version conflict, do not probe PyPI: lower the floor of the package it names to its major version (`>=2.0`), let `uv` pick, and file it as a plugin defect (persona section 9). The plugin's CI resolves the template's dev group, so a conflict here means a new release moved.
3. `.pre-commit-config.yaml`, `uv run pre-commit install`, `uv run detect-secrets scan > .secrets.baseline`. An existing pre-commit config gets our hooks appended, shown first.
4. `scripts/repowise_gate.py`, `scripts/adr_sync.py`, `scripts/run_readme_blocks.py`, `scripts/check_test_diff.py`.
5. **CI.** No workflow yet: `.github/workflows/ci.yml` on a GitHub remote, `.gitlab-ci.yml` on GitLab, both when there is no remote. A workflow already exists: never edit it. Add ours beside it as `.github/workflows/python-dev-checks.yml`, or on GitLab a `python-dev-checks.yml` that the user includes from `.gitlab-ci.yml` (that one-line include is a change to their file: show it, ask). Their pipeline keeps running; ours adds pre-commit on changed lines, the test-diff check, coverage on changed lines and the change gate.
6. `.env.example`; `.gitignore` gets `.env`, `.repowise/`, `coverage.lcov`, `.mutmut-cache/`; `.secrets.baseline` stays tracked. An existing `.gitignore` is a change: show the lines you will add. Then the keys: every variable in `.env.example` a person must obtain (an API key, a token; a pack's keys, such as `GOOGLE_API_KEY` for ADK) and every `secrets.*` the CI file reads is a step only the user can take. One or more of them: Skill `wizard`, scoped from those two files, writes the script that opens each provider's page, captures the value blind and writes it to `.env` and the CI secrets. The user runs it themselves; no value ever passes through the chat.
7. `CONTEXT.md` from the template if absent; `docs/agents/adr-template.md` from `templates/adr-template.md`; `docs/adr/` created empty (any `.md` in it becomes a Repowise decision, so no README there).
8. **Packs.** For each pack step 1 selected, open its `SKILL.md` and apply its "Extra checks this pack turns on" section: the ruff groups into `select`, the import-linter contract, the pre-commit hook, the dev dependencies (`uv add --group dev ...`). Write the pack's name under `## Packs` in `AGENTS.md`. No pack selected: leave the section's comment as it is.

Brownfield: do not apply everything in one commit. Propose the baseline as tickets on the tracker, one file group each (tool tables and pre-commit; CI; scripts and docs), and apply the first one now. Turning strict checks on over ten thousand lines at once is the horizontal slice that never lands. Strictness applies to changed lines only (pre-commit on staged files, CI from `origin/main`), so old code is tolerated and new mess is blocked.

Prove each gate bites before moving on: make one violation on a scratch file (a `print`, a 401-line module), watch the hook fail, revert, watch it pass. Show the output.

## 6. Repowise

Done when `.repowise/` exists and `docs/agents/repowise-map.md` exists.

Already in use (step 1 found `.repowise/`): keep the index and any editor wiring the user made; run only the lines below that are missing their result, and confirm first in one line: "You have used Repowise here before; I will keep the index and your wiring and only add what is missing. Right?"

```bash
DO_NOT_TRACK=1 uv run repowise init --no-prose --no-editor-setup --no-save-key -y . > /tmp/repowise-init.txt 2>&1; grep -i "find the bug\|health score" /tmp/repowise-init.txt
uv run repowise generate-claude-md --stdout | sed -n '/REPOWISE:START/,/REPOWISE:END/p' > docs/agents/repowise-map.md
uv run python scripts/adr_sync.py --no-index
```

Three facts about Repowise 0.52 that shape those lines: `repowise update` writes `.claude/CLAUDE.md` and `.vscode/` files and no flag or variable stops it, so the plugin never runs `update`; `init` with `--no-editor-setup` is the refresh, idempotent and seconds long. `generate-claude-md --output <file>` overwrites the whole file, so the map lives in its own file that only Repowise writes, and `AGENTS.md` points at it. Every `.md` under `docs/adr/` becomes a decision candidate, so the ADR template lives in `docs/agents/`, not there. `.claude/CLAUDE.md` or `.vscode/mcp.json` found in the tree with no `.claude/settings.json` of the user's own: say they came from `repowise update` and propose deleting them.

Read the "Does the score find the bugs?" line from the saved output (run `init` once, never three times to grep it) and repeat it to the user: it is the evidence that the health score means something on this repo, or that the repo is too young to say.

Do not wire Repowise into the editor (`.mcp.json`, `~/.claude/settings.json`). The agent uses the CLI for everything it needs; its MCP tool definitions are a fixed cost on every turn, how large depends on the harness, and the CLI is pay-per-use. Say so in one sentence. If the user asks for it anyway, the command is `uv run repowise init -y`, and it is theirs to run.

## 7. Orientation (brownfield only)

Done when `CONTEXT.md` has at least three terms from this repo and every decision candidate Repowise found is accepted as an ADR, dismissed, or parked.

Read, in this order, and say nothing until you have all of it:

1. The map: `docs/agents/repowise-map.md` (architecture, key modules, entry points), then `uv run repowise context <file>` on at most three entry points, the ones the map lists first. `context` takes files and symbols (`path.py::Name`), not directories, and its output is long; three is enough to describe the repo.
2. Health: `uv run repowise health --refactoring-targets`.
3. Dead code: `uv run repowise dead-code --safe-only`.
4. Decisions: `uv run repowise decision list` first: any accepted decision with no ADR file in `docs/adr/` was added through Repowise directly; then `uv run repowise decision candidates` and `uv run repowise decision health` (ungoverned hotspots).
5. Doc drift: `uv run repowise doc-drift`.

Then tell the user what the repo is, in one message, one or two sentences per item, using its own names: what it does and where a run starts; how it is layered, or that it is not; the three worst files and the one marker that makes each bad, in plain words ("this file talks to the database inside a loop, once per row"); what nothing uses; which files keep getting bug-fixed and have no decision governing them; which docs point at things that no longer exist. No scores without the sentence that explains them.

Now the grill, by `py-shape`'s section 3: rounds of at most five numbered questions, each with your recommended answer, the reason and what the other answer costs. The questions come from what Repowise surfaced and from step 3:

- Every stored decision with no ADR behind it (`decision list` shows an ADR-sourced one as `proposed` until `adr_sync.py` confirms it; that is normal, not a stored decision): "You recorded this in Repowise: <title>. Still true?" Yes: write the ADR from `docs/agents/adr-template.md` with the same title and its paths under `## Scope`, then `uv run python scripts/adr_sync.py` (the ADR is the one write path, ADR 0005; the store entry is kept, now bound to the file). No: `uv run repowise decision deprecate <id>`.
- Every decision candidate: "Repowise found this in `<evidence>`: <quote>. Is this a rule of the repo?" Yes: write the ADR from `docs/agents/adr-template.md` with the paths under `## Scope`, then `uv run python scripts/adr_sync.py`. No: `uv run repowise decision dismiss <id> --yes`. Not now: a `later` ticket.
- Every ungoverned hotspot: "This file is fixed often and no decision covers it. Why is it shaped this way?" The answer is an ADR, a `CONTEXT.md` term, or a `later` ticket titled with the question.
- Every prose rule carried over into `AGENTS.md` in step 3: "A check enforces this now (`<rule>`): delete the sentence?" or "Nothing enforces this. Should a check, an ADR, or neither?" Deleting the sentence is a change to `AGENTS.md`: show it, get the yes.
- Every repeated shape without a how-to: "You have four adapters that look alike. Is adding another one a thing people do here?" Yes: the first how-to in step 8 is that shape.
- Anything in the map you cannot name from the code: a `CONTEXT.md` term, in Matt Pocock's format.

Stop grilling when the frontier is empty or the user says stop; park the rest as `later` tickets so nothing is lost.

## 8. The three human docs

Done when `README.md` has at least one ```bash ci``` block that runs, `docs/architecture.md` exists, and `docs/howto/` has one how-to whose example compiles.

- `README.md`: propose merging `templates/README-skeleton.md` into what exists, section by section; never delete a section a person wrote; show the result, get the yes. Run `uv run python scripts/run_readme_blocks.py README.md` and show it passing.
- `docs/architecture.md` from the template: rules only, the map is Repowise.
- The first how-to: brownfield, the shape from step 7 (or the most repeated module family in the map), mirrored on the best existing example of it; greenfield, wait for the first shape to settle in shaping (the first grill, or the map ticket that names one) and write it then. A how-to with no compiling example is not done.
- A selected pack that ships how-tos (`pack-data-engineering`: `references/howto/`, with the example package under `references/example/`): on greenfield, and on brownfield where the repo has no how-to for that shape, propose copying them. The package `references/example/orders/` to `src/{{PACKAGE}}/examples/orders/` (create `src/{{PACKAGE}}/examples/__init__.py` if missing); `references/example/tests/unit/` to `tests/unit/examples/` and `references/example/tests/integration/` to `tests/integration/examples/`; in every copied `.py` file replace the placeholder package name `yourpkg` with `{{PACKAGE}}`; each how-to to `docs/howto/` with `{{PACKAGE}}` filled. Then `uv run pytest tests/unit/examples tests/integration/examples` and show it green. The how-tos then describe this repo's shapes from the first ticket on. The example needs Python 3.11 or newer; below that, copy the how-tos alone and say why.

## 9. Harness shells

Both harnesses install this plugin whole (Claude Code from `.claude-plugin/`, Copilot CLI from `plugin.json` and `com.github.copilot/`), so the persona, the reviewer agent and the hooks arrive with it. The repo needs only the pointer that selects the persona.

| Harness | File | From |
|---|---|---|
| Claude Code | `.claude/settings.json` with `"agent": "python-dev"` merged in; an existing file is a change, shown first | `templates/claude-settings.json` |
| GitHub Copilot CLI | nothing in the repo. Each machine installs the plugin once: `copilot plugin marketplace add fbhadha/py-dev`, `copilot plugin install python-dev@py-dev`. The agent's id is `python-dev:python-dev`: `copilot --agent python-dev:python-dev -i "start"` opens a session that starts itself; `/agent` lists it as python-dev | say so once |
| VS Code | nothing in the repo. User settings `"chat.plugins.enabled": true` and `"chat.plugins.marketplaces": ["fbhadha/py-dev", "mattpocock/skills"]`, or install with the CLI (VS Code picks up `~/.copilot/installed-plugins/`). Pick python-dev in the Agent dropdown with the session target set to Copilot. The plugin's hooks do not run in VS Code, so the guards there are CI and branch protection | say so once |

Copilot's cloud agent on github.com is not interactive, so it cannot run intake or grilling; it loads a plugin only when the repo's `.github/copilot/settings.json` enables it (`enabledPlugins`). Say so once.

## 10. Finish

0. Walk the "done when" line of every step above and list the ones that do not hold; do those first. "Finish intake" from the user means finish it, not skip to the merge: in the live run the three human docs (step 8) and the harness shells (step 9) were skipped this way.
1. `uv run repowise distill uv run pre-commit run --all-files`, `uv run lint-imports`, and `uv run repowise distill uv run pytest -m "not eval"`; show the distilled output; on brownfield, red is recorded as the first tickets, not fixed now. The commit hook checks staged files only, so intake's own commits go through while CI stays red; never `pre-commit uninstall`.
2. Commit in groups with messages that name the decision (`intake: baseline tool tables`, `intake: ADR 1, adapters never normalise`, ...). Never one commit called "setup".
3. ADK 1.x found in step 1: say that `adk-migrate` is the first ticket and create it.
4. **The intake report.** Fill `templates/intake-summary.md` and show it as one message; a harness that renders a Markdown file may render it instead. Every placeholder is a fact an earlier step established, never a guess: `{{PROJECT}}`; `{{PACK_TOOLS}}`, one table row per dev dependency a pack added in step 5, or nothing; `{{RED_NOW}}`, the tickets sub-step 1 recorded for red checks, or nothing; `{{HOWTO}}`, the how-to step 8 wrote, or "None yet: the first is written when the first grilling settles a shape"; `{{CI_FILE}}`, the workflow step 5 wrote; `{{TRACKER}}`, from step 4; `{{ORIENTATION}}`, the step 7 read-back one line per item, then the ADRs written and the `later` tickets parked (greenfield: the "Does the score find the bugs?" line from step 6, and that the map fills as code lands); `{{FIRST_TICKET}}`, from sub-step 7; `{{PACKS}}`, the names under `## Packs` or "none selected". Delete the row or phrase for anything intake skipped (the change gate on a repo below Python 3.11, the pack row, the pull-request and branch-protection rows when there is no remote): the report says what happened, not what the template offers. Do not commit it: every fact in it lives in `AGENTS.md`, the tool tables, `docs/adr/` or Repowise, and a copy would be the first doc-drift finding (persona section 8).
5. Land it. `git push -u origin intake/baseline`; on GitHub or GitLab, `gh pr create` (`glab mr create`) with the report as the body, so CI runs on it and the report stays with the merge. Show the merge summary (files that existed before, one sentence each; then the commit list; then the check results; the new files are in the report, do not list them again) and ask: "Merge to main?" Yes: `gh pr merge --merge --delete-branch` (`glab mr merge`), or with no remote `git switch main && git merge --no-ff intake/baseline && git branch -d intake/baseline`. The hook asks once more; same yes.
6. After the merge, and only when CI is green on it (or there is no remote): one question: "Protect `main` on the server, so nothing lands there except a merge with green checks, from any tool or person?" CI red on brownfield: a `later` ticket "turn on branch protection when CI is green", blocked by the layering ticket, and say so. Yes, GitHub:

   ```bash
   gh api -X PUT "repos/{owner}/{repo}/branches/main/protection" --input - <<'JSON'
   {"required_status_checks":{"strict":true,"contexts":["commit gate on the diff","tests","README commands still run"]},
    "enforce_admins":false,"required_pull_request_reviews":null,"restrictions":null}
   JSON
   ```

   GitLab: `glab api -X POST "projects/:id/protected_branches" -f name=main -f push_access_level=0 -f merge_access_level=30` and `glab api -X PUT "projects/:id" -f only_allow_merge_if_pipeline_succeeds=true`. No remote: nothing to set; the hook is the guard.
7. Say in one line what comes next (the report's first ticket, from the persona's table) and start it: greenfield, Skill `py-shape` on the user's idea; brownfield, User types `improve-codebase-architecture` with the worst file (persona section 5), or the first `later` ticket the user wants back.

## 11. `later`

List the open tickets labelled `later` from the tracker in `docs/agents/issue-tracker.md`, oldest first, one line each. Ask, one at a time: keep, kill, or do now. Kill closes it with a comment saying why. Do now: Skill `py-build`. Nothing else.
