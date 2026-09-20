---
name: pack-data-engineering
description: "Knowledge pack for data engineering repos (dlt, pandas, polars, pyarrow, SQLAlchemy, DuckDB, dbt, pandera): shapes, canonical repo, extra checks, faults, tests. Reference only; selected by py-intake."
license: Apache-2.0
metadata:
  author: fbhadha
  version: 0.1.0
  tags: [python, data-engineering, pack, dlt, pandas, polars]
---

# Data engineering pack

A pack is a reference with a fixed shape (`packs/TEMPLATE.md`): what selects it, the shapes it knows, the canonical repo to cite, the extra checks it turns on, the faults it looks for, and how it tests. `py-design` carries the general rules; this file carries what changes when the objects moving through the code are tables.

## Selected when

Any of these is a dependency: `dlt`, `pandas`, `polars`, `pyarrow`, `sqlalchemy`, `duckdb`, `dbt-core`, `pandera`, `great-expectations`, `pyspark`, `prefect`, `dagster`, `airflow`.

## Shapes

| Shape | The how-to it gets | The seam |
|---|---|---|
| Source | `add-a-source.md`: one adapter that yields raw records for one external system, incremental state included | `Source` Protocol; in-memory source in tests |
| Transform | `add-a-transform.md`: one pure function from typed records to typed records, no I/O | the function itself, with a small literal frame |
| Sink | `add-a-sink.md`: one adapter that writes the normalised shape to one destination, idempotently | `Sink` Protocol; in-memory sink in tests |
| Pipeline | `add-a-pipeline.md`: the composition root that wires sources, the normaliser and sinks for one dataset | the entrypoint, with in-memory adapters |

Every source produces the same normalised record; every sink consumes it; normalisation happens once, in the domain, never inside a source or a sink. When a new source needs a change to the sink, the shape is wrong.

## Canonical repo

`dlt-hub/dlt`. Cite `dlt/extract/` for sources and incremental state, `dlt/normalize/` for the one place raw items become a schema, `dlt/load/` for destination-agnostic loading, `dlt/common/destination/reference.py` for the destination contract. `py-design/references/canonical-examples.md` has the sentences to use.

## Extra checks this pack turns on

Added to the baseline `pyproject.toml` by `py-intake` when the pack is selected:

- ruff `PD` (pandas-vet: `.values`, `inplace=True`, chained `.iloc`, `pd.merge` as a function), `NPY`, `S608` stays on (string-built SQL).
- import-linter: `pandas`, `polars`, `pyarrow`, `sqlalchemy`, `duckdb` are forbidden imports for `{{PACKAGE}}.domain`; the domain works on records, not frames.
- A notebook (`*.ipynb`) anywhere under `src/` fails pre-commit (`check-added-large-files` plus a `forbid-notebooks-in-src` local hook: `entry: bash -c '! git ls-files src | grep -q ipynb'`).
- `pandera` or a Pydantic model at every boundary a frame crosses; `pyproject` gets `pandera` in the dev group when frames are present.

## Faults this pack looks for (beyond the catalogue)

| Fault | Tell | Fix |
|---|---|---|
| The frame that crosses layers | A `DataFrame` parameter or return in `application/` or `domain/` | Records (frozen dataclass or Pydantic) inside; frames only inside an adapter or a transform's private body |
| Schema by inference | `read_csv` without `dtype`, `to_sql` with no explicit types, `SELECT *` | Declared schema at the edge (`pandera`, `pyarrow.schema`, explicit `dtype`); named columns |
| The non-idempotent load | An append with no key, a `TRUNCATE` inside a loop, a load that cannot be re-run after a crash | Merge on a declared key, or a staging table swapped at the end; the sink's contract says which |
| Incremental state in the wrong place | A "last run" timestamp in a global, a file in the repo, or a column the sink owns | State owned by the source adapter and persisted by the pipeline's state store (dlt's `incremental` is the model) |
| The notebook as source of truth | Logic that exists only in `.ipynb` | A module under `src/` with a test; the notebook imports it |
| Secrets in the pipeline | Connection strings in code, `.env` committed, credentials in a notebook cell | `pydantic-settings`; `.env.example`; `detect-secrets` catches the rest |
| Row-by-row I/O | A query or a write inside a `for` over rows | Batch; Repowise `io_in_loop` finds it, the fix is a set operation |
| The silent cast | `errors="coerce"`, `pd.to_numeric` swallowing bad rows, `try/except` around a parse | Reject or quarantine bad rows explicitly, with a count in the run's output |

## Tests

- Unit: transforms with a five-row literal frame or list of records whose expected output is written by hand from the spec; never computed with the code's own function.
- Integration: sources against a recorded response or a local file; sinks against DuckDB or SQLite in a temp dir, asserting row counts and a checksum, run twice to prove idempotence.
- Never a unit test that reaches a warehouse or an API. Those are integration, and they are marked.
