---
name: pack-data-engineering
description: "Knowledge pack for data-engineering repos (dlt, pandas, polars, pyarrow, SQLAlchemy, DuckDB, dbt, pandera, Spark, Airflow, Dagster, Prefect): the four shapes with how-tos and a tested example package, the design rules for time, money, re-runs, incremental state, backfills, schemas and data quality, extra checks, faults, tests. Reference only; selected by py-intake."
---

# Data engineering pack

A pack is a reference with a fixed shape (`packs/TEMPLATE.md` in this plugin): what selects it, the shapes it knows, the canonical repo to cite, the extra checks it turns on, the faults it looks for, and how it tests. `py-design` carries the general rules; this file carries what changes when the things moving through the code are tables. Open it while shaping, planning, building or reviewing in a repo that lists it under `## Packs` in `AGENTS.md`.

## Selected when

Any of these is a dependency: `dlt`, `pandas`, `polars`, `pyarrow`, `sqlalchemy`, `duckdb`, `dbt-core`, `pandera`, `great-expectations`, `pyspark`, `prefect`, `dagster`, `airflow`.

## Shapes

| Shape | Its how-to (shipped in `references/howto/`) | The seam its tests drive |
|---|---|---|
| Source | `add-a-source.md`: one adapter that reads one outside system and yields parsed records, incremental from a cursor | the `Source` port, against a recorded sample |
| Transform | `add-a-transform.md`: one pure function in the domain, records in, records out | the function, with a handful of literal records |
| Sink | `add-a-sink.md`: one adapter that upserts records into one destination, newer update wins | the sink contract suite, which the in-memory sink also passes |
| Pipeline | `add-a-pipeline.md`: the application function for one load and the entrypoint a scheduler calls | the run with in-memory adapters; the entrypoint end to end, twice |

Parsing happens once, in the source adapter that received the data (`py-design` rule 2). Business rules (what a valid record is, which update wins, conversions) happen once, in the domain. A sink writes what it is given. When a new source needs a change to a sink, the shape is wrong.

## The worked example

`references/example/orders/` is the four shapes in one small package: a CSV export loaded incrementally into SQLite. A frozen `Order` with `Decimal` money and UTC times; a source that parses each row once and turns every bad row into a counted `Rejected`; a pure latest-update-wins transform; a sink that upserts on the key and never lets an older update replace a newer one; a JSON cursor store written atomically; a run that moves the cursor only after the write; a command-line entrypoint that exits 0, 1 (rows rejected) or 2 (could not run). Its 44 tests under `references/example/tests/` include one contract suite per port that the in-memory and the real adapters both pass. This plugin's CI runs it under the baseline's pytest, ruff and `mypy --strict` settings (`scripts/check_pack_examples.py`).

`py-intake` step 8 copies it into a repo that selects this pack: the package to `src/{{PACKAGE}}/examples/orders/` and its tests to `tests/unit/examples/` and `tests/integration/examples/`, with the placeholder package name `yourpkg` replaced by the repo's; the four how-tos to `docs/howto/` with `{{PACKAGE}}` filled. From then on the how-tos describe the repo's own shapes.

## Design rules

1. **Time.** Timezone-aware and in UTC everywhere inside the code; a time with no offset is rejected at the edge, never assumed to be local. When both matter, when something happened (event time) and when it was loaded (load time) are separate fields. Cursors follow the source's own update time, never the load time.
2. **Money and exact quantities.** `Decimal` in Python, `NUMERIC` or `DECIMAL` in SQL; never a float, from the string the source sent.
3. **Every load can run twice.** Upsert on a declared key with the newer update winning, or write to a staging table and swap it in. The cursor moves only after the write commits: rows arrive at least once and are stored once.
4. **Incremental state belongs to the cursor store**, one name per load. Not a global, not a file in the repo, not a column the sink owns.
5. **A backfill is a re-run from an earlier cursor**, safe because of rule 3. Partitioned data is reprocessed one partition at a time, and the overwrite is scoped to that partition.
6. **Schemas are declared, never inferred**: explicit dtypes, a pyarrow schema, a pandera model, SQL DDL. A schema change is additive first (expand, migrate, contract); a breaking change to a table other people read is a one-way door and gets an ADR.
7. **Every run says what it did**: rows read, written and rejected, and the new cursor, in one line. Rejected rows are kept (a quarantine table, or the count with the reasons), never dropped. Anything scheduled also gets freshness and volume checks on the destination.
8. **Transforms are deterministic**: the output depends only on the input. No clock (time is passed in), no randomness, a stated output order.
9. **Personal data stays out of logs and errors.** Log ids, line numbers and counts, never row contents.
10. **Frames stay at the edge.** A DataFrame lives inside an adapter or inside a transform's private body; the domain and the application work on records, and the import contract below refuses the rest.

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
| The load that cannot run twice | An append with no key, a `TRUNCATE` inside a loop, a load that cannot be re-run after a crash | Upsert on a declared key, or a staging table swapped at the end; the sink's contract says which |
| Incremental state in the wrong place | A "last run" timestamp in a global, a file in the repo, or a column the sink owns; a cursor saved before the write | State owned by the cursor store, saved after the write commits (dlt's `incremental` is the model) |
| The notebook as source of truth | Logic that exists only in `.ipynb` | A module under `src/` with a test; the notebook imports it |
| Secrets in the pipeline | Connection strings in code, `.env` committed, credentials in a notebook cell | `pydantic-settings`; `.env.example`; `detect-secrets` catches the rest |
| Row-by-row I/O | A query or a write inside a `for` over rows | Batch; Repowise `io_in_loop` finds it, the fix is a set operation |
| The silent cast | `errors="coerce"`, `pd.to_numeric` swallowing bad rows, `try/except` around a parse | Reject or quarantine bad rows explicitly, with a count in the run's output |
| The naive timestamp | `datetime.now()` or `utcnow()` with no zone, a `TIMESTAMP` column without time zone, a time string parsed with no offset | Aware UTC inside; reject unlabelled times at the edge |
| Float money | `float(amount)`, a `FLOAT` or `DOUBLE` column for currency | `Decimal` in Python, `NUMERIC` in SQL, parsed from the source's string |
| The fan-out join | A join on a key that is not unique multiplies rows, then `DISTINCT` or `drop_duplicates` hides it | Check the key is unique before joining (pandas `merge(validate="many_to_one")`); compare row counts before and after |
| NULL surprises in SQL | `NOT IN (subquery)` where the subquery can return NULL (no rows come back); `=` expected to match NULL | `NOT EXISTS`; the dialect's null-safe comparison; a test row with a NULL key |
| The non-deterministic transform | The clock, randomness, or set and dict order deciding the output | Time passed in; output sorted by a stated key |
| The unscoped overwrite | `if_exists="replace"` or an overwrite of a whole table when one partition was recomputed | Overwrite scoped to the partition, or upsert |
| The whole file in memory | `read_csv` of a multi-gigabyte file, `fetchall()` on a large query | Stream in chunks (`chunksize`, pyarrow `iter_batches`, a server-side cursor) or push the work into the database or DuckDB |
| Python loops over a frame | `iterrows`, `apply(axis=1)` with a Python function on a large frame | A vectorised expression (pandas, polars) or SQL |

## Tests

- **Unit**: transforms and the run, on five or six literal records with in-memory adapters; the expected output written by hand from the spec, never computed with the code's own function.
- **Contract**: one suite per port (source, sink, cursor store); every adapter runs it, the in-memory ones included (`py-design/references/boundaries.md`; the example's `test_orders_sinks.py` and `test_orders_cursors.py`).
- **Integration**: sources against a recorded, scrubbed sample under `tests/fixtures/`; sinks against DuckDB or SQLite in `tmp_path`, asserting the rows and running twice to prove the second run writes nothing; the entrypoint end to end, twice.
- **Edge cases**: the ten design rules above are categories in the edge-case list (`py-design`'s `references/edge-cases.md`): a load run twice, a backfill from an earlier cursor, a time with no offset, a tie on the update time, a schema change, an empty extract, a row with fewer fields than the header. A transform gets a property test (one record per key, the stated output order, a second pass changes nothing); the example's `test_orders_transforms.py` shows one.
- Never a unit test that reaches a warehouse, an API or a cloud bucket. Those are integration tests against a local substitute, and they are marked.

## Not covered in depth yet

Orchestrators (Airflow, Dagster, Prefect), dbt and Spark select this pack, and every rule above holds for them, plus one: the orchestrator's file (a DAG, an asset, a flow) is an entrypoint only, calling application code that is tested without the orchestrator. Their own conventions (dbt's model layers and tests, Spark partitioning and skew, sensors and retries) are not written here yet. When a repo uses one, say so once at intake, file a `later` ticket titled `pack-data-engineering: <tool>`, and never improvise the tool's conventions.
