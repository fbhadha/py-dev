# How python-dev works

One document, start to finish, for someone who has never seen this plugin. It explains the pieces, how a repo gets set up, what a working session looks like, and which file to open when you want to change something. Nothing here is the source of truth; every section says where the truth lives.

## 1. The pieces

Four things, in four places.

| Piece | Where | What it is |
|---|---|---|
| The persona | `agents/python-dev.md`; rendered for Copilot into `com.github.copilot/agents/python-dev.agent.md` by `scripts/render_agents.py` | About a page. Who the agent is, how it talks, what it asks before doing, what it refuses, where its knowledge lives. It is the system prompt when you start `claude --agent python-dev`. It holds no procedures. |
| Our skills | `skills/<name>/SKILL.md` | Six, loaded only when needed: `py-intake` (set a repo up or re-orient), `py-design` (the craft rules and fault catalogue), `py-baseline` (what every repo gets, with templates), `adk-migrate` (ADK 1.x to 2.x), and two reference packs, `pack-adk` and `pack-data-engineering`. |
| Upstream skills | installed from their maintainers' repos | Matt Pocock's process (grilling, spec, tickets, TDD, implement, review, handoff) and Google's ADK knowledge. We call them by name and never copy them. `upstream.json` lists every name we depend on. Repowise is a CLI tool the persona runs at named moments, not a skill we call. |
| The target repo's files | in your repo, written by `py-intake` | The memory. `AGENTS.md`, `CONTEXT.md`, `docs/adr/`, `docs/howto/`, `docs/architecture.md`, the tool tables, the checks, CI. They work with no plugin installed and are what a new person or a fresh session picks up cold. |

The rule that ties them together: **one place to read each kind of knowledge, one place to write it.** Structure, blast radius, history, health and dead code are read from Repowise. Decisions are written as ADRs. Words are in `CONTEXT.md`. Recipes are how-tos. Rules the machine can enforce are in `pyproject.toml`, not in prose. ADR 0005 in this repository states it.

## 2. How the agent runs everything

You talk; you never type a skill name. The persona carries a routing table (situation, what to run) and reads the repo's state at session start, then says in one line what comes next and starts it. Our skills and Matt's model-invoked ones run through the harness's Skill tool. Matt's user-invoked flows (`grill-with-docs`, `to-spec`, `to-tickets`, `implement`, `handoff` and the rest) are refused by that tool, so the persona finds their file with `scripts/find_skill.py` and follows it in the conversation. Repowise runs as a CLI command at the moments the persona names (session start when the index is behind, before editing a file, before naming something new, before review, health on request) and at no other time, because its MCP tools cost ten definitions every turn.

Two guards run in the session on Claude Code: a hook that denies force-push, hard reset, rebase, amend and `--no-verify`, and a hook that stops the turn ending while ruff is red on files the session changed. They are conveniences. The enforcement is pre-commit and CI in your repo.

## 3. What a repo gets, and who writes it

`py-intake` runs once per repo and again after a long gap. It never overwrites a file a person wrote. This is what it leaves behind:

| File | What it is for | Who writes it after intake |
|---|---|---|
| `AGENTS.md` (`CLAUDE.md` is `@AGENTS.md`) | Pointers only: read this first, these commands, these rules, these packs. Below its markers, Repowise keeps a managed section with the architecture map, entry points and the current health line. | You or the agent, above the markers; Repowise below. |
| `CONTEXT.md` | The glossary. The words the code, the tickets and the docs share. | Grilling adds a term whenever one is settled. |
| `docs/adr/` | Decisions that were hard to reverse, in Nygard headings with `## Scope` listing the paths each governs. Repowise reads them and warns whoever edits a governed path. | The agent writes one when you make such a decision, then runs `scripts/adr_sync.py`. |
| `docs/howto/add-a-<shape>.md` | One recipe per kind of addition the repo makes, mirroring a real example package that compiles and has a test. | The agent, at intake for the dominant shape, and whenever grilling settles a new shape. |
| `docs/architecture.md` | The layering rules and the composition root. Rules only; the live map is Repowise. | Rarely; when the layers change, with an ADR. |
| `docs/agents/mode.md`, `issue-tracker.md`, `domain.md` | Guide-mode settings; where tickets live and the commands for them; where the glossary and ADRs live. | Intake. |
| `pyproject.toml` tool tables, `.pre-commit-config.yaml`, CI | The checks: ruff, mypy strict, import-linter, module length, secrets at commit on changed lines; tests, README commands and the Repowise change gate in CI. | Intake, from `skills/py-baseline/templates/`. |
| `scripts/repowise_gate.py`, `adr_sync.py`, `run_readme_blocks.py` | The three scripts we maintain: fail CI when a diff makes a touched file worse; bind ADRs to paths; execute the README's command blocks so it cannot rot. | Intake copies them; nobody edits them in the target repo. |
| `.repowise/` | Repowise's index. Gitignored; rebuilt anywhere in seconds. | Repowise. |

### Where the how-tos come from

A **shape** is a kind of addition this repo already knows how to make: another source adapter, another tool, another agent. A how-to is the recipe for one shape, and it must mirror an example package that compiles, so the recipe cannot lie. On an existing repo, intake asks Repowise for the map, finds the most repeated module family, and writes the first how-to from the best existing example of it. On a new repo, the first how-to is written when the first grilling session settles the first shape. From then on the rule is mechanical: a ticket that fits a how-to is built by it; a ticket that leaves the how-to's layers is a new shape, and the agent grills you, extends the how-to and its example first, then builds. Docs first, then code. ADR 0001 states it.

## 4. A session, start to finish

**A new repo.** The agent runs intake: explores and shows you a facts table, sets guide mode, picks the tracker from your remote (GitHub, GitLab, or Backlog.md when there is none), applies the baseline and proves each check bites, indexes with Repowise, writes the docs above, wires the harness shells, commits in named groups. Then it starts `grill-with-docs` on your idea. When the idea is small, it builds it in the same session by the persona's build steps. When it is not, it runs `to-spec`, writes a handoff document and tells you to open a fresh session with it; that session runs `to-tickets`, hands off again; each ticket is then one fresh session.

**An existing repo.** Same intake, with two differences. The baseline lands as tickets, one file group at a time, because turning strict checks on over ten thousand lines at once never lands. And before anything else the agent reads the repo back to you from Repowise in six plain paragraphs (what it does, how it is layered, the three worst files and why, what nothing uses, what keeps getting bug-fixed with no decision covering it, which docs point at things that no longer exist) and then grills you on what it found. Every answer becomes a term, an ADR, a dismissed candidate, or a `later` ticket.

**One ticket.** The persona's build steps: name the shape and check the scope; `repowise why` and `repowise risk` on the files to be touched; search before naming anything new; agree the seams; then Matt's `implement` with `tdd` slices, tests read-only from red to green and the checks after every green; the full suite, pre-commit and the change gate before review; the review on four axes (Matt's Standards and Spec, Repowise's Change, our Craft through the `py-reviewer` agent); a commit that names the ticket and the decision; the ticket closed; a handoff for the next.

**Upkeep.** The health step is five Repowise commands and one report in plain words, pointing at the first refactoring target. Tests the user does not trust are classified by `py-design/references/test-audit.md`, with evidence, one action per test. Nothing writes a file; Repowise keeps the history.

## 5. What guide mode means

Before each step the agent says in one plain paragraph what it is about to do and why it matters here; after it, what changed. It uses the repo's own words. It has opinions: on design and taste it says what it would do and the cost, twice, then defers and records an ADR if the choice is hard to reverse. On process (scope creep, building without a how-to, skipping the interview on a new shape, weakening a test) it pushes hard and needs your override in your own words. It asks before pushing to main, deleting, migrating anything but a test database, adding a dependency, changing a public interface, spending money. Unattended runs happen only on a ticket that came out of a grilled spec, and they end in a pull request, never a merge.

## 6. Where to change what

| You want to change | Open |
|---|---|
| How the agent talks or what it refuses | `agents/python-dev.md` |
| What every repo gets | `skills/py-baseline/SKILL.md` and its `templates/` |
| The craft rules or the fault catalogue | `skills/py-design/` |
| What the agent does at session start, how it builds, reviews, measures health, when it runs Repowise | `agents/python-dev.md`, sections 1 to 7 |
| Intake or the ADK migration | that skill's `SKILL.md` |
| Which upstream skills we depend on | `upstream.json`, then `python scripts/check_upstream_skills.py` |
| Domain knowledge for a kind of repo | a new `skills/pack-<domain>/` in the shape of `packs/TEMPLATE.md` |
| Why something is the way it is | `docs/design/python-dev-agent.md` and `docs/adr/` in this repository |

Before a release: `python scripts/render_agents.py`, `python scripts/check_plugin.py`, `python scripts/check_upstream_skills.py`, `claude plugin validate --strict .`, and a `claude --agent python-dev --plugin-dir . -p` smoke test.
