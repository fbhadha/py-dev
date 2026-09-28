# Contributing to python-dev

Knowledge packs are the part of this plugin built to be written by other people. Pull requests for packs are welcome. Contributed skills come later ([#76](https://github.com/fbhadha/py-dev/issues/76)).

## Questions and pull requests

- **A question or a bug**: open a [GitHub issue](https://github.com/fbhadha/py-dev/issues).
- **A knowledge pack**: open a pull request. It must meet the checklist below.
- **Anything else**: open an issue first. Every change here starts as a ticket.

## Contribute a knowledge pack

A knowledge pack teaches the agent one Python ecosystem: its shapes, its design rules, its faults, its checks. It is reference material only. It changes what the agent knows, never how the agent works.

1. Copy the block in [packs/TEMPLATE.md](packs/TEMPLATE.md) to `skills/pack-<domain>/SKILL.md`.
2. Fill every section.
3. Add the path to `skills` in `.claude-plugin/plugin.json`.
4. Add the pack, and the dependencies that select it, to the row `Packs` in [skills/py-intake/SKILL.md](skills/py-intake/SKILL.md), step 1. Without this step intake never selects the pack ([#75](https://github.com/fbhadha/py-dev/issues/75)).
5. Run `python scripts/check_plugin.py`.

Two packs to read first: [skills/pack-adk](skills/pack-adk/SKILL.md) and [skills/pack-data-engineering](skills/pack-data-engineering/SKILL.md).

## What a pack must meet

- [ ] Every section of the template is filled.
- [ ] No procedures. Steps belong in a skill with a verb in its name.
- [ ] No copy of another skill's content. Cite it.
- [ ] Nothing a linter enforces. Turn the linter on in "Extra checks" instead.
- [ ] Every claim about a library is checked against its current docs, with the version noted.
- [ ] `scripts/check_plugin.py` is green.
- [ ] A pack that ships an example package: `scripts/check_pack_examples.py` is green.

## Set up and check

Blocks fenced as ```bash ci``` are executed in CI by `scripts/run_readme_blocks.py`, so these commands cannot rot.

```bash ci
uv sync
uv run python scripts/render_agents.py    # after editing agents/*.md: regenerate the per-harness copies
uv run python scripts/check_plugin.py     # frontmatter, manifests in step, the skills list, rendered copies current
uv run pytest -m "not eval"                # every hook decision and baseline script, against a scratch git repo
uv run python scripts/check_template_scripts.py   # every baseline template passes the baseline's own ruff
```

The rest of what `validate.yml` runs on every pull request needs the network or a tool CI does not have, so it is listed here and run there:

```
uv run python scripts/check_pack_examples.py    # the pack example, under the baseline's checks
uv run python scripts/check_upstream_skills.py  # every upstream skill exists at its pin with the invocation we assume
uv run python scripts/check_template_deps.py    # the baseline's dev group resolves with Repowise in it
claude plugin validate --strict .
```

This repo carries the same baseline it installs (`uv run pre-commit install` once; `uv run repowise health` for the whole-repo picture), and a new check follows [docs/howto/add-a-plugin-check.md](docs/howto/add-a-plugin-check.md).

## Rules

- `agents/python-dev.md` is the only hand-written persona. It stays under 14,000 characters, and every skill is reachable from it. CI enforces both.
- Every step list is a skill the persona's table names. Every other copy is generated, and CI fails when one is stale.
- Call upstream skills by name, never copy them. Add the name to `upstream.json`, and bump a pin in its own commit after reading the upstream changelog.
- One read path and one write path per kind of knowledge (ADR 0005). Anything derived from the code comes from Repowise, by CLI.
- No custom code-quality gates. A check is an established tool's rule in `skills/py-baseline/templates/pyproject-tools.toml`.
- The six scripts the baseline copies into a repo (change gate, ADR binder, README runner, test-diff check, literal check, eval-report check) are process, not lint.
- Verify before you write. `docs/research/` records what was checked and when.
- A knowledge pack is `skills/pack-<domain>/` in the shape of `packs/TEMPLATE.md`, reference only.

## Before a release

1. Run the commands above.
2. Run [the smoke test](docs/smoke-test.md) with a real model on each harness someone uses.
3. Set the version in every manifest and in the persona's status line.
4. Add a `CHANGELOG.md` entry that records the smoke test.

## Why things are the way they are

- [docs/how-python-dev-works.md](docs/how-python-dev-works.md): the long explainer.
- [docs/design/python-dev-agent.md](docs/design/python-dev-agent.md): the design and every decision.
- [docs/adr/](docs/adr/): the decisions that were hard to reverse.
- [docs/research/](docs/research/): what was verified.
- [CONTEXT.md](CONTEXT.md): the words.
