# Changelog

## 0.11.1 (2026-09-23)

Six of the Matt Pocock skills python-dev routes to can be started only by a person (`disable-model-invocation: true`), and no harness lets an agent start one. The agent used to read their files and follow them itself, and nothing told the user they existed or when to reach for one. Asked for: make the agent aware of when the user should start one and tell them what to do. Decision 53.

- **The agent gives you the line.** For the six still routed (`setup-matt-pocock-skills` at intake; `wayfinder` for an idea too big for one session and at the start of every session on its map; `improve-codebase-architecture` after the health step; `triage` for issues from other people; `wait-what` when a message did not land; `teach` for a topic over several sessions), the persona says why now, gives the exact line alone in a code block, says what the skill will ask and which answers it will give itself, and waits. Typed, the skill runs in the conversation under the persona's rules. "You run it" falls back to the old way: the agent reads the file and follows it.
- **The line is `/mattpocock-skills:<name>`**, printed by the new `scripts/find_skill.py --typed <name>` (`/<name>` when his skills were installed with `npx skills add`). Checked on Copilot CLI 1.0.88 with a scripted model: the model's skill tool answers "Skill not found" for these skills; the prefixed line loads them in an interactive session, with python-dev selected and as the `-i` start prompt; the bare `/wayfinder` answers "Unknown command"; `copilot -p` never expands a typed skill. Claude Code and VS Code (the Chat view) take the prefixed line by their docs; VS Code's Agents window cannot start these skills yet (microsoft/vscode#331477).
- **A map session starts with the line.** The handoff after charting or working a map gives the next session's first message: `/mattpocock-skills:wayfinder <map> <handoff path>`.
- **Typing one of his retired flow skills** (`grill-with-docs`, `to-spec`, `to-tickets`, `implement`, `handoff`) gets the step of python-dev's that replaces it, what his leaves out (the view and pushback, each ticket's plan, the plan check, the gates, the merge question), a recommendation, and then your choice.
- The intake report and a new README section list the lines. `upstream.json` records his plugin's name and gives the Copilot CLI and VS Code install lines, matching the README. `CONTEXT.md` gains **Typed skill**.
- **CI:** `check_plugin.py` fails a `Skill` call to a skill only a person can start, and a `User types` line for one the agent can start. `check_upstream_skills.py` checks his plugin's name at the pin, because it prefixes every line. `test_hooks.py` checks the typed lines (80 checks).
- The persona is about 13,500 characters (ceiling 14,000), about 400 tokens a turn more than 0.11.0. `docs/smoke-test.md` gains section 6.
- Smoke test for this release: not yet run on a live model. The scripted Copilot CLI 1.0.88 run covered the typed line, the refused skill tool, the bare name and `-p`.

## 0.11.0 (2026-09-23)

The first live test on GitHub Copilot felt like the default agent: no view of its own, no pushback, no grill, no tickets, nothing explained. Two causes. On Copilot it mostly did not run: the README's `copilot --agent python-dev` fails (the id is `python-dev:python-dev`), the hooks ran in the plugin's folder instead of the repo, and the session-start line never reached the model. And where it ran, the persona was written to say one sentence per step, defer after two objections, and hand the flow to Matt Pocock's skills, which only a person can start and which leave file paths and code out of specs and tickets by design. Decisions 47 to 52, ADR 0007.

- **A senior engineer's loop, every message.** The persona's first line says what kind of message it is (new idea, revision, ticket, bug, question, upkeep). No ticket, no code: a one-line fix gets a one-line ticket. It gives its view before any question (the premise, what it would build and leave out, rejected alternatives, risks and one-way doors, the size), asks in rounds of at most five numbered questions with a recommended answer, the reason and the cost, and explains every decision and plan in full; commands still come back as verdicts. `explain:` in `mode.md` is `decisions` (default), `teach` or `brief`.
- **Pushback in three tiers.** The premise (should this be built at all), design (two-way doors get a recommendation and a move on; a one-way door is never decided on a shrug, and an override becomes an ADR), process (refused until the user states the override in their own words).
- **python-dev owns the flow.** `py-shape` reads the code, gives its view, grills, writes the spec (`references/spec.md`: the design at the level of modules, types and interfaces, and the order of work) and cuts the tickets (`references/ticket.md`), in one session, after the user approves a breakdown table. Every ticket carries a plan: the files, the signatures, the tests in the order they get written with seams and expected-value sources, the commands. New routes: a revision (a change to something already decided is re-grilled and the spec and tickets updated before any code, never parked as scope creep) and a quick ticket (a small, clear change). `py-build` checks the plan against the code, shows it, waits for "Go?", then builds one slice at a time with a line after each. `grill-with-docs`, `to-spec`, `to-tickets`, `implement` and `handoff` are no longer called, and `upstream.json` drops them (its label for the Matt Pocock pin now says it is 54 commits past the v1.2.3 tag).
- **No ticket, no code, enforced.** A pre-tool hook asks before an edit to `src/`, `tests/` or any `.py` outside `prototypes/` when the branch is not `ticket/`, `prototype/` or `intake/`, in repos intake set up. Claude Code's matcher and Copilot's pre-tool entry both reach it.
- **Copilot fixes, from a live Copilot CLI 1.0.88 run and VS Code's source.** The CLI agent id is `python-dev:python-dev` (`copilot --agent python-dev:python-dev -i "start"` starts the session itself). Every hook enters the project from the payload's `cwd`; before this, on Copilot CLI the main-branch guard, the shaping guard and the stop gate never fired. The session-start hook prints JSON in both harnesses' shapes and names the plugin's scripts folder, which the persona uses instead of `${PLUGIN_ROOT}` (empty in the model's shell). Each hook command exits 0 when its script or `python3` is missing, because VS Code expands no plugin root for this plugin and, on its Local target, denied every tool call when the hook exited 2. `find_skill.py` also searches VS Code's `agentPlugins` folders. The README and intake give the VS Code setup (`chat.plugins.enabled`, `chat.plugins.marketplaces`, session target Copilot) and correct the cloud agent (it loads plugins enabled in `.github/copilot/settings.json`). The first reply opens with a status line (`python-dev 0.11.0 · branch · guards on|off|unknown · tracker · next`) so the user can tell it from the default agent.
- **Every agent in the repo works ticket-first.** The `AGENTS.md` template gains `## How work happens here` (no ticket, no code; shape first; plans in tickets; one branch per ticket), which Copilot's default agent reads too; intake proposes it for repos set up earlier.
- **The data-engineering pack is populated.** Four how-tos (add a source, a transform, a sink, a pipeline) and an example package they mirror: a CSV export loaded incrementally into SQLite, `Decimal` money, UTC times, bad rows counted never dropped, an upsert where the newer update wins, a cursor that moves only after the write, exit codes 0, 1, 2, and 44 tests with a contract suite per port. Intake copies them when the pack is selected. Ten design rules (time, money, re-runs, incremental state, backfills, schemas, run reports, determinism, personal data, frames at the edge) and eight more faults. `scripts/check_pack_examples.py` runs the example in CI under the baseline's pytest, ruff and `mypy --strict`. Orchestrators, dbt and Spark are named as not yet covered.
- **py-design** gains `references/planning.md` (walking skeleton first, riskiest next, prefactor first, expand-migrate-contract, vertical slices, what every plan step names, sizing) and `references/boundaries.md` (timeouts, retries, idempotency, error translation, parsing at the edge, money, time and ids, config, logs, async, one contract suite per port).
- **The persona's ceiling is 14,000 characters** (it is about 12,000; about 700 tokens a turn more than 0.10.0), and CI checks its status line names the released version.
- **Release gate:** `docs/smoke-test.md`, a fixed first-session script with the behaviour to expect, run by hand with a real model on each harness. CI: `test_hooks.py` drives Copilot payloads from outside the repo, the edit guard, the JSON session line and both manifests with the plugin root expanded and not (76 checks).
- Smoke test for this release: not yet run on a live model; the scripted Copilot CLI run covered install, the agent id and the hooks.

## 0.10.0 (2026-09-21)

The persona had grown to 23,400 characters, about 6,500 tokens loaded on every turn, three quarters of what the plugin side loads at all. Grilled and decided (design decision 46):

- **The persona is the router again.** It keeps identity, voice, pushback, session start, the routing table, the branch rules, session boundaries, the Repowise policy and three lines on filing a defect; it no longer carries a step list, a repeated command or a description of what the hook enforces anyway. Under 10,000 characters, about 2,800 tokens.
- **Three skills carry the steps:** `py-shape` (an idea to its ticket: the grill, research, prototype, the wayfinder map, the shaping branch), `py-build` (a ticket to its merge: the shape, Repowise, the seams, `implement` with `tdd`, the gates, the review, the merge question, the handoff) and `py-review` (the four axes). The health step lives in `py-baseline`, which already owned the gates. Nothing wraps or restates Matt Pocock's skills; ours hold only our steps and call his by name.
- **CI holds the line.** `check_plugin.py` fails when the persona passes 10,000 characters ("grow a skill, not the persona") or when a folder under `skills/` is named by no routing row.
- Section numbers moved: voice is section 5, the Repowise and one-place rule section 4, filing a defect section 8; `py-intake` and `py-baseline` point at the new numbers.

## 0.9.0 (2026-09-21)

From aihero.dev/skills' own grouping of Matt Pocock's skills (Getting Started, The Main Flow, Shaping, Upkeep, Productivity, Reference): the Shaping group was in `upstream.json` but nothing routed to it, so an idea went from the grill to a spec whatever the fog.

- **Shaping is a step of the flow, before any ticket.** The persona routes every idea, feature or new project through a shaping block: `grill-with-docs` first; his `research` as a background reader (one subagent, told to spawn nothing) that leaves a dated, cited note in `docs/research/`; his `prototype` on a `prototype/<slug>` branch under `prototypes/`, which the checks skip, for a question talking cannot settle; his `wayfinder` when the grill turns up more fog than one session can hold, worked one decision ticket per session and handed to `to-spec` when the map clears. Session count decides the route, not size. Shaping runs on a `shaping/<slug>` branch that holds decisions only and lands on `main` before `to-spec`, so every later session reads them; a one-session idea becomes one ticket on that branch renamed. Map sessions hand off like ticket sessions.
- **The hook asks before a commit on a `shaping/` branch that carries `src/` or `tests/` files.** Building inside a plan is the wayfinder failure his docs report most; the answer is a prototype branch or a ticket, unless the user asked in their own words. `test_hooks.py` drives it.
- **Steps only a person can take go through his `wizard`.** At the door check (`uv`, `gh` or `glab` signed in, Node for Backlog.md, Google's skills) and for a project's keys (every `.env.example` variable a person must obtain, every `secrets.*` CI reads), the agent writes the script that opens each page, captures each value blind and writes it where it belongs; the user runs it in another terminal. Only Matt's plugin itself is installed by hand, because `wizard` is in it. No key passes through the chat.
- **His `teach` is routed**, with the workspace named explicitly (`~/learning/<topic>/`, never the repo) and the AI Coding Dictionary, his skill pages and `py-design`'s canonical repos as its first resources.
- **His AI Coding Dictionary is the one definition for the words of AI coding.** The persona fetches an entry's `description` line when the user asks what a word means or a decision turns on one, and gives the page once. The repository states no licence, so it is linked and read, never copied. `upstream.json` gains a `reference` entry pinned to its commit; `check_upstream_skills.py` verifies the term files the plugin names exist there; `find_skill.py` and `check_plugin.py` skip reference entries. `docs/research/ai-coding-dictionary.md` records what was checked.
- Baseline: `docs/research/` and `prototypes/` in the files table; ruff `extend-exclude` and `force-exclude` and bandit skip `prototypes/` (re-running intake merges the keys into a repo set up earlier); `AGENTS.md`, `CONTEXT.md` and the intake report carry the pointers. Intake's greenfield finish routes through shaping instead of straight to `grill-with-docs`. Design decisions 43 to 45.

## 0.8.11 (2026-09-21)

- Intake's finish step starts by checking every earlier step's "done when" line. In the live run, "finish intake" made the agent skip the three human docs and the harness shells and go straight to committing.

## 0.8.10 (2026-09-21)

From the same live intake run, at the finish.

- **Whole-program checks leave the commit hook.** The baseline promised "changed lines only" but ran `mypy` over all of `src/` and `import-linter` over the whole program on every commit, so on a brownfield repo nothing could be committed until the layering existed; the agent uninstalled the hook to land intake. Now `mypy` checks the staged files with `follow_imports = silent`, and `import-linter` is a manual-stage hook run by CI (a dedicated step in both templates) and before review. Intake offers branch protection only once CI is green on the merged intake, and files a ticket otherwise.
- **Two more denies.** `PYTHON_DEV_GUARD=` inside a command (the agent tried it to get past the merge prompt; the variable is for a person's own shell) and `pre-commit uninstall`. Each has its own reason text saying what to do instead. The persona says what to do when no prompt can reach the user: stop and hand them the command.
## 0.8.9 (2026-09-21)

Issue #1: intake ended with commits, a merge summary and a question, and no one place saying what had been set up.

- **Intake ends with one report.** Step 10 now fills `skills/py-intake/templates/intake-summary.md` before it asks to merge: what is installed and each tool's job in plain words; the checks as a table of when each runs and what it refuses; every file intake wrote and when to read it; how work goes from here (a branch per ticket, the shape, tests first, the one yes at the merge); what Repowise found in the orientation step, with the ADRs written and the tickets parked; the first ticket, the health command, and how a pack gets selected later. Every placeholder is a fact an earlier step established, and a row for anything intake skipped is deleted, so the report says what happened, not what the template offers.
- **Shown and used as the pull request body, never committed.** Every fact in it lives in `AGENTS.md`, the tool tables, `docs/adr/` or Repowise; a copy in the tree would be the first `doc-drift` finding (persona section 12, ADR 0005). The merge summary no longer relists the new files, and the spoken "from here on I work on a branch per ticket" line is gone: the report's workflow section says it once. The template lives under `py-intake`, not `py-baseline`, because it never lands in a repo.
- Design decision 42.

## 0.8.8 (2026-09-21)

Three Repowise behaviours found by running intake on a scratch repo, each verified directly, each a plugin defect until now (decision 41, research record updated).

- **`repowise update` is never run.** It writes `.claude/CLAUDE.md` (which Claude Code loads on every turn) and `.vscode/` files, and ignores `REPOWISE_SKIP_EDITOR_SETUP`. The session-start, health and before-review refresh is `init --no-prose --no-editor-setup --no-save-key -y`, idempotent and seconds long. Intake names stray `.claude/CLAUDE.md` or `.vscode/mcp.json` files and proposes deleting them.
- **The map is `docs/agents/repowise-map.md`.** `generate-claude-md --output AGENTS.md` overwrote the whole file, pointers included; the agent lost its `AGENTS.md` mid-intake and rebuilt it from memory. Now `generate-claude-md --stdout` is cut to its markers into a file only Repowise writes; `AGENTS.md` links to it. Side effect: the map no longer loads through `@AGENTS.md` on every turn, about 1,500 tokens saved per turn on a small repo.
- **`docs/adr/` holds decisions only.** Every `.md` there becomes a Repowise decision, the template README included, which showed up as a candidate the agent had to dismiss. The template is now `docs/agents/adr-template.md`; the persona and intake write ADRs from it.
- `decision dismiss` gets `--yes`; intake runs `init` once and greps the saved output instead of running it three times.

## 0.8.7 (2026-09-21)

Found by running intake on a scratch pandas repo as a user would.

- **The baseline's dev group did not resolve.** `mypy>=2.3` names a version that does not exist, and `import-linter>=2.15` needs `rich>=14.2` while Repowise pins `rich<14`; `uv sync` failed and the agent spent twenty turns probing PyPI before pinning around it. Floors lowered to `mypy>=1.10` and `import-linter>=2.0` so `uv` picks the newest set that fits. New `scripts/check_template_deps.py` locks the template's dev group in CI, so a floor that stops resolving fails here, not in a user's intake. Intake now says what to do on a conflict: lower the floor, let `uv` pick, file the plugin defect, no probing.
- **One question fewer.** The agent asked whether to keep the default triage labels although intake had settled it; the tracker step now names every answer his setup skill's questions have.

## 0.8.6 (2026-09-21)

- **Nothing leaves the project without a prompt.** The command guard asks before any `gh` or `glab` command with `-R`/`--repo` naming a repo other than this project's `origin`, a `gh api` write under another repo's path, a gist, or a `git push` to a remote or URL that is not origin. Reads pass. The prompt names both repos. Origin is read from `git remote get-url origin` and normalized across https, ssh, `host/owner/repo` and `owner/repo` forms, GitLab subgroups included. Nine tests. The persona's plugin-bug report now says the hook asks as well.

## 0.8.5 (2026-09-21)

- **Filing a plugin bug shows the draft first.** The issue goes to a public repo, so the agent drafts title and body with nothing from the user's code, paths, hostnames, keys or data, shows it, and sends only the text the user approved.
- **Matt Pocock's ADRs now reach Repowise.** His `domain-modeling` writes an ADR as a title and a paragraph; Repowise reads that shape as a candidate only, so it governed nothing. The persona now says: his three gates decide whether an ADR is written, the baseline template (`## Status` Accepted, `## Scope` paths) decides how. `adr_sync.py` reports an ADR without a Status section instead of skipping it silently, and skips `docs/adr/README.md`, the template copy it used to fail on every run. Tests cover all three shapes.
- **When the plugin itself is wrong.** New persona section 11: a missing command or file, a hook blocking what it should not, two skills contradicting each other is a python-dev defect; say so, work around it once without improvising, and file it (`gh issue create -R fbhadha/py-dev` after a yes, or a `later` ticket titled `python-dev plugin: ...`). Never patch the plugin from a user's session.

## 0.8.4 (2026-09-21)

- **Intake recognises prior use of Matt Pocock's skills and of Repowise.** Two new facts-table rows: his files (`issue-tracker.md`, `domain.md`, `triage-labels.md`, the `## Agent skills` block, `backlog/`) and Repowise's traces (`.repowise/`, the managed section, editor wiring in `.mcp.json`, stored decisions with no ADR behind them, last sync). Step 4 runs his skill only for the missing piece; step 6 never re-runs `init` on an existing index, keeps the user's wiring, and confirms in one line before touching either; step 7 asks about each decision recorded in Repowise directly and turns the ones still true into ADRs, deprecating the rest.

## 0.8.3 (2026-09-21)

- **Cross-references are checked in CI.** `check_plugin.py` now fails when a skill or the persona names a `templates/`, `references/` or `scripts/` file that does not exist (here, in `py-baseline`, or on a line naming the upstream skill it belongs to), calls a skill that is neither in `skills/` nor in `upstream.json`, refers to a step or section number past the last heading, or is a pack missing one of the template's six sections. This is the class of bug 0.8.2 fixed by hand; it found one more (`pack-adk` had no faults table) on its first run.

## 0.8.2 (2026-09-21)

- **Packs verified and wired.** `docs/research/packs.md` records every library claim in `pack-adk`, `adk-migrate`, `pack-data-engineering` and the canonical examples, checked by fetching the file at Google's pinned ADK commit, dlt `devel`, requests `main` and the cosmic python repo. All hold. Two gaps fixed: intake's facts table promised the selected pack's extra checks would be applied in the baseline step, but the step had no line for it (now sub-step 8, which also writes `## Packs` in `AGENTS.md`); `pack-adk` lacked the template's Canonical repo, Extra checks and Tests sections, so `pytest-asyncio` and `asyncio_mode = "auto"` were never installed (now listed). An unverifiable "seven other skills" count is gone.

## 0.8.1 (2026-09-21)

- **Voice, for a user who does not code.** Persona section 8 rewritten as rules: one sentence before a step and one after, nothing when nothing changed; a technical word gets a plain word beside it once; a command's result is a verdict, not pasted output; a question is one line with the recommended answer and its cost; a number only when it changes a decision; no preamble, praise or menus. The persona's opening and description say who the user is. Intake's read-back is one message, one or two sentences per item, instead of six paragraphs.

## 0.8.0 (2026-09-21)

The branch is the guard. The per-file guard is gone.

- **`main` changes only by a merge you said yes to.** The persona works on `ticket/<id>` (intake on `intake/baseline`), commits and pushes there freely, and when the ticket is done shows the diff summary (files outside `src/` and `tests/` first), the commits and the check results and asks "merge to main?". Merge commits, never squash. ADR 0006, decision 39.
- **The hook asks only for what lands on `main`.** `guard_command.py` answers `ask` for a commit while `main` is checked out, a merge into it, a push to it, or `gh pr merge` / `glab mr merge`; on a branch nothing asks. The never list (force-push, hard reset, rebase, amend, `--no-verify`, force-delete) is denied as before. `PYTHON_DEV_GUARD=off` silences the ask, not the denies. The session-start line names the branch.
- **Deleted:** `guard_edit.py`, `record_edit.py`, the approvals and snapshot files, the `on` / `ask-once` / `off` modes, `protect-existing-files` in `mode.md`, and the baseline's `check_protected_commit.py` commit-msg hook. The stop gate keeps only the ruff check. Both hook manifests lose the edit PreToolUse and the PostToolUse entries.
- **Branch protection on the server**, offered at the end of intake with the exact `gh api` / `glab api` commands: no push to `main`, no merge until the CI jobs are green.
- **Tests stay real, in CI.** New baseline script `scripts/check_test_diff.py` fails a pull request whose `tests/` diff deletes a test, adds a `skip` or `xfail`, or loses assertions, unless a commit message carries `test-override:` in the user's words. `diff-cover` at 90% on the lines a change added, in both CI templates. Decision 40.
- `test_hooks.py` rewritten: the guard on `main` and on a branch in both payload shapes, the never list, the stop gate (blocks red ruff when ruff is on PATH), the session line, and the test-diff check on a deleted test, an added skip, fewer assertions, an override and a clean change.

## 0.7.0 (2026-09-21)

The guard asks once, and the agent's admin is bounded.

- **`ask-once` guard mode, the new default.** The first protected change of a session asks through the harness prompt; that yes covers every protected file for the rest of the session, and the persona then offers, in one line, to switch to `on` (per file, as before) or `off`. Intake's `mode.md` template writes `ask-once`; before `mode.md` exists the guard still asks per file. The commit-msg gate in the target repo demands `approved: <files>` only in per-file mode. Session start names the mode. `test_hooks.py` covers the first ask, the free second file and command, the stop gate and the commit gate.
- **Fewer, cheaper admin calls.** Session start reads `AGENTS.md` only and opens `CONTEXT.md`, the tracker file and how-tos when a step needs them. `find_skill.py --door-check` caches a clean result for a day (`--no-cache` to force) and skips Google's ADK upstream unless `google-adk` is a dependency. One `repowise risk -t <f1> -t <f2>` call covers every file a ticket touches, and `why` runs only on files it marks governed or bug-magnet. Test, pre-commit and log output goes through `uv run repowise distill <command>`, which keeps failures, summaries and the exit code and drops the passing noise; the persona never pastes more than twenty lines. Intake's orientation reads at most three entry points with `repowise context`.
- README, design decisions 37 and 38, and the explainer describe the modes and the bounds.

## 0.6.1 (2026-09-21)

Fixes from a walkthrough of intake with the 0.6.0 guards on.

- **The guard no longer blocks intake.** 0.6.0 protected every tracked file until intake wrote `mode.md`, so `uv add` (which also rewrites `uv.lock`) and `pre-commit run --all-files` (which reformats tracked source) left the stop hook refusing to end the turn. Now the protected list applies before intake as well, source files are never guarded, a shell command that asked records every tracked file it actually changed (from a snapshot the guard takes before the command runs), and formatters (`pre-commit run`, `ruff format`, `ruff check --fix`) never ask. `test_hooks.py` covers all three cases plus an unknown command rewriting a protected file, which still blocks.
- **Session start no longer re-indexes every turn.** The persona compared the commit named in the `AGENTS.md` managed section with HEAD; that commit only changes when `generate-claude-md` is re-run, so the check fired every session. It now reads `repowise status`. Refreshing the managed section is an explicit, protected edit offered at the health step.
- **Python below 3.11.** Repowise needs 3.11; intake now says what to do in a repo pinned lower (`uv tool install`, no CI change gate, a ticket to move).
- `.gitignore` added; a committed `__pycache__` removed. ADR 0004's body rewritten to match the code; a stale line about `.repowise/decisions.yaml` fixed; README context numbers corrected (~3,800 always loaded, not ~3,400).

## 0.6.0 (2026-09-20)

The no-unapproved-change rule is enforced by hooks.

- **Pre-tool `ask`.** `guard_edit.py` answers `ask` when the agent is about to edit, write or create over a git-tracked protected file (every tracked file before intake has written `docs/agents/mode.md`; the protected list after). `guard_command.py` does the same for shell commands that would write one (`sed -i`, redirection, `tee`, `cp`, `mv`, `uv add|init|lock`, `uv python pin`, `repowise generate-claude-md`), and keeps its outright denials of destructive git. The harness's own permission prompt is the yes.
- **One yes per file per session.** `record_edit.py` (post-tool) remembers the paths an approved edit or command touched, in a per-session file under the temp directory, so later edits to the same file pass without a prompt.
- **The turn cannot end with an unapproved change.** `stop_gate.py` now checks `git status` for modified protected files without a recorded approval and blocks, naming them, before its ruff check.
- **Commit gate in the target repo.** New baseline template `scripts/check_protected_commit.py`, a commit-msg hook: a commit touching a protected file needs `approved: <files>` in the message. Installed by the pre-commit template, which already installs the commit-msg stage.
- **On by default, and visible.** `session_start.py` prints `python-dev guards active` with the guard's mode; the persona's first step checks for it. `docs/agents/mode.md` gains `protect-existing-files: on`; `off` there (a protected edit, so the harness asks) or `PYTHON_DEV_GUARD=off` for one session turns the file guard off. Intake's last step tells the user this.
- Both hook manifests gain SessionStart, the edit-tool PreToolUse and PostToolUse. `scripts/test_hooks.py` drives every hook decision against a scratch git repo, in both payload shapes; CI runs it.

Unverified live: the argument key Copilot's edit and shell tools use (`path`, `file_path`, `command` are all read; anything else fails open) and whether Copilot's `agentStop` block reaches the model the way Claude Code's `Stop` does.

## 0.5.0 (2026-09-20)

- **Hard rule, in the persona and in intake: no change to an existing file without showing the change and getting a yes for that file.** Name it, one sentence on what and why, the diff, wait. One file, one yes. It overrides templates and upstream skills.
- **Brownfield intake.** New step 3 consolidates agent files before anything else: content from an existing `CLAUDE.md` or `.github/copilot-instructions.md` moves under a heading in `AGENTS.md`, the originals become one-line includes, each move approved; `.cursorrules` and the like are left alone and named. Every carried-over prose rule becomes a grilling question (enforced by a check: delete it; not enforced: should it be?). An existing CI workflow is never edited; ours goes beside it. A repo on `setup.py`, `requirements.txt`, Pipenv or Poetry gets "adopt uv" as its first ticket instead of a second packaging config. Steps renumbered.
- Matt Pocock's setup skill now always finds an `AGENTS.md` to write into, because agent files are consolidated before the tracker step.

## 0.4.0 (2026-09-20)

Laid out the way plugins are laid out for both harnesses, after reading GitHub's Copilot CLI plugin reference. 0.3.0's "ship everything inside py-intake" is undone.

- **One plugin, two manifests, shared skills.** `plugin.json` at the root (Agent Plugins 1.0, what Copilot CLI reads first) and `.claude-plugin/plugin.json` (Claude Code). `skills/` is shared. Claude Code's agents and hooks stay at `agents/` and `hooks/hooks.json`; Copilot's live under `com.github.copilot/agents/` (`*.agent.md`, rendered from `agents/` by `scripts/render_agents.py`) and `com.github.copilot/hooks/hooks.json` (camelCase events, `${PLUGIN_ROOT}`). `check_plugin.py` fails when the three manifests disagree or a rendered agent is stale.
- **Marketplace at both conventional paths**, `.claude-plugin/marketplace.json` and `.github/plugin/marketplace.json`, identical, CI-checked. Copilot CLI reads the Claude path as a fallback anyway; the second file is for people browsing the repo.
- **Install on Copilot is the plugin route**: `copilot plugin marketplace add fbhadha/py-dev`, `copilot plugin install python-dev@py-dev`, and the same for Matt Pocock's marketplace. `npx skills add` is no longer the documented way to get this plugin. Scripts and `upstream.json` are back at the plugin root; `${PLUGIN_ROOT}` is set for plugin hooks on Copilot and `${CLAUDE_PLUGIN_ROOT}` is accepted as its alias.
- **Intake step 8 shrinks**: the plugin delivers the Copilot agents and hooks, so the repo needs only the Claude Code `settings.json` pointer; on Copilot the user selects the agent.
- Copilot agent frontmatter follows the current reference: `python-dev` has `disable-model-invocation: true` (user-selected), `py-reviewer` has `user-invocable: false` (model-dispatched). `include-custom-instructions` is not in the reference and is gone.
- The persona's File legend gains a one-line fallback for finding `find_skill.py` when the plugin-root variable is not in the shell.

Verified against `github/docs` on 2026-09-20: manifest and marketplace resolution order, component locations, hook event names and payloads, variable expansion. Not verified: a live Copilot session. The bash tool's argument key in Copilot's `preToolUse` payload is assumed to be `command`; the guard fails open if it is not.

## 0.3.0 (2026-09-20)

Copilot first. Claude Code and GitHub Copilot are the two harnesses; Codex support is dropped for now.

- **Everything a Copilot user needs ships inside the `py-intake` skill**, because `npx skills add` installs skill folders and nothing else. `scripts/find_skill.py`, the two hook scripts and `upstream.json` moved into `skills/py-intake/`. Claude Code reaches them at `${CLAUDE_PLUGIN_ROOT}/skills/py-intake/...`, Copilot at `.agents/skills/py-intake/...`.
- **Rendered Copilot agent files**, `templates/copilot/python-dev.agent.md` and `py-reviewer.agent.md`, generated from `agents/*.md` by `scripts/render_agents.py`; `check_plugin.py` fails CI when they are stale. This reverses design decision 24 (no rendered copies in this repo): a copy that CI regenerates cannot drift, and without one Copilot has no persona.
- **Copilot hooks template**, `templates/copilot/hooks.json`, with the git guard as a `preToolUse` hook. The guard now reads Copilot's payload shape as well as Claude Code's and answers in both. Shape from the docs, unverified live, fails open.
- Intake step 8 writes the two agent files and the hooks file for Copilot; the Codex row is gone. `agents/openai.yaml` removed from every skill.
- The persona's Skill / File / CLI legend is harness-neutral; the first-turn instruction that Claude Code gets from `initialPrompt` is rendered as the first line of the Copilot copy, which has no initial prompt.
- README: Copilot install first.

Nothing has been run on Copilot yet. The agent file frontmatter, the hooks file shape and where `npx skills add` puts things are from the docs and from the earlier ADK-skills check.

## 0.2.0 (2026-09-20)

Its own repository, six skills instead of eleven, Repowise by CLI only, a persona a small model can follow.

- Moved out of `fbhadha/Skills` (where it lived under `plugins/python-dev/`) into `fbhadha/py-dev`, which is the plugin and its own marketplace. Install: `/plugin marketplace add fbhadha/py-dev`, `/plugin install python-dev@py-dev`; from a clone, `claude --agent python-dev --plugin-dir /path/to/py-dev`. Nothing from the skill library's governance came along: no schema, validator, code of conduct, DCO or PR template. One `scripts/check_plugin.py` checks the plugin.
- **Cut the skills that wrapped or duplicated an upstream.** `ask-dev` is now the persona's routing table, always loaded. `py-implement` is Matt Pocock's `implement` and `tdd` plus the persona's build rules. `py-review` is four lines in the persona: Matt's `code-review`, two Repowise CLI commands, the `py-reviewer` agent. `py-health` is five CLI lines in the persona. `py-test-audit` became `py-design/references/test-audit.md`. `adk-build` became the reference pack `pack-adk`; Google's skills are the procedure.
- **Repowise through its CLI, never its MCP tools.** Its six skills left `upstream.json` and the door check; the persona names the only moments Repowise runs and the exact command for each. Intake no longer offers to wire `.mcp.json`.
- **Persona rewritten** as numbered steps, exact commands and tables: session start, the routing table, building a ticket, review, health, session boundaries, the Repowise policy, voice, pushback, ask-first, where knowledge lives. About 3,000 tokens always loaded, against about 2,300 for the old persona plus eleven descriptions.
- Skill frontmatter is `name` and `description` only.

Known gaps carried from 0.1.0: Copilot and Codex hook files are not written yet; the Backlog.md commands come from its docs, not a live run; the Copilot agent file format is from the docs, untested. Nothing has been run on a real repository yet.

## 0.1.0 (2026-09-20)

First release, for testing on a real repo.

- Persona `python-dev` (guide mode, two-tier pushback, ask-first and never lists, session boundaries) and the read-only `py-reviewer` agent.
- Skills: `ask-dev`, `py-intake`, `py-baseline` with templates, `py-design` with the fault catalogue and canonical examples, `py-implement`, `py-review`, `py-test-audit`, `py-health`, `adk-build`, `adk-migrate`, `pack-data-engineering`, and `packs/TEMPLATE.md`.
- The agent runs every flow itself, including Matt Pocock's user-invoked skills, by locating their files with `scripts/find_skill.py`.
- Repowise is the single store for everything derived from the code; ADRs in `docs/adr/` are the single write path for decisions, bound by `scripts/adr_sync.py`.
- Google's ADK skills are installed from `google/adk-python`, not vendored.
- Hooks: git guard on Bash, stop gate on red ruff.
- CI in this repo: skill validation, invocation sync, upstream skill check against pinned commits of the three upstream repositories.

Known gaps: Copilot and Codex hook files are not written yet (pre-commit and CI are the guards there); the Backlog.md commands come from its docs, not a live run; the Copilot agent file format is from the docs, untested.
