# Changelog

## Unreleased

- Moved out of `fbhadha/Skills` (where it lived under `plugins/python-dev/`) into its own repository and marketplace, `fbhadha/py-dev`. Install is now `/plugin marketplace add fbhadha/py-dev` then `/plugin install python-dev@py-dev`; from a clone, `claude --agent python-dev --plugin-dir /path/to/py-dev`. The design doc, ADRs, research, glossary and the three CI scripts came with it. Nothing in the persona, skills or templates changed beyond the repository name.

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
