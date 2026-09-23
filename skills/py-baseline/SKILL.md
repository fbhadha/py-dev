---
name: py-baseline
description: "The baseline every Python repo gets: layout, pyproject tool tables, pre-commit, CI, the Repowise change gate, agent docs; and the whole-repo health step. Use when setting up or checking a repo's tooling, checks or docs, or when asked where the repo is ugly. Merges, never overwrites."
---

# Python baseline

The skeleton every repo this agent touches ends up with, so a junior reader can pick up any of them the same way. `py-intake` applies it; anything else consults it.

## Files

| File | Purpose | Template |
|---|---|---|
| `pyproject.toml` `[tool.*]` tables | ruff, ruff-format, mypy strict, import-linter layers, pytest, coverage | `templates/pyproject-tools.toml` |
| `uv.lock`, `.python-version` | committed; CI installs with `uv sync --frozen` | created by `uv` |
| `.pre-commit-config.yaml` | ruff, ruff-format, mypy on changed files, import-linter, pylint too-many-lines, detect-secrets | `templates/pre-commit-config.yaml` |
| `.github/workflows/ci.yml` (or the GitLab equivalent) | pre-commit on the files the PR changed, the test-diff check, the whole test suite with coverage on the changed lines, then the Repowise change gate | `templates/ci.yml`, `templates/gitlab-ci.yml` |
| `scripts/repowise_gate.py` | the CI change gate over Repowise's Python API | `templates/repowise_gate.py` |
| `scripts/run_readme_blocks.py` | executes every ```bash ci``` block in `README.md` in CI | `templates/run_readme_blocks.py` |
| `scripts/check_test_diff.py` | fails when the `tests/` diff deletes a test, adds a skip or loses assertions, unless a commit message carries `test-override:` | `templates/check_test_diff.py` |
| `.secrets.baseline` | detect-secrets baseline, created by `uv run detect-secrets scan > .secrets.baseline` | created by `detect-secrets` |
| `.env.example` | every key the code reads, with a comment, no values | `templates/env.example` |
| `AGENTS.md` | the rules of work every agent follows (no ticket, no code; shape first; plans in tickets; one branch per ticket) and pointers, under 60 lines; the map is a link | `templates/AGENTS.md` |
| `docs/agents/repowise-map.md` | the architecture map, entry points and health line; written only by `repowise generate-claude-md --stdout` (`--output` overwrites its target whole) | Repowise |
| `CLAUDE.md` | one line: `@AGENTS.md` | `templates/CLAUDE.md` |
| `CONTEXT.md` | the glossary, Matt Pocock's format, created lazily | `templates/CONTEXT.md` |
| `docs/adr/` | decisions only, one file each, Nygard headings with `## Status` Accepted and `## Scope` paths; Repowise turns every file there into a decision, so nothing else lives there | created empty |
| `docs/agents/adr-template.md` | the ADR shape, for people and the agent | `templates/adr-template.md` |
| `scripts/adr_sync.py` | re-indexes and binds each accepted ADR to its Scope paths in Repowise | `templates/adr_sync.py` |
| `docs/agents/mode.md` | the mode line the skills read | `templates/mode.md` |
| `docs/howto/add-a-<shape>.md` | one per shape, mirrors an `example/` that compiles | `templates/howto-template.md` |
| `docs/research/<slug>.md` | one note per question answered from outside the repo, dated on its first line, one citation per claim; written by Matt Pocock's `research`, read into the grill that asked; a fact on a date, never a decision | created lazily |
| `prototypes/` | throwaway code that answers one design question, on a `prototype/<slug>` branch only, never on `main`; ruff (`force-exclude`) and bandit skip it; mypy, pylint and coverage never look there; detect-secrets still reads it, so a key never goes in a prototype either. A prototype costs no polish | created lazily |
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
| A change lands on `main` without the human's yes | in-session: the plugin's hook asks before a commit, merge or push that lands on `main`; on the server: branch protection requiring the CI jobs, set at intake with the user's yes | session; platform |
| New lines without a test | `diff-cover` at 90% on the lines the change added, in CI | CI |
| Layering | `import-linter` layers contract, whole program: CI and before review, `--hook-stage manual` locally; never in the commit hook, where it would block every commit on a brownfield repo | CI; review |
| Types | `mypy --strict` on the staged `src/` files (`follow_imports = silent`), the whole of `src/` in the health step | commit; health |
| A change made a touched file worse (new nesting, god class, I/O in a loop, duplication, swallowed exception) | `scripts/repowise_gate.py`: `ChangeReviewService.review()` on `origin/main..HEAD`, fails when `introduced_total > 0` | CI |
| Health score, ranking, what to refactor first, trend | `repowise health`, `--refactoring-targets`, `--trend` (its own history; nothing written to docs) | health |
| Duplication | `repowise health` (`dry_violation`) | health |
| Dead code | `repowise dead-code --safe-only` fails on unreachable files; unused exports are listed, never fail | health |
| Test with no assertion, mock-saturated test | `repowise health --format json`, advisory dimension (`assertion_free_test`, `mock_saturated_test`) | health; review |
| Docs that name paths, links or commands the tree no longer has | `repowise doc-drift` | health |
| Security | `bandit` (Repowise's 16-pattern scan is a floor, not a scanner) | health |
| Fake tests (pass on any mutation) | `mutmut`, on the module named; the score is reported in the health step and read at review, not stored | health |
| Weakened test (test deleted, skip added, assertions lost) | `scripts/check_test_diff.py` in CI and before review; an assertion loosened in place is the review's Craft axis on the `tests/` diff | CI; review |

## Where Repowise reads and writes (ADR 0005 in this repo)

Reads: the source tree, git history, `docs/adr/*.md` (Nygard headings; `## Status` Accepted makes it govern, `## Scope` paths are bound by `scripts/adr_sync.py`), `# WHY:` / `# DECISION:` comments, and `coverage.lcov` when ingested with `repowise coverage add coverage.lcov`. Writes: `.repowise/` (gitignored, rebuilt anywhere in seconds) and the managed section between `REPOWISE:START` and `REPOWISE:END` in `AGENTS.md`. Nothing else. No `docs/health/`, no orientation page, no decisions store in git: the ADR files and the code are the truth and the index is derived from them.

Repowise rules: every scripted call is `DO_NOT_TRACK=1 repowise <cmd> --no-editor-setup` where the flag exists; `.repowise/` is gitignored entirely (the ADR files carry the decisions); the index is rebuilt with `repowise init --no-prose --no-editor-setup --no-save-key -y`, in CI and at every refresh (under ten seconds on the repos tried); `repowise update` is never run because it writes `.claude/CLAUDE.md` and `.vscode/` files and ignores every flag and variable meant to stop it. The editor wiring (`.mcp.json`, hooks in `~/.claude/settings.json`) is never done by a skill; the agent uses the CLI.

## Decisions baked into the templates

- **Docstrings are not required** (`D1xx` ignored). Requiring them produces the signature-restating docstrings the prompt-comment gate exists to catch. When a docstring is present it must follow the Google convention.
- **Tests are exempt** from `S101` (assert), `PLR2004` (magic values), `D`, `ARG` (fixtures), `FBT`.
- **Strict from day one, changed lines only.** Pre-commit runs on staged files; CI runs pre-commit with `--from-ref origin/main --to-ref HEAD`, so old mess is tolerated and no new mess gets in. The one whole-program check, import-linter, runs in CI and before review, never in the commit hook: on a brownfield repo it is red until the layering ticket lands, and a hook that blocks every commit gets uninstalled, which is worse than a red CI job. Whole-repo numbers come from the health step, not from the commit gate.
- **`filterwarnings = ["error"]`** in pytest. A deprecation is a failing test, so it gets fixed while it is one line.
- **mypy strict on `src/`, not on `tests/`.** With the Pydantic plugin when Pydantic is a dependency.
- **`uv run` for everything.** No activated virtualenvs in docs or scripts.
- **Repowise is a dev dependency, never a runtime one.** It is AGPL-3.0; the gate script imports it in CI and nowhere else. `DO_NOT_TRACK=1` is set in CI and listed in `.env.example`.

## Health, on request

```bash
DO_NOT_TRACK=1 uv run repowise init --no-prose --no-editor-setup --no-save-key -y
uv run repowise health --refactoring-targets
uv run repowise dead-code --safe-only
uv run repowise doc-drift
uv run repowise decision health
```

Report, in this order: the worst files with one plain sentence each on the marker that makes them bad; files safe to delete; docs that name things that no longer exist; hotspots no ADR governs. Write no report file; `repowise health --trend` is the history. Mutation testing (`uv run mutmut run`) only on the module the user names. Then refresh the map: `uv run repowise generate-claude-md --stdout | sed -n '/REPOWISE:START/,/REPOWISE:END/p' > docs/agents/repowise-map.md`; Repowise is the only writer of that file, and it lands with the next merge. When the user wants the refactor, File `improve-codebase-architecture` on the worst file.

## Applying it (rules for `py-intake`)

1. Work on the intake branch; say which existing file you are about to change and why, then show the result (the branch rule in `py-intake`). Merge missing keys into existing tables; leave existing values; show the merged result with the new parts marked. The user's yes is the merge. A workflow file that already exists is never edited: ours goes beside it. A repo not on `uv` gets "adopt uv" as its first ticket, not a second packaging config.
2. Fill placeholders from the repo, never by guessing: `{{PROJECT}}` (repo name), `{{PACKAGE}}` (import name under `src/`), `{{PYTHON}}` (e.g. `3.12`), `{{PYTHON_NODOT}}` (`312`), `{{SHAPE}}`, `{{LAYERS}}`, `{{PORT}}` (per how-to), `{{NUMBER}}`, `{{TITLE}}`, `{{DATE}}` (per ADR).
3. Brownfield: propose the baseline as tickets, one file group at a time, each green before the next.
4. Prove each gate bites before finishing: make a violation on a scratch file, watch the gate fail, revert, watch it pass.
5. Never `pre-commit uninstall` and never `--no-verify` (both denied by the hook). A check that blocks a commit it should not is a placement defect: file it (persona section 9) and move the check to CI in that repo, with the user's yes.
