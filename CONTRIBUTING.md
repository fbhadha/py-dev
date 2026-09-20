# Contributing

This repository is the `python-dev` agent: one Claude Code plugin, also readable by GitHub Copilot and OpenAI Codex through the Agent Skills format. Its rules are strict, because a target repo depends on them.

## Rules

- **One persona file.** `agents/python-dev.md` is the only copy; `py-intake` renders the Copilot and Codex forms in the target repo. Keep it about a page: identity, voice, rules and pointers. Knowledge goes in skills.
- **Skills are model-invoked** and carry `agents/openai.yaml`. `scripts/check_invocation_sync.py` fails when the two switches disagree.
- **Call upstream skills by name, never copy them.** Add the name to `upstream.json` with the invocation you assume; `scripts/check_upstream_skills.py` verifies it against the pinned commit in CI. Bump the pin deliberately, in its own commit, after reading the upstream changelog.
- **One read path and one write path per kind of knowledge** (ADR 0005). Anything derived from the code comes from Repowise; do not add a second store, report file or orientation page.
- **No custom gates.** A check goes in as an established tool's rule in `skills/py-baseline/templates/pyproject-tools.toml`; the only scripts we maintain are the change gate, the ADR binder and the README block runner, and they must pass the baseline's own ruff rules.
- **Verify before you write.** Every claim about a tool or an upstream skill is checked by running it; `docs/research/` records what was verified and when.
- **A knowledge pack** is `skills/pack-<domain>/` in the shape of `packs/TEMPLATE.md`, reference only.
- **Decisions are ADRs** in `docs/adr/`; the words are in `CONTEXT.md`. Neither is a scratch pad.

## What a skill looks like

```
skills/<name>/
├── SKILL.md            # required: YAML frontmatter + a procedure
├── agents/openai.yaml  # required: Codex display name and invocation policy
├── references/         # optional: deeper docs loaded on demand
└── templates/          # optional: files py-intake copies into a target repo
```

`SKILL.md` frontmatter follows the [Agent Skills open standard](https://agentskills.io) and `schema/skill.schema.json`: `name` equals the folder name, is lowercase letters/numbers/hyphens, ≤64 chars and contains neither `anthropic` nor `claude`; `description` says what and when in ≤1024 chars; the body is a procedure under ~500 lines, with depth pushed into `references/`.

## Before you open a PR

```
pip install pyyaml jsonschema
python scripts/validate_skills.py
python scripts/check_invocation_sync.py
python scripts/check_upstream_skills.py      # if upstream.json or a skill name we call changed
claude plugin validate --strict .
```

Sign your commits (DCO, below) and complete the PR checklist.

## Before a release

The four checks above, then a `claude --agent python-dev --plugin-dir . -p` smoke test in a real repo, then bump `version` in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` and add a `CHANGELOG.md` entry. Claude Code users get a new version only when `version` is bumped.

## Security

Hook scripts and baseline templates run on users' machines. Nothing here may exfiltrate data, fetch-and-execute remote code, or modify a system unexpectedly. Reviewers read every script; the `security-scan` CI job flags risky patterns for manual review. Found a vulnerability? See [SECURITY.md](SECURITY.md).

## Developer Certificate of Origin (DCO)

We use the [DCO](https://developercertificate.org/) instead of a CLA. Sign off each commit to certify you have the right to submit it:

```
git commit -s -m "py-baseline: add the import-linter contract template"
```

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). By participating you agree to uphold it.
