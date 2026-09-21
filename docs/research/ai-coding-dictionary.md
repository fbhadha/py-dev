# Research: Matt Pocock's AI Coding Dictionary, and how this plugin uses it

Verified 2026-09-21 by cloning [mattpocock/dictionary-of-ai-coding](https://github.com/mattpocock/dictionary-of-ai-coding) at `251fec7ec3b08059e4203863024e6123090a54e3` (its `main`) and reading every file. The question: is it available to pull and use, and on what terms?

## What it is

- 69 entries, one file each, `dictionary/<Term>.md` (`Smart zone.md`, `Human-in-the-loop.md`, `AGENTS.md.md`). Each has YAML frontmatter with a `description` under 140 characters (the repo's `CLAUDE.md` requires it) and sometimes `aliases`; a body of at least 200 words that names the symptom the reader has felt; `_Avoid:_` and `_Usage:_` sections in the same shape as his `CONTEXT.md` glossaries. Entries link each other by relative file path.
- `README.md` is generated (`npm run generate`, `internal/generate-readme.ts`) from `internal/Curriculum.md`, which orders the terms into seven sections: The Model; Sessions, Context Windows & Turns; Tools & Environment; Failure Modes; Handoffs; Memory and Steering; Patterns of Work. CI (`.github/workflows/readme-fresh.yml`) fails when the README is out of sync.
- The published site is aicodingdictionary.com, and his skills link individual terms as `https://www.aihero.dev/ai-coding-dictionary/<slug>` (`smart-zone`, `context-pointer`, `human-in-the-loop`, `afk`, `effort`). Both hosts answered 403 through this build environment's proxy; the GitHub repository and `raw.githubusercontent.com` answered 200.
- It is not a skill and not a plugin: no `SKILL.md`, no `.claude-plugin/`, no marketplace file. `npx skills add` and `/plugin install` have nothing to install. It is a folder of Markdown.

## Licence

No `LICENSE` file, no `license` field in `package.json`, no licence line in the README or its template. No licence means the default: the author keeps every right, and GitHub's terms grant only viewing and forking on GitHub itself (choosealicense.com/no-permission). Reading and linking are fine; redistributing a copy, here or in a target repo, is not. His skills repository is MIT; the dictionary is not covered by that.

## What the plugin does with it

- **Links and reads, never copies.** The persona (`agents/python-dev.md`, voice section) fetches `https://raw.githubusercontent.com/mattpocock/dictionary-of-ai-coding/main/dictionary/<Term>.md` when the user asks what a word means or a decision turns on one, uses the `description` line as the plain word beside the term, and gives the user the page once as `https://github.com/mattpocock/dictionary-of-ai-coding#<slug>` (the README's own anchors: lowercase, punctuation dropped, spaces to hyphens, so `Smart zone` is `#smart-zone` and `AGENTS.md` is `#agentsmd`). The aihero.dev URLs would be the nicer page but could not be verified from here.
- **`CONTEXT.md` in a target repo holds that repo's words only.** AI-coding vocabulary (session, handoff, spec, ticket, grilling, smart zone) is not restated there; `AGENTS.md` and the intake report point at the dictionary instead.
- **`teach`'s first resource** when the topic is AI coding or this workflow.
- **Pinned in `upstream.json`** as a `reference` entry (`kind`, `dir`, `terms`); `scripts/check_upstream_skills.py` clones it at the pin and checks that every term the plugin names is a file there, and reports drift on `main` with `--latest`.

## UNVERIFIED

- The aihero.dev slug for every term (only the five his skills link were seen). The GitHub anchors are what the persona gives.
- Whether aicodingdictionary.com mirrors the repository at every commit.
- Whether the missing licence is an oversight; an issue asking would settle it, and nothing here changes if the answer is a permissive licence except that copying would then be allowed.
