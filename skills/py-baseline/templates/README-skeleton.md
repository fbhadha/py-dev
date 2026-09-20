# {{PROJECT}}

One paragraph: what this does, for whom, and what it reads and writes.

## Run

Blocks fenced as ```bash ci``` are executed in CI by `scripts/run_readme_blocks.py`, so these commands cannot rot.

```bash ci
uv sync
uv run python -m {{PACKAGE}} --help
```

## Test

```bash ci
uv run pytest -m "not eval"
```

## Where to start reading

1. `CONTEXT.md` for the words.
2. `docs/architecture.md` for the layers.
3. `src/{{PACKAGE}}/entrypoints/` for where a run begins, then follow the imports down.
4. `docs/howto/` before adding anything.

## Checks

`uv run pre-commit install` once. Every commit then runs ruff, mypy, import-linter and the size gate on the files you changed. `uv run repowise health` shows the whole-repo picture.
