# python-dev

A senior Python engineer and tech lead as a selectable agent. Before any code it tells you what it thinks you should build and why, pushes back on weak ideas, grills you on the open decisions, and writes a spec and tickets whose plans name the files, signatures and tests in the order it will write them. Then it builds one ticket at a time, tests first, explaining each step, and keeps deterministic checks green. No ticket, no code. You talk; it runs the whole flow. The only commands you type are the few of Matt Pocock's skills that only a person can start, and it tells you when and exactly what to type.

It is one plugin in the [Agent Skills](https://agentskills.io) format, with a manifest for each harness that can install it. It is small on purpose. Process comes from [Matt Pocock's skills](https://github.com/mattpocock/skills), framework knowledge from [Google's ADK skills](https://github.com/google/adk-python), codebase intelligence from the [Repowise](https://github.com/repowise-dev/repowise) CLI. All three are installed from their maintainers' repositories and called by name, never copied. The words of AI coding itself come from his [AI Coding Dictionary](https://github.com/mattpocock/dictionary-of-ai-coding), linked and read at runtime, never copied. What is here is what none of them has: a persona that knows when to run what, the Python craft rules and fault catalogue, the baseline every repo gets, an intake that orients in an existing repo and grills you on its undocumented decisions, the ADK 1.x to 2.x migration, and knowledge packs.

## Install

Prerequisites on the machine: `uv`, Python 3.11 or newer. Repowise is added to each target repo as a dev dependency by intake; a repo whose `requires-python` is below 3.11 gets it as a `uv tool` instead, loses the CI change gate until it moves, and gets a ticket saying so. Google's ADK skills are installed by intake only when the repo depends on `google-adk`.

Two plugins, from two marketplaces: Matt Pocock's process skills and this one. The commands differ by harness; the shape does not.

| Harness | Register and install | Start the agent in a repo |
|---|---|---|
| GitHub Copilot CLI | `copilot plugin marketplace add mattpocock/skills`, `copilot plugin install mattpocock-skills@mattpocock`, `copilot plugin marketplace add fbhadha/py-dev`, `copilot plugin install python-dev@py-dev` | `copilot --agent python-dev:python-dev -i "start"` (a plugin agent's id is `<plugin>:<agent>`; `/agent` lists it as python-dev). Without `-i` it waits for your first message |
| VS Code (Copilot Chat) | user settings `"chat.plugins.enabled": true` and `"chat.plugins.marketplaces": ["fbhadha/py-dev", "mattpocock/skills"]`; or install with the CLI above, which VS Code picks up | set the session target to Copilot and pick python-dev in the Agent dropdown. The plugin's hooks do not run here; the guards are the repo's CI and branch protection |
| Claude Code | `/plugin marketplace add mattpocock/skills`, `/plugin install mattpocock-skills@mattpocock`, `/plugin marketplace add fbhadha/py-dev`, `/plugin install python-dev@py-dev` | `claude --agent python-dev`; intake offers to make it the repo's default agent |
| From a clone, without installing | none | `claude --agent python-dev --plugin-dir /path/to/py-dev` |

The agent says it is running: its first reply opens with a status line, `python-dev 0.13.0 · branch <b> · guards <on|off|unknown> · tracker <t> · next: <step>`. No status line means you are talking to the default agent. Copilot's cloud agent on github.com is not interactive, so it cannot run intake or a grill; it loads a plugin only when the repo's `.github/copilot/settings.json` enables it.

The first session in a repo runs intake. Anything missing at the door (`uv`, `gh` or `glab` signed in, Node for Backlog.md, Google's skills) becomes a script Matt's `wizard` writes and you run in another terminal; only his plugin itself is installed by hand, because `wizard` is in it. The same skill walks you through the keys a project needs (`.env`, CI secrets) at intake; no key passes through the chat. Every session after that starts with the persona reading the repo's state and saying what comes next.

What has been run: Copilot CLI 1.0.88 installed this plugin with the commands above and ran its agent and hooks against a scripted model (2026-09-23); that run found the wrong agent id in these docs, hooks running in the plugin's folder instead of your repo, and the session-start line never reaching the model, all fixed in 0.11.0. VS Code's behaviour is from its source at the same date, not a live run. A real model on each harness is the smoke test, [docs/smoke-test.md](docs/smoke-test.md), run before every release.

## What happens

**First session in a repo.** The persona sees no `docs/agents/mode.md` and runs `py-intake`. It shows you a table of facts about the repo and asks if anything is wrong. It sets guide mode, gives you the one line that starts Matt Pocock's setup skill (only a person can start it) and answers its questions itself (tracker from your remote: GitHub Issues, GitLab Issues, or Backlog.md when there is none; default triage labels; single-context docs), applies the baseline and proves each check bites, indexes with Repowise, and writes the docs a junior reader needs: `AGENTS.md` pointers, a `CONTEXT.md` glossary, `docs/adr/`, `docs/howto/`, a rules-only `docs/architecture.md`. On an existing repo it first reads the codebase back to you in six plain paragraphs (what it does, how it is layered, the three worst files and why, what nothing uses, what keeps getting bug-fixed with no decision behind it, which docs point at things that no longer exist) and grills you on what it found. Every answer becomes a glossary term, an ADR, or a `later` ticket. Intake ends with one report, shown to you and used as the pull request's body: what is installed, which check stops what and when, what each file is for, how work goes from here, what Repowise found, and the first ticket. Nothing in it is a second copy in the tree.

**Every session after that.** The persona opens with its status line, reads the repo's state, and puts every message through one loop: say what kind of request it is (a new idea, a change to something already decided, a ticket, a bug, a question), then route it. No ticket, no code: a one-line fix gets a one-line ticket.

A new idea is shaped (`py-shape`) on a `shaping/` branch that holds decisions only. The agent reads the code first, then gives its view in one message: the problem, whether it should be built at all, what it would build and leave out, the alternatives it rejected, the risks and one-way doors, the size. Then it grills you in rounds of up to five numbered questions, each with its recommended answer, the reason and what the other answer costs, detouring to Matt's `research` for a fact from outside the repo and his `prototype` for a question talking cannot settle; an idea bigger than one session becomes a `wayfinder` map. In the same session it writes the spec (the design at the level of modules, types and interfaces, and the order of work) and cuts the tickets: you approve a breakdown table first, and every ticket carries its plan, the files, the signatures, the tests in the order they get written and where each expected value comes from, the commands. A change to something already decided goes back through the grill for that part, and the spec and tickets are updated before any code.

A ticket gets built (`py-build`), one per session: the plan checked against the code and shown to you ("Go?"), then one slice at a time, test first, the checks after every green and a line on what each slice added; the change gate, a four-axis review (`py-review`), the merge question, the ticket closed with evidence, a handoff for the next session.

**The rule underneath.** A **shape** is a kind of addition the repo already knows how to make, described by one how-to in `docs/howto/` and mirrored on an example package that compiles. A ticket that fits a how-to is built by it. A ticket that leaves the how-to's layers is a new shape: the agent grills you, extends the how-to and its example first, then builds. Docs first, then code.

## Skills only you can start

Six of the Matt Pocock skills python-dev routes to are marked so that only a person can start them (`disable-model-invocation: true`), and no harness lets an agent start one: Claude Code's Skill tool refuses them, and Copilot CLI's answers "Skill not found". So when one is due, the agent says why, gives you the exact line alone in a code block, says what the skill will ask and which answers it will give itself, and waits for you to send the line. Say "you run it" instead and it reads the skill's file and follows it, as earlier versions always did.

| Skill | When the agent gives you the line | What you type |
|---|---|---|
| `setup-matt-pocock-skills` | intake, once per repo, at the tracker step | `/mattpocock-skills:setup-matt-pocock-skills` |
| `wayfinder` | an idea too big for one session; then the first message of every session on its map | `/mattpocock-skills:wayfinder <the idea>`; later `/mattpocock-skills:wayfinder <map> <handoff path>` |
| `improve-codebase-architecture` | after the health step, when you want the refactor | `/mattpocock-skills:improve-codebase-architecture <worst file>` |
| `triage` | issues from other people | `/mattpocock-skills:triage what needs my attention?` |
| `wait-what` | any time a message did not land; the agent mentions it once a session | `/mattpocock-skills:wait-what` |
| `teach` | learning a topic over several sessions, in a new session opened in `~/learning/<topic>/`, never the repo | `/mattpocock-skills:teach <topic>` |

The line comes from `scripts/find_skill.py --typed <name>`. As checked on 2026-09-23 with Copilot CLI 1.0.88 and a scripted model: the `mattpocock-skills:` prefix is required there (the bare `/wayfinder` answers "Unknown command"), the line works with python-dev selected and as the start prompt (`copilot --agent python-dev:python-dev -i "/mattpocock-skills:wayfinder ..."`), and it is expanded only in an interactive session: `copilot -p` sends it to the model as plain text, whose skill tool then answers "Skill not found" (the behaviour in [github/copilot-cli#4438](https://github.com/github/copilot-cli/issues/4438)). Claude Code takes the prefixed line, and the bare one when no other command has that name. VS Code prefixes a plugin's skills with its name; use the Chat view, because the Agents window cannot start these skills yet ([microsoft/vscode#331477](https://github.com/microsoft/vscode/issues/331477)). Matt's skills installed with `npx skills add` instead of as a plugin have no prefix, and `--typed` prints the bare line.

His retired flow skills (`grill-with-docs`, `to-spec`, `to-tickets`, `implement`, `handoff`) still run if you type them. The agent first says which of its steps replaces each and what his leaves out (its view and pushback, the plan in each ticket, the plan check, the gates and the merge question), recommends its own, and follows his if you still want it.

## What is in the box

| Path | What |
|---|---|
| `agents/python-dev.md` | The persona, the only hand-written copy: the loop every message goes through (classify it; no ticket, no code), how it talks (its view first, exact plans, questions in rounds, full reasoning at decisions), how it pushes back, session start with the status line, the routing table, the line it gives you for a skill of Matt's that only a person can start, session boundaries, the branch rules, the Repowise policy, what to do when the plugin is wrong. Always loaded; CI keeps it under 14,000 characters, checks every skill is reachable from it, and checks its status line names the released version. |
| `agents/py-reviewer.md` | Read-only craft reviewer the review step dispatches. Applies the fault catalogue to a diff. |
| `agents/py-eval.md` | The scenario author the eval step dispatches when a ticket changed an agent: reads one targets file and nothing else, writes the eval set and config that Google ADK's simulated user plays, with a persona from a fixed list, under `tests/evals/` only. |
| `skills/py-intake` | Set up a repo or re-orient in one. Resumable; never overwrites what a person wrote. `later` reviews the parked list. |
| `skills/py-shape` | An idea to its tickets, in one session: its view and pushback, the grill in rounds, a research note, a prototype, a wayfinder map when it is more than one session, the spec (`references/spec.md`) and the tickets with plans (`references/ticket.md`); plus the revision route and the quick-ticket route. On a `shaping/` branch that holds decisions only. |
| `skills/py-build` | A ticket to its merge: the plan checked against the code and shown for a go, the shape, Repowise, the slices test first with `tdd`, the gates, the review, the merge question, the ticket closed, the handoff. |
| `skills/py-review` | The four axes on a diff: Matt's Standards and Spec, Repowise's Change, our Craft through `py-reviewer` and the test-diff check. |
| `skills/py-design` | The craft rules, the order to build things in (`references/planning.md`), the boundaries: timeouts, retries, parsing, errors, config, logs, contract tests (`references/boundaries.md`), the edge-case method: ten categories per behaviour, the ticket's table, property-test rules, mutation triage (`references/edge-cases.md`), the fault catalogue, three canonical repos to cite, the worked adapter-model-writer shape, the test-audit classes. |
| `skills/py-baseline` | What every repo gets: tool tables, pre-commit, CI, the Repowise change gate, the standard docs, and the health step. With the templates intake copies. |
| `skills/adk-migrate` | Google ADK 1.x to 2.x: detect mechanically, force only what silently breaks, evals first, expand then migrate then contract. |
| `skills/pack-adk` | Reference for ADK 2.x repos: which Google skill to open for which job, the six rules this baseline adds, the outside user (ADK's simulated user, six non-cooperative personas, the judges an API key can run, the report). |
| `skills/pack-data-engineering` | Reference for pipeline repos: four shapes with their how-tos, a tested example package (CSV to SQLite, incremental, re-runnable, 54 tests with a contract suite per port) that intake copies into the repo, design rules for time, money, re-runs, backfills, schemas and data quality, extra checks, sixteen faults, tests. Orchestrators, dbt and Spark are named as not yet covered. `packs/TEMPLATE.md` is the shape for new packs. |
| `hooks/`, `com.github.copilot/hooks/`, `scripts/hooks/` | The guards, the same scripts on every harness (below). |
| `upstream.json`, `scripts/find_skill.py` | Every upstream skill called by name and the dictionary terms the persona links to, pinned; and the locator that finds an installed skill's `SKILL.md` wherever a harness put it, and prints the line a person types to start one (`--typed`). |
| `scripts/` | `check_plugin.py`, `check_upstream_skills.py`, `render_agents.py`, `test_hooks.py`, `check_pack_examples.py`: the checks CI runs. |

### How one plugin serves more than one harness

The skills are shared; they are plain `SKILL.md` folders every harness reads. What differs per harness is the manifest, the agent-file format and the hook-file format, so each harness gets its own copy of those three things and nothing else:

| Harness | Manifest | Agents | Hooks |
|---|---|---|---|
| Claude Code | `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | `agents/*.md` (the source) | `hooks/hooks.json` |
| GitHub Copilot CLI | `plugin.json` (Agent Plugins 1.0), `.github/plugin/marketplace.json` | `com.github.copilot/agents/*.agent.md`, rendered from `agents/` | `com.github.copilot/hooks/hooks.json` |

`scripts/render_agents.py` produces the rendered agent files and `scripts/check_plugin.py` fails CI when they are stale or the manifests disagree, so there is still one persona to edit. Adding a harness is one more row: a manifest, a render rule, a hooks file.

## Guards

`main` changes only by a merge you said yes to. That is the whole rule, and the branch is what enforces it: the agent works on `ticket/<id>` (intake on `intake/baseline`), commits and pushes there freely, and when the ticket is done it shows you the diff summary, the commits and the check results and asks "merge to main?". Files outside `src/` and `tests/` are listed first in that summary, one sentence each, so a change to packaging, CI or the docs cannot hide in it. Mechanical layers hold the rule without the model's cooperation:

| Layer | Mechanism | What it catches |
|---|---|---|
| The hook asks before `main` | A pre-tool hook on shell commands answers `ask` for anything that lands on `main`: a commit while `main` is checked out, a merge into it, a push to it, `gh pr merge` or `glab mr merge`. The harness's own permission prompt is the yes. On a branch nothing asks. | The agent committing to `main` by habit, or merging without you |
| Nothing leaves the project unseen | The same hook asks for any `gh`, `glab` or `git push` aimed at a repo that is not this project's `origin`: another `-R` repo, a write through `gh api`, a gist, a push to a fork or a URL. Reads (`view`, `list`, `status`, `diff`) pass. The prompt names both repos. | Content from your repo going to a public issue, a gist or someone else's fork without your eyes on it |
| Branch protection on the server | Set at the end of intake with your yes (`gh api`, `glab api`): no push to `main`, no merge until the CI jobs are green. | Any tool or person, hook or no hook |
| The turn cannot end red | The stop hook runs ruff on the files the session changed and blocks until it is clean. | A turn ending mid-mess |
| No ticket, no code | In a repo intake set up, the hook asks before an edit to `src/`, `tests/` or any `.py` outside `prototypes/` when the branch is not `ticket/`, `prototype/` or `intake/`; its reason tells the agent to open the ticket first. | The agent coding straight from a chat message, which is what the default agent does |
| Shaping never builds | On a `shaping/` branch the command hook asks before a commit that carries `src/` or `tests/` files, and before an edit to them. | Product code written inside a grill or a wayfinder map, the failure Matt's own docs report most |

Plus the never list: force-push, hard reset, rebase, `--amend`, `--no-verify` and force-deleting a branch are denied outright, on any branch.

The guards are on as soon as the plugin is installed, on Copilot CLI and Claude Code; a session-start hook tells the model `python-dev guards active` with the plugin version, the branch and where the plugin's scripts are, and the persona puts the state on its status line. The hooks run in your project whichever folder the harness starts them in. VS Code does not run this plugin's hooks (it expands no plugin root for them), so each hook command exits quietly there instead of denying every tool call; in VS Code the guards are your repo's pre-commit, CI and branch protection, and the status line says `guards unknown`. `PYTHON_DEV_GUARD=off` silences the ask for one session; the denies stay. The hooks fail open on any error of their own, and `scripts/test_hooks.py` drives every decision in CI, in both harnesses' payload shapes, started from outside the repo the way Copilot CLI starts them.

Earlier versions (0.6.0 to 0.7.0) guarded individual files with ask, record and stop hooks and a commit-msg gate. The branch does the same job with one prompt per ticket instead of one per file, and about four hundred lines less hook code; see decision 39.

**Tests stay real.** Two checks in CI gate the merge: `scripts/check_test_diff.py` fails when the `tests/` diff deletes a test, adds a `skip` or `xfail`, or loses assertions, unless a commit message carries `test-override:` in your words; `diff-cover` fails when under 90% of the lines a change added are covered. The review's Craft axis reads the `tests/` diff for what a script cannot see: an assertion loosened in place, an expected value computed the way the code computes it.

## Repowise, and why it is CLI only

Repowise is the one store for everything derived from the code: structure, callers, blast radius, health, dead code, change risk, doc drift, which ADR governs which file. Its MCP server puts every tool definition in context on every turn, used or not; how much that costs depends on the harness (caching and deferred tool loading soften it) and nobody here has measured it. The CLI costs only what a call returns, and behaves the same everywhere. The agent never uses the MCP server. Instead the persona names the only moments Repowise runs, and the command for each:

| Moment | Command |
|---|---|
| Session start, when the index is behind HEAD | `DO_NOT_TRACK=1 uv run repowise init --no-prose --no-editor-setup --no-save-key -y` (never `update`: it writes editor files no flag stops) |
| Before editing, once per ticket | `uv run repowise risk -t <f1> -t <f2> ...` for every file the ticket touches; `why <file>` only for a file that call marks governed or bug-magnet |
| Before naming something new | `uv run repowise search <name>` |
| Before review | `scripts/repowise_gate.py`, `repowise risk <range>`, `repowise impacted-tests <range>` |
| Any command that prints pages | `uv run repowise distill <command>`: keeps failures and summaries, drops the pass parade, keeps the exit code |
| Health, on request | `health --refactoring-targets`, `dead-code --safe-only`, `doc-drift`, `decision health` |
| Orientation, at intake | `context`, `health`, `dead-code`, `decision candidates`, `doc-drift` |

Never for browsing: to find or read code the agent greps and opens the file. Decisions are written only as ADR files in `docs/adr/`, bound to paths by `scripts/adr_sync.py`; Repowise reads them, nothing writes to it. Repowise is AGPL-3.0 and a development tool only; the templates set `DO_NOT_TRACK=1`.

## Context cost

What a harness loads every turn from this plugin is the persona and nine skill descriptions, about 4,500 tokens at 3.6 characters per token (persona ~3,700, descriptions ~800), plus the guard line from the session-start hook. 0.11.0 spends about 700 more tokens a turn than 0.10.0 on the loop, the explaining and the pushback, which the 10,000-character ceiling had squeezed out, 0.11.1 about 400 more on the line it gives you for a skill of Matt's that only a person can start, 0.12.0 about 25 more on two clauses about edge cases, and 0.13.0 about 100 more on two clauses (every literal from a file open in this slice; you are the author); CI fails at 14,000, so it cannot creep further without a choice. Skill bodies load only when a skill runs (`py-intake`, the largest, about 7,700 tokens, once per repo; `py-shape` about 2,600, once per idea; `py-build` about 1,700, once per ticket); `references/` files only when a skill opens them. Matt's skills add their descriptions when installed. Google's four are installed only in ADK repos. The rest of the session's overhead is what the persona reads and runs before real work, and each of those is bounded: session start reads `AGENTS.md` only (`CONTEXT.md`, the tracker file and a how-to are opened when a step needs them); the index is refreshed only when `repowise status` says it is behind HEAD; the upstream door check caches a clean result for a day; one `risk` call covers every file a ticket touches; test, pre-commit and log output goes through `repowise distill`, which drops the passing noise and keeps the failures; intake's orientation reads at most three entry points. Every step is a numbered instruction or a command, so a smaller model can follow it; what a smaller model does worse is the judgement in the review's Craft axis and in grilling, and the mechanical checks do not get weaker.

## What the baseline installs in your repo

Line-level at commit: ruff (bugbear, blind except, security, print, commented-out code, prompt-shaped TODOs and docstrings, complexity, boolean flags, banned grab-bag modules), mypy strict on `src/`, import-linter layers, pylint module length, detect-secrets. Whole-repo and per-change: the Repowise health score and a CI gate that fails when a diff makes a touched file worse. Before review, on the modules a ticket changed: mutmut, each survivor triaged. Hypothesis for property tests. On demand: bandit. Three scripts, copied once and never edited in the target repo: the change gate, the ADR binder, and a runner that executes the README's command blocks in CI so the README cannot rot.

## Working on this repo

```
pip install pyyaml
python scripts/render_agents.py           # after editing agents/*.md: regenerate the per-harness copies
python scripts/check_plugin.py            # frontmatter, manifests in step, the skills list, rendered copies current
python scripts/test_hooks.py              # every hook decision against a scratch git repo
pip install pytest hypothesis ruff mypy && python scripts/check_pack_examples.py   # the pack example, under the baseline's checks
python scripts/check_upstream_skills.py   # every upstream skill exists at its pin with the invocation we assume
claude plugin validate --strict .
```

Rules: `agents/python-dev.md` is the only hand-written persona: the loop, the voice, the pushback, the routing table and the rules that hold on every turn, under 14,000 characters, which CI enforces along with every skill being reachable from it; every step list is a skill the table names; every other copy is generated and CI fails when it is stale. Call upstream skills by name, never copy them; add the name to `upstream.json` and bump a pin in its own commit after reading the upstream changelog. One read path and one write path per kind of knowledge (ADR 0005): anything derived from the code comes from Repowise, by CLI. No custom code-quality gates; a check is an established tool's rule in `skills/py-baseline/templates/pyproject-tools.toml`. The six scripts the baseline copies into a repo (change gate, ADR binder, README runner, test-diff check, literal check, eval-report check) are process, not lint. Verify before you write; `docs/research/` records what was checked and when. A knowledge pack is `skills/pack-<domain>/` in the shape of `packs/TEMPLATE.md`, reference only. Before a release: the commands above, [the smoke test](docs/smoke-test.md) with a real model on each harness someone uses, then the version in every manifest and in the persona's status line, and a `CHANGELOG.md` entry that records the smoke test.

Why things are the way they are: [docs/how-python-dev-works.md](docs/how-python-dev-works.md) for the long explainer, [docs/design/python-dev-agent.md](docs/design/python-dev-agent.md) for the design and every decision, [docs/adr/](docs/adr/) for the ones that were hard to reverse, [docs/research/](docs/research/) for what was verified, [CONTEXT.md](CONTEXT.md) for the words.

## Licence

Apache-2.0. `NOTICE` lists what is called from elsewhere.
