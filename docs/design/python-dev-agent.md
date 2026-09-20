# Design proposal: the Python developer agent

Status: sections 1 to 7 are the original draft; sections 8 to 15 record decisions taken with Firdaush on 2026-09-20 and supersede the draft where they conflict.

Built from [matt-pocock-skills.md](../research/matt-pocock-skills.md) and [python-craft-and-llm-faults.md](../research/python-craft-and-llm-faults.md), and your answers on 2026-09-20.

## 1. What it is, in one paragraph

A Claude Code agent (a `CLAUDE.md` persona plus a small set of skills in this repo) that behaves like a senior Python engineer pairing with you. It runs Matt Pocock's workflow verbatim through his plugin, uses Google's own ADK skills for framework knowledge, and adds one layer they both lack: Python craft and the deterministic checks that stop LLM faults at the commit. It has two modes chosen at intake, **guide** (you are vibe coding; it explains, recommends, and asks before anything hard to reverse) and **partner** (you are a pro; it moves faster and argues). Both modes produce a repo a human could pick up cold: same layout, same checks, same glossary, same ADRs.

## 2. The three sources and the seam between them

| Layer | Who maintains it | What it owns | How we get it |
|---|---|---|---|
| **Process** | Matt Pocock | grill → spec → tickets → implement → review; domain modelling; diagnosing bugs; architecture surveys; writing-for-agents | `claude plugins install mattpocock-skills`. Never fork. Auto-updates. |
| **Framework** | Google (adk-python repo) | building ADK agents, tools, workflows, HITL, eval, ADK style and review | Vendored copy of `adk-python/.agents/skills/` refreshed by a script; or a pointer that tells the agent to read them from the installed package source. Apache-2.0. |
| **Craft** | Us, in this repo | Python design rules, the repo baseline, the fault gates, intake, the two modes, the router | Written here, validated by this repo's CI, shipped as `python-dev` in this marketplace. |

The seam: our skills call his by name (`Call the Skill tool with "grilling"`), never copy his text. Where his skill has a TypeScript assumption (`setup-ts-deep-modules`, Effect, barrels) we write the Python counterpart and our router sends you to ours. Where a skill of his has a known hole (the `tdd` gap on glue code, `implement` never closing tickets, `code-review` sub-agents recursing), our wrapper carries the one-line fix in the invocation rather than editing his file, so updates never overwrite it.

**Licences.** His repo is MIT: copy, modify, redistribute freely; keep his copyright line in anything copied. Google's ADK skills are Apache-2.0: same freedoms, keep the notice and record changes. This repo's skills are Apache-2.0 already. All compatible.

## 3. The skills we write (first cut)

User-invoked unless marked.

| Skill | Job | Calls |
|---|---|---|
| `py-intake` (built) | Run once per repo, or when re-entering after a long gap. Detects greenfield vs brownfield, git remote (GitHub / GitLab / none), existing tooling, ADK presence, `CONTEXT.md`/ADRs. Asks the mode question. Runs `setup-matt-pocock-skills` with the tracker answer pre-filled. Installs or verifies the baseline (section 4). Writes `docs/agents/mode.md` and the `## Agent skills` block. For brownfield: runs `repowise init --no-prose --no-editor-setup -y`, reads the overview, the health report, the dead-code report and the decision candidates, grills the user on what those surfaced (each answer becomes a `CONTEXT.md` term or an ADR), and offers `improve-codebase-architecture` on the worst file next. No orientation page: the index is the orientation (ADR 0005). | `setup-matt-pocock-skills`, `codebase-exploration`, `code-health`, `domain-modeling`, `codebase-design` |
| `py-baseline` (model-invoked) | The reference for section 4: layout, pyproject, ruff/mypy/import-linter/pytest config, pre-commit hooks including the file-size, no-assert-less-test, and prompt-in-comment gates. Idempotent; merges into existing config, never overwrites. | none |
| `py-design` (model-invoked) | The Python craft reference: when a class earns its keep, Protocols at seams, composition over inheritance, parse-at-the-edge, exceptions as interface, one composition root, the adapter → normalised model → writer shape, the fault catalogue. Consulted by grilling, implement, and review. | `codebase-design` for vocabulary |
| `py-implement` (built) | Thin wrapper over his `implement`: adds "search `CONTEXT.md` terms before writing a new function", "tests are read-only during red→green", "run ruff/mypy/single test file after every slice", "close or update the ticket", "commit with the decision in the message". | `implement`, `tdd`, `py-design` |
| `py-review` (built) | His two-axis `code-review` plus a third axis, **Craft**, that runs the fault catalogue as labelled judgement calls and cites `py-design`. Guard line against sub-agent recursion. Report first; fix on request (ADK posture). In guide mode, each finding carries a one-sentence "why this matters". | `code-review`, `py-design` |
| `py-test-audit` (built) | Point it at a test directory: classifies every test as behavioural / tautological / instruction-shaped / mock-only / trivial, and proposes deletions and rewrites at the right seam. The direct answer to "my tests aren't real tests". | `tdd`, `py-design` |
| `adk-build` | Router into Google's ADK skills with our baseline applied: agent package layout, prompts in a file, tools as typed functions, unit tests with a faked model, evals as a separate tier. | vendored `adk-agent-builder`, `adk-style`, `py-baseline` |
| `ask-dev` | The router, like `ask-matt` but aware of all three layers and of your mode. In guide mode it also explains *why* the recommended next step is next. Answers "what do I type now?" | reads `ask-matt` |

Not written, because his are used as-is: `grill-with-docs`, `to-spec`, `to-tickets`, `wayfinder`, `diagnosing-bugs`, `prototype`, `research`, `handoff`, `wait-what`, `improve-codebase-architecture`, `domain-modeling`, `codebase-design`, `writing-for-agents`, `triage`, `resolving-merge-conflicts`, `wizard`.

## 4. The baseline `py-intake` guarantees

See research §3 for the full list. Non-negotiables: `uv` + committed lock; `ruff` with the fault-catalogue rule set; strict type checking; `pytest` with the assertion gate; `import-linter` layers contract; `pre-commit`; one CI workflow; `pydantic-settings`; `.env.example`; `CONTEXT.md`; `docs/adr/`; a `CLAUDE.md` that is pointers only. On brownfield repos the baseline is proposed as tickets, applied one at a time, each green before the next, because turning on strict mypy over 10k lines in one commit is the horizontal slice Matt warns about.

## 5. The two modes

| | Guide (vibe coder) | Partner (pro) |
|---|---|---|
| Grilling | Same rounds, but each question carries a plain-English "what this decides" line and the recommendation is chosen for safety. | His format unchanged. |
| Decisions | Anything hard to reverse (schema, public interface, dependency, deletion) stops and asks, with the one-way/two-way door named. | Asks only where the spec is silent. |
| Explanations | Every review finding and every ADR offer explains why in one sentence. | Terse. |
| AFK | Allowed only for tickets labelled by a grilled spec; the run ends in a PR with before/after evidence, never a merge. | Same rule; the user may widen it in `docs/agents/mode.md`. |
| Vocabulary | `wait-what` is suggested proactively when jargon density rises. | Never. |

Mode is a line in `docs/agents/mode.md`, set at intake, changeable any time. It is prose the skills read, not a config schema; Matt's "config is death" applies.

## 6. Issue tracker

GitHub Issues is free on all plans. Still, the default is **local markdown** under `.scratch/`, because it works with no account, no network, and no public planning noise. Matt's `setup-matt-pocock-skills` already supports GitHub, GitLab, and local, and the ticket format is the same on all three. We add one thing: `py-intake` offers a **migration** ("push these local tickets to the remote tracker") that reads `.scratch/<feature>/issues/*.md` and creates issues with the blocking edges, so starting local costs nothing later. Intake detects the remote from `git remote -v` and proposes accordingly.

## 7. How a session looks

**Greenfield, guide mode.** `/py-intake` → mode question, tracker (local), baseline installed, empty `CONTEXT.md` → `/grill-with-docs` on the idea (the agent proposes the adapter → model → writer shape from `py-design` when it fits) → `/to-spec` → `/to-tickets` → `/py-implement` per ticket in a fresh window → `/py-review` → you read the PR evidence.

**Brownfield, a 10k-line file.** `/py-intake` → Repowise index, health and candidates read back to you in plain words, a grilling round on the undocumented decisions → `/improve-codebase-architecture` finds the seams → grill one candidate → `/to-spec` (a refactor spec leaning on implementation decisions, not user stories) → `/to-tickets` as expand→migrate→contract → implement per ticket, each green → `/py-test-audit` on the old tests.

**Bug.** `/diagnosing-bugs` unchanged; `py-review` afterwards.

## 8. Decisions taken on 2026-09-20

| Question | Decision |
|---|---|
| Where the agent lives | This repo, shipped as a second plugin (`python-dev`) installed next to `mattpocock-skills`. (See §9 for what "plugin" means.) |
| Gate strictness on existing repos | Strict and blocking, on changed lines only, from day one. |
| Brownfield intake | Deep read of the repo, then an automatic grilling session about every decision the code makes that no `CONTEXT.md` or ADR explains. The agent acts as a senior engineer mentoring a junior: names the alternative, says why it may be better, and always pushes for the better design. |
| Deterministic bad-code detection | Ship a `py-health` suite (§10). Yes, this exists in the wild; it is several tools, not one. |
| Canonical example codebases | `psf/requests` for a deep module, `cosmicpython/code` for ports-and-adapters layering, `dlt-hub/dlt` for the data-engineering extract → normalise → load shape (§11). |
| ADK version | 2.x only for new code. A separate `adk-migrate` skill turns 1.x repos into 2.x, using Google's own migration notes. |

## 9. What "this repo as a plugin" means

Claude Code can load skills from a folder on your machine, or from a **plugin**. A plugin is just a Git repository with a small manifest file (`.claude-plugin/plugin.json`) that lists which skill folders it contains. When you run `claude plugins install <name>`, Claude Code downloads that repository, reads the manifest, and makes every listed skill available as a slash command. When the repository changes, the plugin updates itself.

This repository already has that manifest (`.claude-plugin/marketplace.json` and the skills under `skills/`). So "this repo as a plugin" means: we add the new Python skills as folders under `skills/`, add their names to the manifest, and you install this repository the same way you install Matt's. Two install commands, one machine, everything current. You never copy files by hand.

## 10. `py-health`: the deterministic bad-code suite

Two layers, split by what each needs to see. Whole-repo signals come from **Repowise** (verified in `docs/research/repowise.md`): it builds the dependency graph and git history once and scores every file from 49 deterministic markers calibrated against a defect corpus, with no model and no network. Line-level signals come from the established Python linters, which are instant on staged files and precise to the line. `py-health` runs both and writes one report: the Repowise score and its worst files, then the linter counts.

| Axis | Tool | What it catches |
|---|---|---|
| Health score, ranking, refactoring targets | `repowise health`, `--refactoring-targets`, `--trend` | Nesting, brain methods, god classes, low cohesion (LCOM4), I/O in loops across function boundaries, churn and ownership risk, untested hotspots once coverage is ingested. |
| Duplication | `repowise health` (`dry_violation`) | Near-duplicate blocks across files. |
| Dead code | `repowise dead-code --safe-only` | Modules nothing imports; unused exports are shown but never fail a run. |
| Test hygiene | `repowise health --format json`, advisory dimension (`assertion_free_test`, `mock_saturated_test`) | A test that runs code and checks nothing; a test that is mostly mock setup. |
| Change gate (CI) | `scripts/repowise_gate.py` over `ChangeReviewService` | The diff introduced a new health finding on a file it touched. Exit non-zero. The CLI cannot do this; the Python API can. |
| Lint, common bugs, prompt-shaped text | `ruff` with the fault-catalogue rule set | Mutable defaults, blind excepts, prints, commented-out code, TODOs without an owner, "This function" docstrings, boolean flags, banned `utils` imports. |
| Size | `pylint --enable=too-many-lines` | Modules over 400 lines (tests 150). Repowise has no file-length marker. |
| Architecture | `import-linter` layers contract | Domain importing adapters, cycles, entrypoints bypassing the application layer. |
| Types | `mypy --strict` error count | `Any` leakage, untyped surfaces. |
| Security | `bandit`, `detect-secrets` | Hard-coded secrets, injection, unsafe deserialisation. Repowise's own security layer is a 16-pattern floor and its doc says to run a real SAST. |
| Test strength | `mutmut` (mutation testing) | The direct answer to fake tests: it edits the code and re-runs the suite. A test that still passes never tested anything. Survivor rate is the score. |

`scripts/adr_sync.py` sits beside the gate: it re-indexes and binds each accepted ADR to its `## Scope` paths, which is what lets Repowise warn the agent when it edits a governed file (ADR 0005).

Retired from the earlier draft: radon and xenon (the Repowise score supersedes them), vulture (Repowise dead code), and every custom gate. Nothing in the suite is code we maintain except the 40-line change-gate script.

Mutation testing is slow, so it runs on demand and on a schedule. Repowise indexes in under ten seconds on the repos tried and runs in CI once per pipeline. Everything else runs in pre-commit on changed files.

Constraints that shape the baseline: Repowise is AGPL-3.0 (free for internal use; the gate script imports it, so it stays a development script and never ships inside a product), needs Python 3.11, phones home unless `DO_NOT_TRACK=1`, and by default writes editor config outside the repo, so every scripted call passes `--no-editor-setup`.

## 11. The canonical examples, and why these three

| Repo | Stars (order of magnitude) | What it demonstrates | Where it lives in `py-design` |
|---|---|---|---|
| `psf/requests` | ~50k, universally known | A **deep module**: eight public functions in `api.py` (`get`, `post`, ...) hiding ~6,000 lines of sessions, adapters, auth, cookies, retries. Callers learn one function; the implementation absorbs everything. Its `adapters.py` is also a textbook adapter seam (`HTTPAdapter` behind `BaseAdapter`). | The "what depth looks like" section. |
| `cosmicpython/code` | ~1k, but the reference implementation of the O'Reilly book *Architecture Patterns with Python* | **Ports and adapters** in plain Python: `domain/` (models, commands, events, imports nothing), `service_layer/` (handlers, unit of work, message bus), `adapters/` (repository, ORM, notifications, Redis), `entrypoints/` (Flask, Redis consumer), `bootstrap.py` as the one composition root, and tests split `unit/` `integration/` `e2e/`. This is exactly the layering the import-linter contract enforces. | The layout template and the layering rules. |
| `dlt-hub/dlt` | several thousand, production data-engineering library | The **extract → normalise → load** shape you described, at scale: `sources/` (one package per external system), `extract/` (resources, incremental state), `normalize/` (one place that turns raw items into a typed schema), `load/` and `destinations/` (one writer contract, many backends behind `common/destination/reference.py`). Adapter in, common shape in the middle, one writer out. | The worked example for data projects, and the counter-example for "each source has its own writer". |

The agent quotes these by path when it explains a recommendation, so a human can go and read the real thing.

## 12. Additional skills from these decisions

| Skill | Job |
|---|---|
| `py-health` | Run the suite in §10 and print one report: Repowise health, dead code, doc drift, the advisory test markers, then the mutation score. Writes nothing; Repowise keeps its own history (`health --trend`). Feeds the mentor's first grilling round at intake. |
| ~~`py-orient`~~ | Dropped (ADR 0005). Brownfield orientation is Repowise's index read through `codebase-exploration` and `code-health`, then a grilling round on the decision candidates and ungoverned hotspots it surfaces. |
| `adk-migrate` | Detect ADK 1.x patterns (`SequentialAgent`/`LoopAgent`/`ParallelAgent`, `_run_async_impl` overrides, direct `session.events.append`, broad `except` inside tools, rigid custom session tables) and rewrite them to 2.x (`Workflow` graphs, callbacks, yielded events, narrow excepts, schema update), as expand → migrate → contract tickets with the eval suite green at each step. |


## 13. Harness portability: how the agent is packaged for Claude Code, Copilot, and Codex

Verified 2026-09-20 against the Claude Code docs (CLI 2.1.278), the GitHub Copilot docs source (`github/docs`, CLI changelog to 1.0.86), the OpenAI Codex source (`openai/codex` at rust-v0.155.1), and the Agent Skills spec repo. Anything not exercised on a live harness is marked UNVERIFIED.

### 13.1 The plain answer

**Is this an agent you can select?** In Claude Code and GitHub Copilot, yes: a named agent called `python-dev` that you pick, and it takes over the session with its own persona. In OpenAI Codex there is no agent picker at all, so the same persona is written into the repo's `AGENTS.md`, which Codex reads on every turn; you don't select it, it is simply on in that repo.

**Does it know everything we discussed?** It knows what is written in files, and nothing else. An agent in these harnesses is a system prompt, a set of tools, a model, and the skills it can reach. It has no memory of this conversation. Everything we decided lives in three places it reads every session: the persona file, the skills, and the target repo's own docs (`CONTEXT.md`, ADRs, `docs/agents/`, the how-tos). That is by design: it is what makes the fresh-eyes test passable and what lets the same agent behave the same in three harnesses.

**Harness** is the word for the program that runs the model and its tools (Claude Code, Copilot, Codex). The **agent** is what runs inside it.

### 13.2 What you do in each harness

| | Claude Code | GitHub Copilot (CLI, VS Code, github.com) | OpenAI Codex |
|---|---|---|---|
| Install Matt's layer | `claude plugins install mattpocock-skills` | `npx skills@latest add mattpocock/skills` | `npx skills@latest add mattpocock/skills` |
| Install ours | `/plugin marketplace add fbhadha/py-dev` then `/plugin install python-dev@py-dev` | `npx skills@latest add fbhadha/py-dev` (skills only); plugin route `copilot plugin install fbhadha/py-dev` is documented but UNVERIFIED | `npx skills@latest add fbhadha/py-dev`; plugin route via `codex plugin marketplace add` reads our `.claude-plugin/plugin.json` in source but is UNVERIFIED |
| First run in a repo | `/py-intake` | `/py-intake` | `$py-intake` |
| Select the agent | `claude --agent python-dev`, or intake writes `"agent": "python-dev"` into `.claude/settings.json` so plain `claude` starts as it | `/agent` picker or `copilot --agent python-dev`; on github.com, the agents dropdown; intake writes `.github/agents/python-dev.agent.md` | Nothing to select. Intake writes the persona into `AGENTS.md`; you type `$ask-dev` to start |
| What the persona is, technically | The main thread's system prompt (replaces Claude Code's default prompt entirely) | A subagent with its own context that the main agent delegates to; `include-custom-instructions: true` lets it see `AGENTS.md` | A section of `AGENTS.md`, plus an optional `.codex/agents/py-reviewer.toml` role for fresh-context review |
| Skills reachable as | `/python-dev:py-review` (bare `/py-review` when unambiguous) | `/py-review` | `$py-review`, or the model opens `SKILL.md` |
| Hooks (fast in-session guards) | plugin `hooks/hooks.json` plus repo `.claude/settings.json` | repo `.github/hooks/python-dev.json` (the only file the cloud agent reads) | repo `.codex/hooks.json`, same JSON shape; return contracts partly UNVERIFIED |
| The floor that never degrades | pre-commit + CI in the target repo | same | same |

### 13.3 One source tree

The plugin is its own repository, `fbhadha/py-dev`, and its own marketplace. It was built under `plugins/python-dev/` in `fbhadha/Skills` and moved out once it had a release; the skill library there is unrelated to it.

```
fbhadha/py-dev/                         THE AGENT PLUGIN (one repository, three loaders); Google's ADK skills are installed, not vendored (decision 23)
├── .claude-plugin/plugin.json          read by Claude Code natively, by Codex and Copilot as a legacy manifest
├── .claude-plugin/marketplace.json     makes the repo installable: marketplace `py-dev`, one plugin, source `./`
├── agents/python-dev.md                the persona: session start, the routing table, build, review, health, Repowise policy (decisions 26 to 28)
├── agents/py-reviewer.md               craft-axis reviewer: Read/Grep/Glob/Bash only, no Agent tool (cannot recurse), no Edit
├── skills/                             py-intake, py-design, py-baseline, adk-migrate, pack-adk, pack-data-engineering (each with agents/openai.yaml)
├── hooks/hooks.json                    deny destructive git, stop-gate on red ruff
├── scripts/hooks/, scripts/find_skill.py   the hook scripts; the skill locator the door check uses
├── upstream.json                       every upstream skill we call by name, pinned (Matt Pocock's, Google's)
├── scripts/
│   ├── check_plugin.py                 frontmatter, openai.yaml sync, manifests, the skills list
│   └── check_upstream_skills.py        every skill we call by name exists at the pinned commit with the invocation we assume
├── CONTEXT.md                          this repo's own glossary
└── docs/adr/                           this repo's own decisions
```

### 13.4 What lives where, and why

| Container | Holds | Never holds | Why this container |
|---|---|---|---|
| **Persona** (`agents/python-dev.md`, rendered into the Copilot and Codex shells) | Identity, the guide voice, the two-tier pushback, the must-ask list, the checkpoints, the session-start read list, pointers to skills. About a page. | Craft knowledge, procedures over three lines, anything a linter can enforce, anything that changes per repo. | It is the only thing loaded before the first turn and the only thing a harness lets you select by name. Long prompts decay (research §1). |
| **Skills** (`skills/`) | Procedures and references, loaded on demand. | Persona voice; harness-specific tool names in operative steps (Matt dropped them in 1.2.3 so steps run on Codex). | The Agent Skills format is the only container all three harnesses read from the same files. |
| **Vendored ADK skills** (`plugins/adk-skills/`) | Google's skills verbatim. | Any hand edit. | Separate plugin keeps the licence boundary to one directory and lets ADK users take it alone. |
| **Target repo files** (written by `py-intake`) | `AGENTS.md` (pointers only) and `CLAUDE.md` = `@AGENTS.md`; `CONTEXT.md`; `docs/adr/`; `docs/agents/mode.md`, `issue-tracker.md`, `domain.md`; `docs/howto/`; `scripts/repowise_gate.py`, `scripts/adr_sync.py`; `pyproject.toml` tool tables; `.pre-commit-config.yaml`; `ci.yml`; `.env.example`; the harness shells (`.github/agents/`, `.github/hooks/`, `copilot-setup-steps.yml`, `.codex/hooks.json`, `.claude/settings.json`). | Copies of skill bodies. | This is the memory, and the floor. It works with no plugin installed, it is versioned with the code, and it is what a junior reader or a fresh session picks up cold. |
| **Hooks** | Fast in-session feedback: format after edit, deny `git push --force` and friends, deny a diff that weakens an existing test, block the turn ending while ruff/mypy on changed files are red, inject mode and last health score at session start. | The only enforcement of anything. | Hooks are best-effort and differ per harness (Copilot timeouts fail open; Codex contracts unverified). Pre-commit and CI are the truth. |

### 13.5 Two corrections to the earlier sections

1. **The Skill tool refuses Matt's user-invoked skills, so ours open the file instead.** `implement`, `to-spec`, `to-tickets`, `grill-with-docs`, `improve-codebase-architecture`, `setup-matt-pocock-skills`, `triage`, `wayfinder` and `ask-matt` carry `disable-model-invocation: true`; Claude Code blocks a Skill-tool call to them, Copilot honours the flag, Codex hides them unless typed. Nothing blocks reading the file. `scripts/find_skill.py <name>` locates the installed `SKILL.md` across the harnesses' install directories, and the persona reads it and follows it in the conversation as if invoked. The user never types a skill name; the agent runs the whole flow and the user only answers its questions (decision 21). The door check uses the same script, so "installed" means "found on disk", not "callable". `scripts/check_pocock_refs.py` checks every name we use exists upstream at the pinned version.
2. **"The plugin updates itself" is only half true.** Claude Code users get a new version only when `version` in `plugin.json` is bumped; Codex needs strict semver; Copilot auto-updates only first-party or opted-in marketplaces. A release is therefore a deliberate version bump here, not a push.

### 13.6 Degradation, honestly

| Harness | Lost | Fallback |
|---|---|---|
| Claude Code | Nothing relative to this design. `--agent` replaces the default system prompt, so the persona must carry its own operating basics (mirror the structure of `claude-security/agents/claude-security.md` in the official plugin repo). | Smoke-test `claude --agent python-dev -p` before each release. |
| Copilot CLI | Main-thread persona (it runs as a delegated subagent); no `initialPrompt`; skill-to-skill chaining reliability UNVERIFIED; `context: fork` only in VS Code. | `include-custom-instructions: true`; user types `/ask-dev`; wrappers keep gate-critical steps inline so a missed chain loses polish, not safety. |
| Copilot cloud agent (github.com) | Interactivity, so intake and grilling cannot run there; hook `ask` becomes `deny`; no plugins. | Run intake locally first; the persona's non-interactive rule: stop at any one-way door, write the question into the PR body, never merge. `copilot-setup-steps.yml` preinstalls `uv` and the gates. |
| Codex | Any selectable persona; the Skill tool; `context: fork`; `disable-model-invocation` (ignored); hook return contracts UNVERIFIED. | Persona in `AGENTS.md`; `$name` mentions; the `py-reviewer` role via `spawn_agent`; user-only skills hidden by `policy.allow_implicit_invocation: false` in `agents/openai.yaml`; hooks advisory until a Codex binary is tested. |
| Any other harness | Selection and hooks. | `AGENTS.md` pointer says "read and follow `.github/agents/python-dev.agent.md`"; `.agents/skills/` if it implements the standard; pre-commit and CI regardless. |

### 13.7 Flaws found in my own adversarial pass (the workflow's attack stage did not run)

- A plugin-root `settings.json` with `{"agent": "python-dev"}` would hijack every session in every repo where the plugin is enabled. Not shipped; the per-repo `.claude/settings.json` key is used instead.
- Shipping hooks in both the plugin and the target repo makes Copilot CLI run them twice. Accepted because every hook script is idempotent; a later non-idempotent hook would break this and CI will test for it.
- Hook payload field names differ per harness. A guard that cannot find the command string must exit 0 with no decision, otherwise Copilot's fail-closed pre-tool hook denies every shell call.
- Non-spec frontmatter (`disable-model-invocation`, `context: fork`) is rejected by the agentskills reference validator and by claude.ai upload. Acceptable: distribution is git and plugins. It closes those channels, and the README will say so.
- The `.agent.md` filename suffix for a Claude plugin agent is UNVERIFIED; ship `agents/python-dev.md` for Claude Code and render the Copilot copy separately.
- Name collision: `fbhadha/Skills` ships a `grill-me` that duplicates Matt's, and on Copilot and Codex skills resolve by name first-found-wins. Moving this plugin into its own repository (`fbhadha/py-dev`) closed that: `npx skills add fbhadha/py-dev` installs only this plugin's skills.
- `skills:` preload of a skill from another plugin is undocumented; we preload only our own `py-design`.

## 14. Decisions from the grilling session, 2026-09-20

| # | Decision | Consequence |
|---|---|---|
| 1 | Success is the **junior reader**: can read Python, not write it fluently, never saw the repo, cannot ask you. | Documentation is a deliverable with the same weight as code. |
| 2 | Three human docs per repo, each mechanically checked: `README.md` (commands executed in CI), `docs/architecture.md` (generated from the import-linter contract and ADRs), `docs/howto/add-a-<thing>.md` (mirrors a real `example/` package that compiles and has a test). Plus the **fresh-eyes test**: a new session, docs only, small feature, zero questions is the pass. | Docs that lie fail the build. |
| 3 | Docs are built at project start or at intake. They are the agent's operating manual. | The how-tos are how the agent builds. |
| 4 | The **shape** rule: a ticket that matches a how-to is built by template; one that touches anything outside the how-to's named layers is a new shape and the interview is mandatory. Mechanical trigger, plus the agent always asks "this looks like adding another X, correct?" before building. Grilling may end in "extend the existing shape". **Docs first, then code.** | See ADR 0001. |
| 5 | **Guide mode only.** Plain-language before and after every step, project vocabulary, one paragraph. Partner mode parked as a future one-line switch in `docs/agents/mode.md`. | Halves the surface to build and test. |
| 6 | **Must ask, every time:** push to main, delete files or data, migrations off a local test DB, new third-party dependency, public interface or schema change, spending money, one-way doors. **Blocked outright by hook:** force-push, hard reset, history rewrite. AFK is earned per ticket by a grilled spec and ends in a PR, never a merge. | See §13.4 hooks row. |
| 7 | **Scope pushback lives in the plan, not only the docs:** the spec's Out of Scope, the ticket's acceptance criteria, ADRs, `.out-of-scope/` for "never", and a `later` label in the tracker for "not now". Intake shows the `later` list each time and asks what to kill. | The checkpoint in #4 also checks the request against the current ticket. |
| 8 | **Two-tier pushback.** Design and taste: opinion with costs, twice, then defer and record an ADR when hard to reverse. Process discipline (scope creep, building without a how-to, skipping the interview on a new shape, tests after code, weakening a test): pushes hard, requires an explicit override in your own words, records it. | The mentor is opinionated, not nagging. |
| 9 | **Python only** for the craft layer in v1; Matt's process layer stays language-agnostic. | JS-heavy projects get process but no craft gates, and the agent says so. |
| 10 | **Craft core + knowledge packs + project how-tos.** Packs are reference-only skills with a fixed shape (trigger dependencies, shapes, canonical repo, extra checks, fault list), auto-selected at intake from `pyproject.toml`. v1 ships **two packs: ADK and data engineering**, plus the pack template. | Anyone can add a pack by copying the template; this repo's validator checks its shape. |
| 11 | **Stay coupled to Matt's plugin, with a door check.** Intake and `ask-dev` verify every upstream skill we name exists at session start and report the changelog entry if not. A one-line table here maps his skill → our use → last verified version. | See ADR 0004. |
| 12 | **Tracker: the remote decides.** GitHub remote → GitHub Issues; GitLab → GitLab Issues; no remote → **Backlog.md** (research: `docs/research/local-trackers.md`), accepting its Node dependency. Public repo → intake warns and offers local. | A new `issue-tracker-backlog-md.md` template mirrors Matt's GitHub one. |
| 13 | Test in your real GitLab environment; you report back. No synthetic fixture repo here. | Skills go to you checked only for loading and for their commands running. |
| 14 | **Short persona, deep library.** The persona is about a page of identity, voice, rules, and pointers; expertise lives in `py-design`, the packs, Matt's skills, and the checks. | See §13.4. |
| 15 | Portability as in §13: Claude Code is the reference experience, Copilot second, Codex the always-on `AGENTS.md` version. One plugin directory, three loaders. | Releases are version bumps. |
| 16 | **No Claude-Code-only feature ships without its repo-level fallback in the same change.** | Every skill carries its Copilot and Codex behaviour up front. |
| 17 | **`adk-migrate`: detect all 1.x patterns mechanically, force only what silently breaks on 2.x** (broad `except` in tools, direct event appends, ignored `run` overrides, rigid custom session stores) with hard pushback, **ticket the deprecated shells as `later`**, one agent per ticket as expand → migrate → contract with an ADK eval written first if none exists. | A repo with no evals gets "write the evals" as its first migration ticket. |
| 18 | **Repowise owns the whole-repo and change-level checks; per-line linters own the commit gate.** Repowise: health score, duplication, dead code, assertion-free tests, the CI change gate, brownfield orientation, decision records. Linters: ruff, pylint `too-many-lines`, mypy, import-linter, bandit, detect-secrets, mutmut. See `docs/research/repowise.md`. | radon, xenon, vulture and every custom gate are dropped. AGPL, `DO_NOT_TRACK=1`, `--no-editor-setup` are baked into the templates. |
| 19 | **No custom gates at all.** The last candidate (a test with no assertion) is Repowise's `assertion_free_test`. The only code we maintain in the check suite is the change-gate script over Repowise's Python API. | Q18 closed. |
| 20 | **One read path and one write path per kind of codebase knowledge; Repowise is the store for everything derived from the code** (structure, blast radius, why, health, dead code, change risk, doc drift). Humans and the agent write only ADRs (`docs/adr/`, Nygard headings, `## Scope`), `CONTEXT.md`, the how-tos and the tool tables. `docs/health/`, the orientation page and `py-orient` are gone; `docs/architecture.md` holds rules only; the Repowise plugin's six skills are called by name after a door check. | ADR 0005. `.repowise/` is gitignored; `scripts/adr_sync.py` binds ADRs to paths. |
| 21 | **The agent runs every flow, including Matt's user-invoked skills.** Where the Skill tool refuses a skill, the persona locates its `SKILL.md` with `scripts/find_skill.py` and follows it in the conversation. `ask-dev` names the next step and starts it. The user talks; they never type a skill name. | §13.5 correction 1 rewritten. `py-intake` runs `setup-matt-pocock-skills` itself with the answers it already knows. |
| 22 | **Session boundaries are explicit.** After `to-spec` and after `to-tickets` the agent runs Matt's `handoff` with the next step as its argument and tells the user to open a fresh session with the document; `py-implement` is one ticket per session and hands off the same way. A session that starts with a handoff path reads it, then `AGENTS.md`, and never re-asks what it answers. | Persona "Session boundaries"; `ask-dev` row. Keeps each build inside the smart zone Matt's `ask-matt` describes. |
| 23 | **Google's ADK skills are installed from Google's repo, not vendored.** `npx skills@latest add google/adk-python -s adk-agent-builder,adk-architecture,adk-debug,adk-style` puts them in `.agents/skills/` where `find_skill.py` finds them; the other seven are for adk-python contributors. The `adk-skills` plugin and `sync_adk_skills.py` are dropped. `adk-build` routes into Google's skills and adds the baseline; `adk-migrate` detects 1.x mechanically and forces only what silently breaks. | Same rule as Matt's and Repowise's: one maintainer, one install, called by name. Verified 2026-09-20 against adk-python at d57c84f (ADK 2.9). |
| 24 | **No rendered copies of the persona in this repo.** `py-intake` renders the Copilot agent file and the Codex `AGENTS.md` section in the target repo from the one persona file at intake time, so there is nothing here to drift and `render_harness_shells.py` is dropped. `check_upstream_skills.py` replaces `check_pocock_refs.py` and covers all three upstreams from `upstream.json`. | One persona file. CI clones the three upstreams at their pins on every change and reports drift on their default branches. |
| 25 | **Context budget is a design constraint.** Always-loaded cost is the persona plus every skill's name and description; bodies and `references/` load on demand. The persona stays near a page, descriptions near 40 words, worked examples and long tables live in `references/`, the door check is one script call, and human explainers (`docs/how-python-dev-works.md`) live outside the plugin. Measured numbers in the plugin README. | Smaller models get a shorter prompt; the same files work for every harness. Repowise's MCP `lean` profile is the lever on its side. |
| 26 | **Cut every skill that wrapped or duplicated an upstream** (2026-09-20, after the move to `fbhadha/py-dev`). `ask-dev`, `py-implement`, `py-review`, `py-health`, `py-test-audit` and `adk-build` are gone. Matt's `implement`, `tdd` and `code-review` are the procedures; Google's skills are the ADK procedure. What was ours in each (the Python build rules, the four-axis review recipe, the health commands, the test classes, the six ADK rules) moved into the persona, `py-design/references/test-audit.md` and `pack-adk`. | Six skills: `py-intake`, `py-design`, `py-baseline`, `adk-migrate`, `pack-adk`, `pack-data-engineering`. |
| 27 | **The routing table lives in the persona, always loaded.** The main goal is that the agent knows at every turn when to invoke what and how to keep the repo good by its how-tos. A skill it must remember to call cannot guarantee that; the persona can. Written as numbered steps, tables and exact commands so a smaller model can follow it. | Persona grows to about 3,000 tokens (from about 1,650). Skill descriptions fall from eleven to six. Net always-loaded cost is roughly level. |
| 28 | **Repowise through its CLI only, at named moments.** Its MCP surface is ten tool definitions per turn, the single largest context cost outside the plugin. The persona lists the moments Repowise may run (index behind HEAD, before editing a file, before naming something new, before review, health on request, intake orientation) and the exact command for each; never for browsing. Its six skills left `upstream.json`; intake no longer offers to wire `.mcp.json`. ADR 0005 stands: it is still the one store, reached one way. | Decision 20's "six skills called by name after a door check" is superseded on the access path only. |
| 29 | **Independent of `fbhadha/Skills`.** Nothing from the skill library's governance carries over: no JSON schema, validator, code of conduct, CODEOWNERS, DCO or PR template. Skill frontmatter is `name` and `description`. One `scripts/check_plugin.py` checks the plugin. | The library is one person's archive of skills they like; this is a product with a target repo depending on it. |

## 15. Build order

1. Plugin skeleton: manifest, persona, `py-design` (craft core with the fault catalogue and the three canonical repos), `py-baseline` templates, `ask-dev`.
2. `py-intake` with the health suite, the brownfield orientation and auto-grill, the tracker rule (including the Backlog.md template), the three human docs, and the harness shells.
3. `py-implement`, `py-review` (with the `py-reviewer` agent), `py-test-audit`.
4. `adk-build` and `adk-migrate` over Google's own skills (installed, not vendored; decision 23); the data-engineering pack and the pack template. (built)
5. CI: skill validation, invocation sync, upstream skill check against pinned commits (`scripts/check_upstream_skills.py`, all three upstreams), `claude plugin validate --strict` run locally before a release. (built; the persona drift check is dropped, decision 24)
6. First release: version 0.1.0, you run it on the GitLab repo, report back. (built: `CHANGELOG.md`; install with `--plugin-dir` from a clone of this branch)
