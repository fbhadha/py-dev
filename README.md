# python-dev

A senior Python engineer as a selectable agent, in guide mode: it explains every step in plain words, builds by your repo's own how-tos, pushes back on scope creep, and keeps deterministic checks green. It runs the whole flow itself; you never type a skill name.

This repository is the plugin and its Claude Code marketplace. It stands on three maintained upstreams, installed from their own repositories and called by name, never copied:

| Upstream | Gives | Install |
|---|---|---|
| [Matt Pocock's skills](https://github.com/mattpocock/skills) | the process: grilling, spec, tickets, TDD, two-axis review, handoff | `/plugin marketplace add mattpocock/skills`, `/plugin install mattpocock-skills@mattpocock` |
| [Repowise](https://github.com/repowise-dev/repowise) | codebase intelligence: structure, blast radius, why, health, dead code, change risk; the one store for everything derived from the code | `pip install repowise`; `/plugin marketplace add repowise-dev/repowise`, `/plugin install repowise@repowise` |
| [Google's ADK skills](https://github.com/google/adk-python) | framework knowledge for Agent Development Kit repos | `py-intake` installs them when the repo depends on `google-adk` |

What is ours: the persona, the Python craft rules and fault catalogue, the repo baseline (tool tables, commit gate, CI, docs a junior reader can continue from), the intake that orients in an existing repo and grills you on its undocumented decisions, the implement, review, test-audit and health flows, ADK build and 1.x to 2.x migration, and knowledge packs.

How it all fits together: [docs/how-python-dev-works.md](docs/how-python-dev-works.md). Design and the decisions behind it: [docs/design/python-dev-agent.md](docs/design/python-dev-agent.md), [docs/adr/](docs/adr/), [docs/research/](docs/research/). The words this repo uses: [CONTEXT.md](CONTEXT.md).

## Install

Prerequisites in every harness: `uv`, Python 3.11 or newer, Matt Pocock's skills, and Repowise (`pip install repowise` or `uv tool install repowise`, plus its agent plugin: `/plugin marketplace add repowise-dev/repowise` then `/plugin install repowise@repowise` on Claude Code; `repowise agents add --target=codex` or `--target=vscode` elsewhere). Repowise is the agent's only store for everything derived from the code (ADR 0005 in this repo).

| Harness | Install | Select the persona |
|---|---|---|
| Claude Code | `/plugin marketplace add fbhadha/py-dev` then `/plugin install python-dev@py-dev`; also `/plugin install mattpocock-skills@mattpocock` (his marketplace) | `claude --agent python-dev`, or set `"agent": "python-dev"` in the repo's `.claude/settings.json` (py-intake offers to) |
| GitHub Copilot | `npx skills@latest add fbhadha/py-dev --all` and `npx skills@latest add mattpocock/skills --all` | py-intake writes `.github/agents/python-dev.agent.md`; pick it from the agent picker |
| OpenAI Codex | same two `npx skills` commands | no persona picker; py-intake writes the persona into `AGENTS.md`, skills are `$py-intake`, `$ask-dev` |

Then, in the target repo, say what you want; the agent runs `py-intake` first if the repo is not set up. You never type a skill name: the agent runs Matt's flows too, by reading their skill files when the harness refuses to invoke them (`scripts/find_skill.py`). After `to-spec` and after `to-tickets` it writes a handoff document and tells you to open a fresh session with it; each ticket is one session. It applies the baseline (`skills/py-baseline`), sets up the tracker, writes the three human docs, and on an existing repo orients itself and grills you about the undocumented decisions.

### How it works

- **You talk; it runs the flow.** At session start the persona decides the next step and starts it. Matt Pocock's flows it cannot invoke through the harness it runs by reading their skill files. You never type a skill name.
- **Intake first.** On a repo it has not seen, it explores and shows you the facts, sets guide mode and the tracker (your remote decides), applies the baseline and proves each check bites, indexes with Repowise, and writes the docs a junior reader needs: `AGENTS.md` pointers, `CONTEXT.md` glossary, ADRs, how-tos, the rules-only architecture doc. On an existing repo it reads the codebase back to you in plain words and grills you on the undocumented decisions it found.
- **Shapes and how-tos.** A how-to is the recipe for one kind of addition the repo makes, mirrored on an example that compiles. A ticket that fits a how-to is built by it; one that leaves its layers is a new shape and gets the interview first. Docs first, then code.
- **One ticket, one session.** Grill, spec and tickets in one window; then a handoff document and a fresh session per ticket. Each ticket is built test-first, checked after every slice, gated by Repowise before review, reviewed on four axes, committed with the decision in the message.
- **One store.** Everything derived from the code is read from Repowise. Decisions are written only as ADRs. Rules a machine can enforce live in `pyproject.toml`, not in prose.

## Try it from a clone

In the repo you want to work on:

```bash
claude --agent python-dev --plugin-dir /path/to/py-dev
```

That loads the plugin for the session only and starts with the persona. Its first turn runs `ask-dev`, which runs `py-intake` when the repo is not set up. Matt Pocock's and Repowise's plugins still need to be installed as above; the door check names whatever is missing.

## What is in the box

| Path | What |
|---|---|
| `agents/python-dev.md` | the persona: identity, guide voice, two-tier pushback, the ask-first and never lists |
| `agents/py-reviewer.md` | read-only craft reviewer used by `py-review` |
| `skills/ask-dev` | which command comes next, from the repo's state |
| `skills/py-design` | the craft rules, the fault catalogue, three canonical repos to cite |
| `skills/py-baseline` | the layout, tool tables, commit gate, CI, docs every repo gets, plus templates |
| `skills/py-intake` | set up a repo or re-orient in one: baseline, Repowise index, brownfield read-back and grill, the three human docs, harness shells; `py-intake later` reviews the parked list |
| `skills/py-implement` | one ticket per session, test-first, by the how-to, with the Repowise pre-edit checks, review, commit, and a handoff to the next session |
| `skills/py-review` | four-axis review: Standards and Spec (Matt's code-review), Change (Repowise), Craft (py-reviewer and the fault catalogue); report first |
| `skills/py-test-audit` | classify every test with evidence from Repowise's test-quality markers and mutation testing; propose deletions and rewrites |
| `skills/adk-build` | Google ADK 2.x work: routes into Google's own skills, installed from `google/adk-python`, and adds this baseline's layout, test tiers and craft rules |
| `skills/adk-migrate` | ADK 1.x to 2.x: mechanical detection, force only what silently breaks, evals first, expand, migrate, contract |
| `skills/pack-data-engineering` | knowledge pack for pipelines, sources, sinks and frames; `packs/TEMPLATE.md` is the shape for new packs |
| `skills/py-health` | one report on where the repo is ugly and what to fix first, from Repowise and the linters; writes nothing |
| `upstream.json` | the skills we call by name in Matt Pocock's, Repowise's and Google's repos, pinned; `scripts/check_upstream_skills.py` in this repo's CI verifies them |
| `hooks/hooks.json` | in-session guards (below) |
| `scripts/hooks/` | the hook scripts |
| `scripts/find_skill.py` | locates an installed skill's `SKILL.md` by name across Claude Code, Copilot and Codex install directories; the door check and the persona use it |

Version 0.1.0, a first release for testing on real repositories; see [CHANGELOG.md](CHANGELOG.md) for known gaps.

## Repository layout

```
.
├── .claude-plugin/plugin.json        # the plugin manifest
├── .claude-plugin/marketplace.json   # makes this repo installable with /plugin marketplace add
├── agents/                           # the persona and the read-only reviewer
├── skills/<name>/                    # the skills, each with agents/openai.yaml for Codex
├── hooks/, scripts/hooks/            # in-session guards (Claude Code)
├── scripts/find_skill.py             # locates an installed skill by name across harnesses
├── scripts/                          # validate_skills.py, check_invocation_sync.py, check_upstream_skills.py
├── schema/skill.schema.json          # frontmatter contract, enforced in CI
├── packs/TEMPLATE.md                 # the shape of a knowledge pack
├── upstream.json                     # the upstream skills we call by name, pinned
├── docs/adr/, docs/design/, docs/research/   # decisions, the design, verified research
├── docs/how-python-dev-works.md      # the long explainer
├── CONTEXT.md                        # the words this repo uses
└── .github/                          # CI, CODEOWNERS, PR template
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Security reports: [SECURITY.md](SECURITY.md).

## Hooks (Claude Code)

Best effort. Pre-commit and CI in the target repo are the enforcement; the hooks just shorten the loop.

| Event | Script | Does |
|---|---|---|
| `PreToolUse` on Bash | `guard_command.py` | denies force-push, hard reset, rebase, amend, filter-branch, `--no-verify`, `branch -D`. Fails open on any parse error. |
| `Stop` | `stop_gate.py` | blocks the turn ending while `ruff check` is red on the `.py` files changed this session. Only in repos with the baseline; never blocks twice in a row. |

Copilot and Codex get the same guards as repo-level hook files written by `py-intake`; Copilot's hooks fail open on timeout, Codex's hook contract is unverified, so treat both as advisory.

## Checks the baseline installs in a target repo

One read path and one write path per kind of knowledge. Everything derived from the code (structure, callers, blast radius, why, health, dead code, change risk, doc drift) is read from Repowise through its six skills. Humans and the agent write only ADRs, `CONTEXT.md`, how-tos and tool tables; `scripts/adr_sync.py` binds each ADR to the paths it governs so Repowise warns whoever edits them.

Line-level at commit: ruff (bugbear, blind except, security, print, commented-out code, prompt-shaped TODOs and docstrings, complexity, boolean flags, banned grab-bag modules), mypy strict on `src/`, import-linter layers, pylint module length, detect-secrets. Whole-repo and per-change: [Repowise](https://github.com/repowise-dev/repowise) health score, duplication, dead code, assertion-free tests, and a CI gate that fails when a diff makes a touched file worse. On demand: mutmut, bandit. Why this split: `docs/research/repowise.md`.

Repowise is AGPL-3.0 and is used as a development tool only. Set `DO_NOT_TRACK=1` (the templates do) to switch off its telemetry.

## Context cost

What a harness loads every turn from this plugin is the persona and every skill's name and description. Skill bodies load only when a skill runs, and `references/` files only when a skill opens them. Estimated at 3.6 characters per token:

| Always loaded | Tokens |
|---|---|
| Persona (`agents/python-dev.md`) | ~1,650 |
| 11 skill descriptions | ~630 |
| Total from this plugin | ~2,300 (was ~3,900 before the 0.1.0 trim) |

| Loaded on demand | Tokens |
|---|---|
| The largest skill body (`py-intake`, runs once per repo) | ~3,200 |
| A typical skill body | 800 to 1,500 |
| `py-design` references (fault catalogue, canonical examples, worked example) | ~3,300, opened one at a time |

Levers, in order of effect:

1. **Repowise's MCP surface** is the biggest cost outside this plugin: ten tool definitions per session by default. Its `lean` profile trims that to six for tight budgets (see `docs/agent/INTEGRATIONS.md` in the Repowise repo). Without MCP the skills fall back to the CLI and cost nothing per turn.
2. **Matt's and Google's skills** add their own descriptions when installed; only the four ADK skills are installed, and only in ADK repos.
3. **Packs** are selected per repo; an unselected pack costs its description only.
4. **Smaller models.** Everything here is plain steps and tables, nothing depends on a tool the harness might not have, and the persona fits in a page, so a smaller model can follow it. What a smaller model will do worse is the judgement in `py-review`'s Craft axis and in grilling; the mechanical checks (ruff, mypy, import-linter, the Repowise gate) do not get weaker.

## Licence

Apache-2.0. See `NOTICE` for what is called or vendored from elsewhere.
