---
name: py-baseline
description: "The baseline every Python repo gets: layout, pyproject tool tables, pre-commit, CI, the Repowise change gate, agent docs. Use when setting up or checking a repo's tooling, checks or docs. Merges, never overwrites."
---

# Python baseline

The skeleton every repo this agent touches ends up with, so a junior reader can pick up any of them the same way. `py-intake` applies it; anything else consults it.

## Files

| File | Purpose | Template |
|---|---|---|
| `pyproject.toml` `[tool.*]` tables | ruff, ruff-format, mypy strict, import-linter layers, pytest, coverage | `templates/pyproject-tools.toml` |
| `uv.lock`, `.python-version` | committed; CI installs with `uv sync --frozen` | created by `uv` |
| `.pre-commit-config.yaml` | ruff, ruff-format, mypy on changed files, import-linter, pylint too-many-lines, detect-secrets | `templates/pre-commit-config.yaml` |
| `.github/workflows/ci.yml` (or the GitLab equivalent) | pre-commit on the files the PR changed, the whole test suite, then the Repowise change gate | `templates/ci.yml`, `templates/gitlab-ci.yml` |
| `scripts/repowise_gate.py` | the CI change gate over Repowise's Python API | `templates/repowise_gate.py` |
| `scripts/run_readme_blocks.py` | executes every ```bash ci``` block in `README.md` in CI | `templates/run_readme_blocks.py` |
| `scripts/check_protected_commit.py` | commit-msg hook: a commit that changes a protected file must carry `approved: <files>` | `templates/check_protected_commit.py` |
| `.secrets.baseline` | detect-secrets baseline, created by `uv run detect-secrets scan > .secrets.baseline` | created by `detect-secrets` |
| `.env.example` | every key the code reads, with a comment, no values | `templates/env.example` |
| `AGENTS.md` | pointers only, under 40 lines, above the Repowise managed section (`repowise generate-claude-md --output AGENTS.md`) | `templates/AGENTS.md` |
| `CLAUDE.md` | one line: `@AGENTS.md` | `templates/CLAUDE.md` |
| `CONTEXT.md` | the glossary, Matt Pocock's format, created lazily | `templates/CONTEXT.md` |
| `docs/adr/` | decisions, Nygard headings with `## Status` Accepted and `## Scope` paths; Repowise reads them | `templates/adr-template.md` |
| `scripts/adr_sync.py` | re-indexes and binds each accepted ADR to its Scope paths in Repowise | `templates/adr_sync.py` |
| `docs/agents/mode.md` | the mode line the skills read | `templates/mode.md` |
| `docs/howto/add-a-<shape>.md` | one per shape, mirrors an `example/` that compiles | `templates/howto-template.md` |
| `docs/architecture.md` | the layering rules and the composition root only; the live map is Repowise | `templates/architecture.md` |
| `README.md` | run, test, where to start reading; commands in ```bash ci``` blocks are executed in CI | `templates/README-skeleton.md` |

## The gates

Two layers. Line-level tools run at commit on the changed files. Repowise (`docs/research/repowise.md` in this repo) runs whole-repo in the persona's health step and once per CI pipeline as the change gate. Always its CLI, never its MCP tools. Custom code: one script, the change gate, because Repowise's CLI cannot do it and its Python API can.

| Fault | Tool | Where it runs |
|---|---|---|
| Module over 400 lines (tests 150) | `pylint --disable=all --enable=too-many-lines --max-module-lines=400` | commit |
| `utils`, `helpers`, `common`, `misc` modules | ruff `TID251` banned imports plus an import-linter `forbidden` contract | commit |
| Prompt-shaped docstrings and comments | ruff `D401` (non-imperative docstring), `TD002`/`TD003` (a TODO must name an author and an issue), `FIX002` (no TODO left in code), `ERA001` (commented-out code) | commit |
| Swallowed exceptions, mutable defaults, prints, string SQL, secrets | ruff `BLE`, `B`, `T20`, `S`; `detect-secrets` | commit |
| Complexity, flags, too many parameters | ruff `C901`, `PLR091x`, `FBT` | commit |
| An existing protected file changed without the human's yes | in-session: the plugin's hooks make the harness ask, once per file per session, and refuse to end a turn with an unapproved change; at commit: `scripts/check_protected_commit.py` needs `approved: <files>` in the message | session; commit |
| Layering | `import-linter` layers contract | commit |
| Types | `mypy --strict` on `src/` | commit |
| A change made a touched file worse (new nesting, god class, I/O in a loop, duplication, swallowed exception) | `scripts/repowise_gate.py`: `ChangeReviewService.review()` on `origin/main..HEAD`, fails when `introduced_total > 0` | CI |
| Health score, ranking, what to refactor first, trend | `repowise health`, `--refactoring-targets`, `--trend` (its own history; nothing written to docs) | health |
| Duplication | `repowise health` (`dry_violation`) | health |
| Dead code | `repowise dead-code --safe-only` fails on unreachable files; unused exports are listed, never fail | health |
| Test with no assertion, mock-saturated test | `repowise health --format json`, advisory dimension (`assertion_free_test`, `mock_saturated_test`) | health; review |
| Docs that name paths, links or commands the tree no longer has | `repowise doc-drift` | health |
| Security | `bandit` (Repowise's 16-pattern scan is a floor, not a scanner) | health |
| Fake tests (pass on any mutation) | `mutmut`, on the module named; the score is reported in the health step and read at review, not stored | health |
| Weakened test (assertion loosened, test deleted, skip added) | the review's Craft axis on the `tests/` diff, and a `CODEOWNERS` line on `tests/` requiring the owner's approval | review; platform |

## Where Repowise reads and writes (ADR 0005 in this repo)

Reads: the source tree, git history, `docs/adr/*.md` (Nygard headings; `## Status` Accepted makes it govern, `## Scope` paths are bound by `scripts/adr_sync.py`), `# WHY:` / `# DECISION:` comments, and `coverage.lcov` when ingested with `repowise coverage add coverage.lcov`. Writes: `.repowise/` (gitignored, rebuilt anywhere in seconds) and the managed section between `REPOWISE:START` and `REPOWISE:END` in `AGENTS.md`. Nothing else. No `docs/health/`, no orientation page, no decisions store in git: the ADR files and the code are the truth and the index is derived from them.

Repowise rules: every scripted call is `DO_NOT_TRACK=1 repowise <cmd> --no-editor-setup` where the flag exists; `.repowise/` is gitignored except `decisions.yaml`; the index is rebuilt in CI with `repowise init --no-prose --no-editor-setup -y` (under ten seconds on the repos tried). The editor wiring (`.mcp.json`, hooks in `~/.claude/settings.json`) is never done by a skill; the agent uses the CLI.

## Decisions baked into the templates

- **Docstrings are not required** (`D1xx` ignored). Requiring them produces the signature-restating docstrings the prompt-comment gate exists to catch. When a docstring is present it must follow the Google convention.
- **Tests are exempt** from `S101` (assert), `PLR2004` (magic values), `D`, `ARG` (fixtures), `FBT`.
- **Strict from day one, changed lines only.** Pre-commit runs on staged files; CI runs pre-commit with `--from-ref origin/main --to-ref HEAD`, so old mess is tolerated and no new mess gets in. Whole-repo numbers come from the health step, not from the commit gate.
- **`filterwarnings = ["error"]`** in pytest. A deprecation is a failing test, so it gets fixed while it is one line.
- **mypy strict on `src/`, not on `tests/`.** With the Pydantic plugin when Pydantic is a dependency.
- **`uv run` for everything.** No activated virtualenvs in docs or scripts.
- **Repowise is a dev dependency, never a runtime one.** It is AGPL-3.0; the gate script imports it in CI and nowhere else. `DO_NOT_TRACK=1` is set in CI and listed in `.env.example`.

## Applying it (rules for `py-intake`)

1. Never change an existing file without showing the change and getting a yes for that file (the rule in `py-intake`). Merge missing keys into existing tables; leave existing values; show the merged result with the new parts marked; one file, one yes. A workflow file that already exists is never edited: ours goes beside it. A repo not on `uv` gets "adopt uv" as its first ticket, not a second packaging config.
2. Fill placeholders from the repo, never by guessing: `{{PROJECT}}` (repo name), `{{PACKAGE}}` (import name under `src/`), `{{PYTHON}}` (e.g. `3.12`), `{{PYTHON_NODOT}}` (`312`), `{{SHAPE}}`, `{{LAYERS}}`, `{{PORT}}` (per how-to), `{{NUMBER}}`, `{{TITLE}}`, `{{DATE}}` (per ADR).
3. Brownfield: propose the baseline as tickets, one file group at a time, each green before the next.
4. Prove each gate bites before finishing: make a violation on a scratch file, watch the gate fail, revert, watch it pass.
