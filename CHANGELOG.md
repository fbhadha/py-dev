# Changelog

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
