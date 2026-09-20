# Changelog

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
