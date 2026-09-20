# python-dev

A senior Python engineer as a selectable agent, in guide mode. It explains every step in plain words, builds by your repo's own how-tos, pushes back on scope creep, and keeps deterministic checks green. You talk; it runs the whole flow. You never type a skill name.

It is one plugin in the [Agent Skills](https://agentskills.io) format, with a manifest for each harness that can install it. It is small on purpose. Process comes from [Matt Pocock's skills](https://github.com/mattpocock/skills), framework knowledge from [Google's ADK skills](https://github.com/google/adk-python), codebase intelligence from the [Repowise](https://github.com/repowise-dev/repowise) CLI. All three are installed from their maintainers' repositories and called by name, never copied. What is here is what none of them has: a persona that knows when to run what, the Python craft rules and fault catalogue, the baseline every repo gets, an intake that orients in an existing repo and grills you on its undocumented decisions, the ADK 1.x to 2.x migration, and knowledge packs.

## Install

Prerequisites on the machine: `uv`, Python 3.11 or newer. Repowise is added to each target repo as a dev dependency by intake. Google's ADK skills are installed by intake only when the repo depends on `google-adk`.

Two plugins, from two marketplaces: Matt Pocock's process skills and this one. The commands differ by harness; the shape does not.

| Harness | Register and install | Start the agent in a repo |
|---|---|---|
| GitHub Copilot CLI | `copilot plugin marketplace add mattpocock/skills`, `copilot plugin install mattpocock-skills@mattpocock`, `copilot plugin marketplace add fbhadha/py-dev`, `copilot plugin install python-dev@py-dev` | `copilot --agent python-dev`, or the agent picker |
| Claude Code | `/plugin marketplace add mattpocock/skills`, `/plugin install mattpocock-skills@mattpocock`, `/plugin marketplace add fbhadha/py-dev`, `/plugin install python-dev@py-dev` | `claude --agent python-dev`; intake offers to make it the repo's default agent |
| From a clone, without installing | none | `claude --agent python-dev --plugin-dir /path/to/py-dev`, or `copilot plugin install /path/to/py-dev` |

The first session in a repo runs intake. Every session after that starts with the persona reading the repo's state and saying what comes next.

The plugin has been checked against both harnesses' plugin references (2026-09-20) and validated with Claude Code's plugin validator. It has not yet been run in a live session on either; the first one is the test.

## What happens

**First session in a repo.** The persona sees no `docs/agents/mode.md` and runs `py-intake`. It shows you a table of facts about the repo and asks if anything is wrong. It sets guide mode, runs Matt Pocock's setup skill with the answers it already knows (tracker from your remote: GitHub Issues, GitLab Issues, or Backlog.md when there is none; default triage labels; single-context docs), applies the baseline and proves each check bites, indexes with Repowise, and writes the docs a junior reader needs: `AGENTS.md` pointers, a `CONTEXT.md` glossary, `docs/adr/`, `docs/howto/`, a rules-only `docs/architecture.md`. On an existing repo it first reads the codebase back to you in six plain paragraphs (what it does, how it is layered, the three worst files and why, what nothing uses, what keeps getting bug-fixed with no decision behind it, which docs point at things that no longer exist) and grills you on what it found. Every answer becomes a glossary term, an ADR, or a `later` ticket.

**Every session after that.** The persona reads the repo's state, checks the upstream skills are installed, says in one line what comes next, and starts it. An idea gets Matt's `grill-with-docs`, then `to-spec` and `to-tickets` with a handoff and a fresh session between each. A ticket gets built: name the shape, ask Repowise what the files depend on, search before naming anything new, agree the seams, then Matt's `implement` with `tdd`, checks after every green, the change gate, a four-axis review, a commit that names the decision, a handoff. One ticket per session.

**The rule underneath.** A **shape** is a kind of addition the repo already knows how to make, described by one how-to in `docs/howto/` and mirrored on an example package that compiles. A ticket that fits a how-to is built by it. A ticket that leaves the how-to's layers is a new shape: the agent grills you, extends the how-to and its example first, then builds. Docs first, then code.

## What is in the box

| Path | What |
|---|---|
| `agents/python-dev.md` | The persona, the only hand-written copy. Session start, the routing table (situation, what to run), how to build a ticket, how to review, health, session boundaries, the Repowise policy, voice, pushback, the ask-first list, where knowledge lives. Always loaded. |
| `agents/py-reviewer.md` | Read-only craft reviewer the review step dispatches. Applies the fault catalogue to a diff. |
| `skills/py-intake` | Set up a repo or re-orient in one. Resumable; never overwrites what a person wrote. `later` reviews the parked list. |
| `skills/py-design` | The craft rules, the fault catalogue, three canonical repos to cite, the worked adapter-model-writer shape, the test-audit classes. |
| `skills/py-baseline` | What every repo gets: tool tables, pre-commit, CI, the Repowise change gate, the standard docs. With the templates intake copies. |
| `skills/adk-migrate` | Google ADK 1.x to 2.x: detect mechanically, force only what silently breaks, evals first, expand then migrate then contract. |
| `skills/pack-adk` | Reference for ADK 2.x repos: which Google skill to open for which job, the six rules this baseline adds. |
| `skills/pack-data-engineering` | Reference for pipeline repos: shapes, the canonical repo, extra checks, faults, tests. `packs/TEMPLATE.md` is the shape for new packs. |
| `hooks/`, `scripts/hooks/` | Two guards, the same scripts on every harness: deny force-push, hard reset, rebase, amend and `--no-verify`; stop the turn ending while ruff is red on files the session changed. Pre-commit and CI in your repo are the enforcement. |
| `upstream.json`, `scripts/find_skill.py` | Every upstream skill called by name, pinned; and the locator that finds an installed skill's `SKILL.md` wherever a harness put it. |
| `scripts/` | `check_plugin.py`, `check_upstream_skills.py`, `render_agents.py`: the checks CI runs. |

### How one plugin serves more than one harness

The skills are shared; they are plain `SKILL.md` folders every harness reads. What differs per harness is the manifest, the agent-file format and the hook-file format, so each harness gets its own copy of those three things and nothing else:

| Harness | Manifest | Agents | Hooks |
|---|---|---|---|
| Claude Code | `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | `agents/*.md` (the source) | `hooks/hooks.json` |
| GitHub Copilot CLI | `plugin.json` (Agent Plugins 1.0), `.github/plugin/marketplace.json` | `com.github.copilot/agents/*.agent.md`, rendered from `agents/` | `com.github.copilot/hooks/hooks.json` |

`scripts/render_agents.py` produces the rendered agent files and `scripts/check_plugin.py` fails CI when they are stale or the manifests disagree, so there is still one persona to edit. Adding a harness is one more row: a manifest, a render rule, a hooks file.

## How the agent decides

The persona carries one table: the situation the user is in, and what to run. Three kinds of thing can be run. A **Skill** is invoked by name: ours, Matt's model-invoked ones, Google's. A **File** is one of Matt's user-invoked skills (`grill-with-docs`, `to-spec`, `to-tickets`, `implement`, `handoff`, `improve-codebase-architecture`, `triage`, `wayfinder`, `wait-what`), which no harness lets the model invoke; the persona locates the file with `find_skill.py`, reads it and follows it in the conversation. A **CLI** command is run and its output shown. The table is always loaded, so the agent never has to remember to ask what comes next.

## Repowise, and why it is CLI only

Repowise is the one store for everything derived from the code: structure, callers, blast radius, health, dead code, change risk, doc drift, which ADR governs which file. Its MCP server puts every tool definition in context on every turn, used or not; how much that costs depends on the harness (caching and deferred tool loading soften it) and nobody here has measured it. The CLI costs only what a call returns, and behaves the same everywhere. The agent never uses the MCP server. Instead the persona names the only moments Repowise runs, and the command for each:

| Moment | Command |
|---|---|
| Session start, when the index is behind HEAD | `uv run repowise update` |
| Before editing a file | `uv run repowise why <file>`, `uv run repowise risk -t <file>` |
| Before naming something new | `uv run repowise search <name>` |
| Before review | `scripts/repowise_gate.py`, `repowise risk <range>`, `repowise impacted-tests <range>` |
| Health, on request | `health --refactoring-targets`, `dead-code --safe-only`, `doc-drift`, `decision health` |
| Orientation, at intake | `context`, `health`, `dead-code`, `decision candidates`, `doc-drift` |

Never for browsing: to find or read code the agent greps and opens the file. Decisions are written only as ADR files in `docs/adr/`, bound to paths by `scripts/adr_sync.py`; Repowise reads them, nothing writes to it. Repowise is AGPL-3.0 and a development tool only; the templates set `DO_NOT_TRACK=1`.

## Context cost

What a harness loads every turn from this plugin is the persona and six skill descriptions, about 3,400 tokens at 3.6 characters per token. Skill bodies load only when a skill runs (`py-intake`, the largest, about 3,000 tokens, once per repo); `references/` files only when a skill opens them. Matt's skills add their descriptions when installed. Google's four are installed only in ADK repos. Every step is a numbered instruction or a command, so a smaller model can follow it; what a smaller model does worse is the judgement in the review's Craft axis and in grilling, and the mechanical checks do not get weaker.

## What the baseline installs in your repo

Line-level at commit: ruff (bugbear, blind except, security, print, commented-out code, prompt-shaped TODOs and docstrings, complexity, boolean flags, banned grab-bag modules), mypy strict on `src/`, import-linter layers, pylint module length, detect-secrets. Whole-repo and per-change: the Repowise health score and a CI gate that fails when a diff makes a touched file worse. On demand: mutmut, bandit. Three scripts, copied once and never edited in the target repo: the change gate, the ADR binder, and a runner that executes the README's command blocks in CI so the README cannot rot.

## Working on this repo

```
pip install pyyaml
python scripts/render_agents.py           # after editing agents/*.md: regenerate the per-harness copies
python scripts/check_plugin.py            # frontmatter, manifests in step, the skills list, rendered copies current
python scripts/check_upstream_skills.py   # every upstream skill exists at its pin with the invocation we assume
claude plugin validate --strict .
```

Rules: `agents/python-dev.md` is the only hand-written persona; every other copy is generated and CI fails when it is stale. Keep it steps and tables; craft knowledge goes in skills. Call upstream skills by name, never copy them; add the name to `upstream.json` and bump a pin in its own commit after reading the upstream changelog. One read path and one write path per kind of knowledge (ADR 0005): anything derived from the code comes from Repowise, by CLI. No custom gates; a check is an established tool's rule in `skills/py-baseline/templates/pyproject-tools.toml`. Verify before you write; `docs/research/` records what was checked and when. A knowledge pack is `skills/pack-<domain>/` in the shape of `packs/TEMPLATE.md`, reference only. Before a release: the four commands above, a smoke test in a real repo on each harness, then the version in every manifest and a `CHANGELOG.md` entry.

Why things are the way they are: [docs/how-python-dev-works.md](docs/how-python-dev-works.md) for the long explainer, [docs/design/python-dev-agent.md](docs/design/python-dev-agent.md) for the design and every decision, [docs/adr/](docs/adr/) for the ones that were hard to reverse, [docs/research/](docs/research/) for what was verified, [CONTEXT.md](CONTEXT.md) for the words.

## Licence

Apache-2.0. `NOTICE` lists what is called from elsewhere.
